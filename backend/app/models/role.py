from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Role(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "roles"

    name = db.Column(db.String(50), nullable=False, unique=True)
