import uuid

from sqlalchemy.sql import func

from app.extensions import db


class UUIDPrimaryKeyMixin:
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )