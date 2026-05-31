from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ConsultationSummary(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "consultation_summaries"

    appointment_id = db.Column(db.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, unique=True)
    created_by_user_id = db.Column(db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    summary_text = db.Column(db.Text, nullable=False)

    appointment = db.relationship("Appointment", back_populates="consultation_summary")
