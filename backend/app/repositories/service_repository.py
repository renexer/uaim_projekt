from app.models import Service, TherapistService
from app.repositories.base_repository import BaseRepository


class ServiceRepository(BaseRepository):
    model = Service

    def list_active(self):
        return Service.query.filter_by(is_active=True).order_by(Service.name.asc()).all()

    def get_active(self, service_id):
        return Service.query.filter_by(id=service_id, is_active=True).first()

    def therapist_link(self, therapist_id, service_id):
        return TherapistService.query.filter_by(
            therapist_id=therapist_id, service_id=service_id, is_active=True
        ).first()
