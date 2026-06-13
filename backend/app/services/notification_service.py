from __future__ import annotations

import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from html import escape
from zoneinfo import ZoneInfo

from app.extensions import db
from app.models import Appointment, EmailNotification


# Warstwa logiki biznesowej odpowiedzialna za kolejkowanie i wysyłanie powiadomień e-mail.
class NotificationService:
    # Kolejkuje e-mail potwierdzający rezerwację oraz przypomnienie 24h przed wizytą.
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

    # Kolejkuje e-mail o anulowaniu wizyty i usuwa oczekujące przypomnienia.
    def schedule_cancellation_email(self, appointment):
        self.cancel_pending_reminders(appointment.id)

        self._create_notification(
            appointment_id=appointment.id,
            recipient_email=appointment.patient.email,
            notification_type="APPOINTMENT_CANCELLED",
            scheduled_at=datetime.utcnow(),
        )
        db.session.commit()

    # Oznacza oczekujące przypomnienia jako pominięte po anulowaniu wizyty.
    def cancel_pending_reminders(self, appointment_id):
        EmailNotification.query.filter(
            EmailNotification.appointment_id == appointment_id,
            EmailNotification.status == "PENDING",
            EmailNotification.type == "APPOINTMENT_REMINDER_24H",
        ).update(
            {
                "status": "SKIPPED",
                "error_message": "Wizyta została anulowana przed wysłaniem przypomnienia.",
            },
            synchronize_session=False,
        )

    # Wysyła wszystkie zaległe powiadomienia, których czas wysyłki już nadszedł.
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

    # Metoda pomocnicza dodająca rekord powiadomienia do kolejki w bazie danych.
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

    # Wysyła pojedyncze powiadomienie przez skonfigurowany backend pocztowy.
    def _send(self, notification):
        backend = os.getenv("MAIL_BACKEND", "console")

        subject, plain_body, html_body = self._build_message(notification)

        if backend == "console":
            print(
                f"[MAIL] to={notification.recipient_email} "
                f"type={notification.type} scheduled_at={notification.scheduled_at}\n"
                f"subject={subject}\n{plain_body}"
            )
            return

        if backend != "smtp":
            raise RuntimeError(f"Nieznany MAIL_BACKEND: {backend}")

        smtp_host = os.getenv("MAIL_SMTP_HOST")
        smtp_port = int(os.getenv("MAIL_SMTP_PORT", "587"))
        smtp_username = os.getenv("MAIL_SMTP_USERNAME")
        smtp_password = os.getenv("MAIL_SMTP_PASSWORD")
        smtp_use_tls = os.getenv("MAIL_SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}

        mail_sender = os.getenv("MAIL_SENDER", smtp_username)
        mail_from_name = os.getenv("MAIL_FROM_NAME", "Spokojna Przystań")

        if not smtp_host:
            raise RuntimeError("Brak MAIL_SMTP_HOST.")
        if not smtp_username:
            raise RuntimeError("Brak MAIL_SMTP_USERNAME.")
        if not smtp_password:
            raise RuntimeError("Brak MAIL_SMTP_PASSWORD.")
        if not mail_sender:
            raise RuntimeError("Brak MAIL_SENDER.")

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = formataddr((mail_from_name, mail_sender))
        message["To"] = notification.recipient_email

        message.attach(MIMEText(plain_body, "plain", "utf-8"))
        message.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            if smtp_use_tls:
                server.starttls()
                server.ehlo()
            server.login(smtp_username, smtp_password)
            server.sendmail(mail_sender, [notification.recipient_email], message.as_string())

    # Dobiera temat i treść wiadomości do typu powiadomienia.
    def _build_message(self, notification):
        appointment = None
        if notification.appointment_id:
            appointment = Appointment.query.get(notification.appointment_id)

        if notification.type == "APPOINTMENT_BOOKED":
            subject = "Potwierdzenie rezerwacji wizyty"
            title = "Twoja wizyta jest zarezerwowana"
            intro = "Dziękujemy za rezerwację. Poniżej znajdziesz szczegóły wizyty."
            badge = "Rezerwacja potwierdzona"
            badge_color = "#246b6b"

        elif notification.type == "APPOINTMENT_CANCELLED":
            subject = "Odwołanie wizyty"
            title = "Wizyta została odwołana"
            intro = "Twoja wizyta została odwołana. Szczegóły znajdziesz poniżej."
            badge = "Wizyta odwołana"
            badge_color = "#b93737"

        elif notification.type == "APPOINTMENT_REMINDER_24H":
            subject = "Przypomnienie o wizycie"
            title = "Przypomnienie o jutrzejszej wizycie"
            intro = "Przypominamy o nadchodzącej wizycie zaplanowanej za mniej niż 24 godziny."
            badge = "Przypomnienie"
            badge_color = "#d98e5f"

        else:
            subject = "Powiadomienie"
            title = "Nowe powiadomienie"
            intro = "Masz nowe powiadomienie z systemu Spokojna Przystań."
            badge = "Powiadomienie"
            badge_color = "#246b6b"

        plain_body = self._build_plain_body(title, intro, appointment)
        html_body = self._build_html_body(title, intro, badge, badge_color, appointment)

        return subject, plain_body, html_body

    # Buduje tekstową wersję wiadomości jako fallback dla klientów bez HTML.
    def _build_plain_body(self, title, intro, appointment):
        lines = [
            "Spokojna Przystań",
            "",
            title,
            "",
            intro,
            "",
        ]

        if appointment:
            lines.extend(
                [
                    f"Usługa: {appointment.service_name_snapshot}",
                    f"Terapeuta: {appointment.therapist_name_snapshot}",
                    f"Termin: {self._format_datetime(appointment.start_at)}",
                    f"Czas trwania: {appointment.duration_minutes_snapshot} min",
                    f"Cena: {appointment.price_snapshot} PLN",
                    "",
                ]
            )

            if appointment.cancellation_reason:
                lines.extend(
                    [
                        f"Powód odwołania: {appointment.cancellation_reason}",
                        "",
                    ]
                )

        lines.extend(
            [
                "Panel pacjenta:",
                f"{self._public_url()}/appointments",
                "",
                "To jest wiadomość automatyczna. Prosimy na nią nie odpowiadać.",
            ]
        )

        return "\n".join(lines)

    # Buduje graficzną wersję wiadomości HTML spójną ze stylem aplikacji.
    def _build_html_body(self, title, intro, badge, badge_color, appointment):
        details_html = ""

        if appointment:
            rows = [
                ("Usługa", appointment.service_name_snapshot),
                ("Terapeuta", appointment.therapist_name_snapshot),
                ("Termin", self._format_datetime(appointment.start_at)),
                ("Czas trwania", f"{appointment.duration_minutes_snapshot} min"),
                ("Cena", f"{appointment.price_snapshot} PLN"),
            ]

            if appointment.cancellation_reason:
                rows.append(("Powód odwołania", appointment.cancellation_reason))

            details_rows = "".join(self._detail_row(label, value) for label, value in rows)

            details_html = f"""
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                       style="margin-top: 22px; border-collapse: collapse; border: 1px solid #d7e0e4; border-radius: 18px; overflow: hidden;">
                    {details_rows}
                </table>
            """

        appointments_url = f"{self._public_url()}/appointments"

        return f"""<!doctype html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
</head>
<body style="margin:0; padding:0; background:#f6f8fb; color:#1d2939; font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f6f8fb; padding:32px 12px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                       style="max-width:640px; background:#ffffff; border:1px solid #d7e0e4; border-radius:24px; overflow:hidden; box-shadow:0 18px 45px rgba(33,59,78,0.09);">
                    <tr>
                        <td style="background:#246b6b; padding:28px 30px;">
                            <div style="font-size:14px; letter-spacing:0.12em; text-transform:uppercase; font-weight:800; color:#f5d8c8;">
                                Spokojna Przystań
                            </div>
                            <h1 style="margin:10px 0 0; color:#ffffff; font-size:28px; line-height:1.2; font-weight:800;">
                                {escape(title)}
                            </h1>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:30px;">
                            <span style="display:inline-block; padding:8px 12px; border-radius:999px; background:{badge_color}; color:#ffffff; font-size:13px; font-weight:800;">
                                {escape(badge)}
                            </span>

                            <p style="margin:20px 0 0; color:#667085; font-size:16px; line-height:1.7;">
                                {escape(intro)}
                            </p>

                            {details_html}

                            <div style="margin-top:28px;">
                                <a href="{escape(appointments_url)}"
                                   style="display:inline-block; background:#246b6b; color:#ffffff; text-decoration:none; border-radius:999px; padding:13px 20px; font-weight:800; box-shadow:0 10px 20px rgba(36,107,107,0.18);">
                                    Zobacz moje wizyty
                                </a>
                            </div>

                            <div style="margin-top:26px; padding:16px 18px; background:#eef4f5; border-radius:18px; color:#667085; font-size:14px; line-height:1.6;">
                                To jest wiadomość automatyczna. Prosimy na nią nie odpowiadać.
                            </div>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:18px 30px; border-top:1px solid #d7e0e4; color:#667085; font-size:13px; background:#ffffff;">
                            Projekt UAIM — gabinet psychologiczno-terapeutyczny
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    # Generuje pojedynczy wiersz tabeli szczegółów w wiadomości HTML.
    def _detail_row(self, label, value):
        return f"""
            <tr>
                <td style="padding:14px 16px; background:#f8fbfb; border-bottom:1px solid #d7e0e4; color:#667085; font-size:13px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em; width:38%;">
                    {escape(str(label))}
                </td>
                <td style="padding:14px 16px; border-bottom:1px solid #d7e0e4; color:#1d2939; font-size:15px; font-weight:700;">
                    {escape(str(value or '—'))}
                </td>
            </tr>
        """

    # Formatuje datę wizyty do strefy czasowej aplikacji.
    def _format_datetime(self, value):
        if not value:
            return "—"

        app_timezone = os.getenv("APP_TIMEZONE", "Europe/Warsaw")

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        local_value = value.astimezone(ZoneInfo(app_timezone))
        return local_value.strftime("%d.%m.%Y, %H:%M")

    # Zwraca publiczny adres frontendu używany w linkach e-mail.
    def _public_url(self):
        return os.getenv("APP_PUBLIC_URL", "http://localhost:3000").rstrip("/")
