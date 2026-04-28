from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AvailabilityException(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "availability_exceptions"

    therapist_id = db.Column(db.ForeignKey("therapist_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=False)
    reason = db.Column(db.String(255), nullable=True)

    therapist = db.relationship("TherapistProfile", back_populates="availability_exceptions")
