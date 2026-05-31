from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Appointment(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "appointments"

    patient_user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    therapist_id = db.Column(db.ForeignKey("therapist_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = db.Column(db.ForeignKey("services.id", ondelete="RESTRICT"), nullable=False)
    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(50), nullable=False, index=True)
    booked_at = db.Column(db.DateTime(timezone=True), nullable=False)
    cancellation_deadline_at = db.Column(db.DateTime(timezone=True), nullable=False)
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    cancelled_by_user_id = db.Column(db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    cancellation_reason = db.Column(db.String(255), nullable=True)

    service_name_snapshot = db.Column(db.String(255), nullable=False)
    service_description_snapshot = db.Column(db.Text, nullable=False)
    duration_minutes_snapshot = db.Column(db.Integer, nullable=False)
    price_snapshot = db.Column(db.Numeric(10, 2), nullable=False)
    therapist_name_snapshot = db.Column(db.String(255), nullable=False)
    therapist_title_snapshot = db.Column(db.String(255), nullable=False)

    patient = db.relationship("User", foreign_keys=[patient_user_id], back_populates="patient_appointments")
    therapist = db.relationship("TherapistProfile", back_populates="appointments")
    service = db.relationship("Service")
    consultation_summary = db.relationship(
        "ConsultationSummary", back_populates="appointment", uselist=False, cascade="all, delete-orphan"
    )
    review = db.relationship("Review", back_populates="appointment", uselist=False, cascade="all, delete-orphan")
