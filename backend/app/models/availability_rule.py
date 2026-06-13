from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


# Model SQLAlchemy przechowujący cykliczne reguły dostępności terapeuty.
class AvailabilityRule(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "availability_rules"

    therapist_id = db.Column(db.ForeignKey("therapist_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    weekday = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    valid_from = db.Column(db.Date, nullable=False)
    valid_to = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    therapist = db.relationship("TherapistProfile", back_populates="availability_rules")
