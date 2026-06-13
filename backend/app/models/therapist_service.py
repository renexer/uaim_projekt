from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


# Model SQLAlchemy łączący terapeutów z usługami, które mogą realizować.
class TherapistService(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "therapist_services"

    therapist_id = db.Column(db.ForeignKey("therapist_profiles.id", ondelete="CASCADE"), nullable=False)
    service_id = db.Column(db.ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    price_override = db.Column(db.Numeric(10, 2), nullable=True)
    duration_override_minutes = db.Column(db.Integer, nullable=True)

    therapist = db.relationship("TherapistProfile", back_populates="services")
    service = db.relationship("Service", back_populates="therapists")

    __table_args__ = (db.UniqueConstraint("therapist_id", "service_id", name="uq_therapist_service"),)
