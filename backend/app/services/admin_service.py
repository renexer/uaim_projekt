from app.extensions import db
from app.models import Service
from app.utils.errors import ConflictError, NotFoundError


# Warstwa logiki biznesowej dla administracyjnego zarządzania usługami.
class AdminService:
    # Zwraca wszystkie usługi dla panelu administratora, również nieaktywne.
    def list_services(self):
        return Service.query.order_by(Service.name.asc()).all()

    # Tworzy nową usługę na podstawie danych z panelu administratora.
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

    # Aktualizuje dane istniejącej usługi bez tworzenia nowego rekordu.
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
