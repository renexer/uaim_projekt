from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.helpers import load_or_400, success
from app.models import User
from app.schemas import LoginSchema, RegisterSchema
from app.services.auth_service import AuthService
from app.utils.auth import get_current_user
from app.utils.errors import UnauthorizedError


# Blueprint uwierzytelniania udostępnia rejestrację, logowanie i obsługę tokenów JWT.
auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1")
# Serwis auth wykonuje operacje związane z użytkownikiem, hasłem i tokenami.
auth_service = AuthService()


@auth_bp.post("/auth/register")
# Endpoint rejestruje konto pacjenta i zwraca dane nowo utworzonego użytkownika.
def register():
    payload = load_or_400(RegisterSchema(), request.get_json() or {})
    user = auth_service.register_patient(payload)
    return success(AuthService.serialize_user(user), status=201)


@auth_bp.post("/auth/login")
# Endpoint loguje użytkownika i zwraca tokeny potrzebne do autoryzacji żądań.
def login():
    payload = load_or_400(LoginSchema(), request.get_json() or {})
    return success(auth_service.login(payload["email"], payload["password"]))


@auth_bp.post("/auth/refresh")
@jwt_required(refresh=True)
# Endpoint odświeża access token na podstawie poprawnego refresh tokena.
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        raise UnauthorizedError("Użytkownik nie istnieje.")
    return success(auth_service.refresh(user))


@auth_bp.post("/auth/logout")
@jwt_required()
# Endpoint obsługuje wylogowanie użytkownika po stronie API.
def logout():
    user = get_current_user()
    return success(auth_service.logout(user))


@auth_bp.get("/users/me")
@jwt_required()
# Endpoint zwraca profil aktualnie zalogowanego użytkownika.
def me():
    user = User.query.get(get_jwt_identity())
    if not user:
        raise UnauthorizedError("Użytkownik nie istnieje.")
    return success(AuthService.serialize_user(user))