from __future__ import annotations

import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from flask import current_app

from app.extensions import db
from app.models import EmailNotification
from app.utils.enums import EmailNotificationStatus, EmailNotificationType


class NotificationService:
    """Tworzy i wysyła powiadomienia o wizytach.

    W trybie demonstracyjnym (`MAIL_BACKEND=console`) wiadomości są widoczne w
    logach aplikacji. Po ustawieniu `MAIL_BACKEND=smtp` serwis korzysta ze
    zmiennych `MAIL_SMTP_*` i wysyła faktyczną wiadomość e-mail.
    """

    def schedule_booking_email(self, appointment):
        """Dodaje wiadomość potwierdzającą rezerwację i przypomnienie 24h przed wizytą."""
        self._create_notification(
            appointment=appointment,
            recipient_email=appointment.patient.email,
            notification_type=EmailNotificationType.APPOINTMENT_BOOKED.value,
            scheduled_at=datetime.now(timezone.utc),
        )
        self._create_notification(
            appointment=appointment,
            recipient_email=appointment.patient.email,
            notification_type=EmailNotificationType.APPOINTMENT_REMINDER_24H.value,
            scheduled_at=appointment.start_at - timedelta(hours=24),
        )
        db.session.commit()

    def schedule_cancellation_email(self, appointment):
        """Dodaje powiadomienie o anulowaniu wizyty."""
        self._create_notification(
            appointment=appointment,
            recipient_email=appointment.patient.email,
            notification_type=EmailNotificationType.APPOINTMENT_CANCELLED.value,
            scheduled_at=datetime.now(timezone.utc),
        )
        db.session.commit()

    def send_due_notifications(self):
        """Wysyła wszystkie zaległe powiadomienia i aktualizuje ich status w bazie."""
        due = (
            EmailNotification.query.filter(
                EmailNotification.status == EmailNotificationStatus.PENDING.value,
                EmailNotification.scheduled_at <= datetime.now(timezone.utc),
            )
            .order_by(EmailNotification.scheduled_at.asc())
            .all()
        )
        for item in due:
            try:
                self._send(item)
                item.status = EmailNotificationStatus.SENT.value
                item.sent_at = datetime.now(timezone.utc)
                item.error_message = None
            except Exception as exc:  # pragma: no cover
                item.status = EmailNotificationStatus.FAILED.value
                item.error_message = str(exc)
        db.session.commit()
        return due

    def _create_notification(self, appointment, recipient_email, notification_type, scheduled_at):
        db.session.add(
            EmailNotification(
                appointment_id=appointment.id,
                recipient_email=recipient_email,
                type=notification_type,
                status=EmailNotificationStatus.PENDING.value,
                scheduled_at=scheduled_at,
            )
        )

    @staticmethod
    def _send(notification: EmailNotification):
        backend = current_app.config.get("MAIL_BACKEND", "console")
        if backend == "console":
            print(
                f"[MAIL] to={notification.recipient_email} "
                f"type={notification.type} scheduled_at={notification.scheduled_at.isoformat()}"
            )
            return
        if backend == "smtp":  # pragma: no cover - wymaga zewnętrznego serwera SMTP
            NotificationService._send_smtp(notification)
            return
        raise NotImplementedError(f"Nieobsługiwany MAIL_BACKEND={backend!r}.")

    @staticmethod
    def _send_smtp(notification: EmailNotification):
        host = current_app.config["MAIL_SMTP_HOST"]
        port = current_app.config["MAIL_SMTP_PORT"]
        username = current_app.config["MAIL_SMTP_USERNAME"]
        password = current_app.config["MAIL_SMTP_PASSWORD"]
        sender = current_app.config["MAIL_SENDER"]

        if not host:
            raise RuntimeError("Brak konfiguracji MAIL_SMTP_HOST.")

        message = EmailMessage()
        message["From"] = sender
        message["To"] = notification.recipient_email
        message["Subject"] = NotificationService._subject(notification.type)
        message.set_content(NotificationService._body(notification))

        with smtplib.SMTP(host, port, timeout=15) as smtp:
            if current_app.config["MAIL_SMTP_USE_TLS"]:
                smtp.starttls()
            if username:
                smtp.login(username, password)
            smtp.send_message(message)

    @staticmethod
    def _subject(notification_type: str) -> str:
        mapping = {
            EmailNotificationType.APPOINTMENT_BOOKED.value: "Potwierdzenie rezerwacji wizyty",
            EmailNotificationType.APPOINTMENT_CANCELLED.value: "Anulowanie wizyty",
            EmailNotificationType.APPOINTMENT_REMINDER_24H.value: "Przypomnienie o wizycie",
        }
        return mapping.get(notification_type, "Powiadomienie z gabinetu")

    @staticmethod
    def _body(notification: EmailNotification) -> str:
        return (
            "To jest automatyczne powiadomienie z aplikacji gabinetu psychologiczno-terapeutycznego.\n"
            f"Typ powiadomienia: {notification.type}\n"
            f"Identyfikator wizyty: {notification.appointment_id}\n"
        )
