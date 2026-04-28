from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Review(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "reviews"

    appointment_id = db.Column(db.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False, unique=True)
    patient_user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    therapist_id = db.Column(db.ForeignKey("therapist_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="PUBLISHED")

    appointment = db.relationship("Appointment", back_populates="review")
    therapist = db.relationship("TherapistProfile", back_populates="reviews")
