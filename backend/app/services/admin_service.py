from app.extensions import db
from app.models import Service
from app.utils.errors import ConflictError, NotFoundError


class AdminService:
    def list_services(self):
        return Service.query.order_by(Service.name.asc()).all()

    def create_service(self, payload: dict):
        existing = Service.query.filter_by(code=payload["code"]).first()
        if existing:
            raise ConflictError("Usługa o takim kodzie już istnieje.", code="SERVICE_CODE_ALREADY_EXISTS")
        service = Service(
            code=payload["code"],
            name=payload["name"],
            description=payload["description"],
            duration_minutes=payload["durationMinutes"],
            base_price=payload["basePrice"],
            currency=payload.get("currency", "PLN"),
            is_active=payload.get("isActive", True),
        )
        db.session.add(service)
        db.session.commit()
        return service

    def update_service(self, service_id, payload: dict):
        service = Service.query.get(service_id)
        if not service:
            raise NotFoundError("Usługa nie istnieje.", code="SERVICE_NOT_FOUND")
        if "code" in payload and payload["code"] != service.code:
            existing = Service.query.filter_by(code=payload["code"]).first()
            if existing:
                raise ConflictError("Usługa o takim kodzie już istnieje.", code="SERVICE_CODE_ALREADY_EXISTS")
            service.code = payload["code"]
        if "name" in payload:
            service.name = payload["name"]
        if "description" in payload:
            service.description = payload["description"]
        if "durationMinutes" in payload:
            service.duration_minutes = payload["durationMinutes"]
        if "basePrice" in payload:
            service.base_price = payload["basePrice"]
        if "currency" in payload:
            service.currency = payload["currency"]
        if "isActive" in payload:
            service.is_active = payload["isActive"]
        db.session.commit()
        return service
