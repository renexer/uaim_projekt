from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class EmailNotification(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "email_notifications"

    appointment_id = db.Column(db.ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    recipient_email = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="PENDING")
    scheduled_at = db.Column(db.DateTime(timezone=True), nullable=False)
    sent_at = db.Column(db.DateTime(timezone=True), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
