from app.models import TherapistProfile, TherapistService
from app.repositories.base_repository import BaseRepository


class TherapistRepository(BaseRepository):
    model = TherapistProfile

    def list_for_service(self, service_id):
        return (
            TherapistProfile.query.join(TherapistService)
            .filter(
                TherapistService.service_id == service_id,
                TherapistService.is_active.is_(True),
                TherapistProfile.is_active.is_(True),
            )
            .all()
        )
