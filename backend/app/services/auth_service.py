from datetime import datetime, timezone

from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import Role, User, UserRole
from app.repositories.user_repository import UserRepository
from app.utils.enums import RoleName
from app.utils.errors import ConflictError, UnauthorizedError


class AuthService:
    def __init__(self, user_repository=None):
        self.user_repository = user_repository or UserRepository()

    def register_patient(self, payload: dict) -> User:
        existing_user = self.user_repository.get_by_email(payload["email"])
        if existing_user:
            raise ConflictError(
                "Użytkownik o takim adresie email już istnieje.",
                code="USER_ALREADY_EXISTS",
            )

        patient_role = self.user_repository.get_role_by_name(RoleName.PATIENT.value)
        if not patient_role:
            patient_role = Role(name=RoleName.PATIENT.value)
            db.session.add(patient_role)
            db.session.flush()

        user = User(
            email=payload["email"].lower(),
            password_hash=generate_password_hash(payload["password"], method="pbkdf2:sha256"),
            first_name=payload["firstName"],
            last_name=payload["lastName"],
            phone=payload.get("phone"),
        )
        db.session.add(user)
        db.session.flush()

        db.session.add(UserRole(user_id=user.id, role_id=patient_role.id))
        db.session.commit()
        return user

    def login(self, email: str, password: str) -> dict:
        user = self.user_repository.get_by_email(email)
        if not user or not check_password_hash(user.password_hash, password):
            raise UnauthorizedError(
                "Nieprawidłowy email lub hasło.",
                code="AUTH_INVALID_CREDENTIALS",
            )
        if not user.is_active:
            raise UnauthorizedError("Konto użytkownika jest nieaktywne.", code="USER_INACTIVE")

        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
        return self._issue_tokens(user)

    def refresh(self, user: User) -> dict:
        return {"accessToken": create_access_token(identity=str(user.id))}

    def logout(self, user: User) -> dict:
        return {"message": f"Użytkownik {user.email} został wylogowany po stronie klienta."}

    def _issue_tokens(self, user: User) -> dict:
        return {
            "accessToken": create_access_token(identity=str(user.id)),
            "refreshToken": create_refresh_token(identity=str(user.id)),
            "user": self.serialize_user(user),
        }

    @staticmethod
    def serialize_user(user: User) -> dict:
        return {
            "id": str(user.id),
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "roles": [role.name for role in user.roles],
        }
