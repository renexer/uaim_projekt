from __future__ import annotations

import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from app.extensions import db
from app.models import EmailNotification


class NotificationService:
    def schedule_booking_email(self, appointment):
        self._create_notification(
            appointment_id=appointment.id,
            recipient_email=appointment.patient.email,
            notification_type="APPOINTMENT_BOOKED",
            scheduled_at=datetime.utcnow(),
        )
        self._create_notification(
            appointment_id=appointment.id,
            recipient_email=appointment.patient.email,
            notification_type="APPOINTMENT_REMINDER_24H",
            scheduled_at=appointment.start_at - timedelta(hours=24),
        )
        db.session.commit()

    def schedule_cancellation_email(self, appointment):
        self._create_notification(
            appointment_id=appointment.id,
            recipient_email=appointment.patient.email,
            notification_type="APPOINTMENT_CANCELLED",
            scheduled_at=datetime.utcnow(),
        )
        db.session.commit()

    def send_due_notifications(self):
        now = datetime.utcnow()
        due = (
            EmailNotification.query.filter(
                EmailNotification.status == "PENDING",
                EmailNotification.scheduled_at <= now,
            )
            .order_by(EmailNotification.scheduled_at.asc())
            .all()
        )

        for notification in due:
            try:
                self._send(notification)
                notification.status = "SENT"
                notification.sent_at = datetime.utcnow()
                notification.error_message = None
            except Exception as exc:
                notification.status = "FAILED"
                notification.error_message = str(exc)

        db.session.commit()
        return due

    def _create_notification(self, appointment_id, recipient_email, notification_type, scheduled_at):
        db.session.add(
            EmailNotification(
                appointment_id=appointment_id,
                recipient_email=recipient_email,
                type=notification_type,
                status="PENDING",
                scheduled_at=scheduled_at,
            )
        )

    def _send(self, notification):
        backend = os.getenv("MAIL_BACKEND", "console")

        if backend == "console":
            print(
                f"[MAIL] to={notification.recipient_email} type={notification.type} scheduled_at={notification.scheduled_at}"
            )
            return

        if backend != "smtp":
            raise RuntimeError(f"Nieznany MAIL_BACKEND: {backend}")

        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        mail_sender = os.getenv("MAIL_SENDER", smtp_username)

        subject, body = self._build_message(notification)

        message = MIMEText(body, "plain", "utf-8")
        message["Subject"] = subject
        message["From"] = mail_sender
        message["To"] = notification.recipient_email

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_use_tls:
                server.starttls()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.sendmail(mail_sender, [notification.recipient_email], message.as_string())

    def _build_message(self, notification):
        if notification.type == "APPOINTMENT_BOOKED":
            return (
                "Potwierdzenie rezerwacji wizyty",
                "Twoja wizyta została poprawnie zarezerwowana.",
            )
        if notification.type == "APPOINTMENT_CANCELLED":
            return (
                "Odwołanie wizyty",
                "Twoja wizyta została odwołana.",
            )
        if notification.type == "APPOINTMENT_REMINDER_24H":
            return (
                "Przypomnienie o wizycie",
                "Przypominamy o wizycie zaplanowanej za mniej niż 24 godziny.",
            )
        return ("Powiadomienie", "Nowe powiadomienie z systemu.")