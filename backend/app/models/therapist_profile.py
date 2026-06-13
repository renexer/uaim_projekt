from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


# Model SQLAlchemy opisujący publiczny profil terapeuty powiązany z kontem użytkownika.
class TherapistProfile(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "therapist_profiles"

    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    title = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    experience_years = db.Column(db.Integer, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    average_rating = db.Column(db.Numeric(3, 2), nullable=False, default=0)
    reviews_count = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship("User", back_populates="therapist_profile")
    services = db.relationship("TherapistService", back_populates="therapist", cascade="all, delete-orphan")
    availability_rules = db.relationship(
        "AvailabilityRule", back_populates="therapist", cascade="all, delete-orphan"
    )
    availability_exceptions = db.relationship(
        "AvailabilityException", back_populates="therapist", cascade="all, delete-orphan"
    )
    appointments = db.relationship("Appointment", back_populates="therapist")
    reviews = db.relationship("Review", back_populates="therapist")
