from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import current_app

from app.extensions import db
from app.models import EmailNotification
from app.utils.enums import EmailNotificationStatus, EmailNotificationType


class NotificationService:
    def schedule_booking_email(self, appointment):
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
        self._create_notification(
            appointment=appointment,
            recipient_email=appointment.patient.email,
            notification_type=EmailNotificationType.APPOINTMENT_CANCELLED.value,
            scheduled_at=datetime.now(timezone.utc),
        )
        db.session.commit()

    def send_due_notifications(self):
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
        if current_app.config.get("MAIL_BACKEND") == "console":
            print(
                f"[MAIL] to={notification.recipient_email} type={notification.type} scheduled_at={notification.scheduled_at.isoformat()}"
            )
        else:  # pragma: no cover
            raise NotImplementedError("Realny backend mailowy nie został jeszcze podłączony.")
