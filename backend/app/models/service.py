from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


# Model SQLAlchemy reprezentujący usługę terapeutyczną dostępną w katalogu.
class Service(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "services"

    code = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="PLN")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    therapists = db.relationship("TherapistService", back_populates="service", cascade="all, delete-orphan")
