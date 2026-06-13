from sqlalchemy.ext.associationproxy import association_proxy

from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


# Tabela asocjacyjna SQLAlchemy łącząca użytkowników z przypisanymi rolami.
class UserRole(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "user_roles"

    user_id = db.Column(db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = db.Column(db.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    user = db.relationship("User", back_populates="role_links")
    role = db.relationship("Role")

    __table_args__ = (db.UniqueConstraint("user_id", "role_id", name="uq_user_role"),)


# Model SQLAlchemy reprezentujący konto użytkownika aplikacji.
class User(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_email_verified = db.Column(db.Boolean, nullable=False, default=False)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    role_links = db.relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    roles = association_proxy("role_links", "role")
    therapist_profile = db.relationship("TherapistProfile", back_populates="user", uselist=False)

    patient_appointments = db.relationship(
        "Appointment",
        foreign_keys="Appointment.patient_user_id",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    # Zwraca pełną nazwę użytkownika złożoną z imienia i nazwiska.
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
