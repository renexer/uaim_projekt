from functools import wraps

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import User
from app.utils.errors import ForbiddenError, UnauthorizedError


# Pobiera użytkownika z tokena JWT i zapewnia jednolitą obsługę błędów autoryzacji.
def get_current_user() -> User:
    """Zwraca użytkownika powiązanego z aktualnym JWT albo zgłasza 401."""
    identity = get_jwt_identity()
    if not identity:
        raise UnauthorizedError("Brak tożsamości użytkownika.")
    user = User.query.get(identity)
    if not user:
        raise UnauthorizedError("Użytkownik nie istnieje.")
    return user


# Tworzy dekorator sprawdzający, czy aktualny użytkownik ma jedną z wymaganych ról.
def roles_required(*role_names: str):
    """Dekorator ograniczający endpoint do wskazanych ról, np. ADMIN/THERAPIST."""

    # Dekorator opakowuje funkcję endpointu bez utraty jej metadanych.
    def decorator(fn):
        @wraps(fn)
        # Wrapper wymusza obecność JWT, pobiera użytkownika i porównuje jego role z wymaganiami endpointu.
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            user_role_names = {role.name for role in user.roles}
            if not user_role_names.intersection(set(role_names)):
                raise ForbiddenError("Brak wymaganych uprawnień.")
            return fn(*args, **kwargs)

        return wrapper

    return decorator