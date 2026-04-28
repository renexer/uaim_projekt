from __future__ import annotations
from app.models import TherapistProfile
from app.repositories.review_repository import ReviewRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.therapist_repository import TherapistRepository
from app.utils.errors import NotFoundError


class CatalogService:
    def __init__(
        self,
        service_repository: ServiceRepository | None = None,
        therapist_repository: TherapistRepository | None = None,
        review_repository: ReviewRepository | None = None,
    ):
        self.service_repository = service_repository or ServiceRepository()
        self.therapist_repository = therapist_repository or TherapistRepository()
        self.review_repository = review_repository or ReviewRepository()

    def list_services(self):
        return self.service_repository.list_active()

    def get_service(self, service_id):
        service = self.service_repository.get_active(service_id)
        if not service:
            raise NotFoundError("Usługa nie istnieje.", code="SERVICE_NOT_FOUND")
        return service

    def list_therapists_for_service(self, service_id):
        self.get_service(service_id)
        return self.therapist_repository.list_for_service(service_id)

    def get_therapist_public(self, therapist_id):
        therapist = TherapistProfile.query.filter_by(id=therapist_id, is_active=True).first()
        if not therapist:
            raise NotFoundError("Terapeuta nie istnieje.", code="THERAPIST_NOT_FOUND")
        return therapist

    def list_published_reviews(self, therapist_id):
        self.get_therapist_public(therapist_id)
        return self.review_repository.list_published_for_therapist(therapist_id)
