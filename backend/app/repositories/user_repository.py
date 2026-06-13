from app.extensions import db
from app.models import Role, User
from app.repositories.base_repository import BaseRepository


# Repozytorium obsługujące wyszukiwanie użytkowników i ról.
class UserRepository(BaseRepository):
    model = User

    # Wyszukuje użytkownika po adresie e-mail.
    def get_by_email(self, email: str):
        return User.query.filter(db.func.lower(User.email) == email.lower()).first()

    # Wyszukuje rolę po jej nazwie systemowej.
    def get_role_by_name(self, role_name: str):
        return Role.query.filter_by(name=role_name).first()
