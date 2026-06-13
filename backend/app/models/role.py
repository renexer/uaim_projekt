from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


# Model SQLAlchemy opisujący rolę użytkownika w systemie.
class Role(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "roles"

    name = db.Column(db.String(50), nullable=False, unique=True)
