from sqlalchemy import or_

from app.models import TherapistProfile, TherapistService, User


# Repozytorium obsługujące zapytania dotyczące profili terapeutów.
class TherapistRepository:
    # Pobiera encję po identyfikatorze z użyciem modelu przypisanego do repozytorium.
    def get(self, therapist_id):
        return TherapistProfile.query.filter_by(id=therapist_id).first()

    # Pobiera aktywnych terapeutów realizujących wskazaną usługę.
    def list_for_service(self, service_id):
        return (
            TherapistProfile.query.join(
                TherapistService, TherapistService.therapist_id == TherapistProfile.id
            )
            .filter(
                TherapistProfile.is_active.is_(True),
                TherapistService.service_id == service_id,
                TherapistService.is_active.is_(True),
            )
            .order_by(TherapistProfile.created_at.desc())
            .all()
        )

    # Pobiera publiczną listę aktywnych terapeutów, opcjonalnie zawężoną wyszukiwaniem.
    def list_public(self, service_id=None, search_query=None):
        query = (
            TherapistProfile.query.join(User, User.id == TherapistProfile.user_id)
            .filter(TherapistProfile.is_active.is_(True))
        )

        if service_id:
            query = query.join(
                TherapistService, TherapistService.therapist_id == TherapistProfile.id
            ).filter(
                TherapistService.service_id == service_id,
                TherapistService.is_active.is_(True),
            )

        if search_query:
            pattern = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    User.first_name.ilike(pattern),
                    User.last_name.ilike(pattern),
                    TherapistProfile.title.ilike(pattern),
                    TherapistProfile.bio.ilike(pattern),
                )
            )

        return query.order_by(User.last_name.asc(), User.first_name.asc()).all()
