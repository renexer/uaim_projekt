from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.helpers import load_or_400, success
from app.schemas import ServiceCreateSchema, ServiceSchema, ServiceUpdateSchema
from app.services.admin_service import AdminService
from app.utils.auth import roles_required


# Blueprint administracyjny dla zarządzania katalogiem usług.
admin_services_bp = Blueprint("admin_services", __name__, url_prefix="/api/v1/admin/services")
# Serwis administracyjny wykonuje operacje na usługach poza warstwą HTTP.
admin_service = AdminService()
# Schemat pojedynczej usługi serializuje obiekt modelu do odpowiedzi JSON.
service_schema = ServiceSchema()
# Schemat listy usług obsługuje serializację wielu rekordów naraz.
services_schema = ServiceSchema(many=True)


@admin_services_bp.get("")
@jwt_required()
@roles_required("ADMIN")
# Endpoint zwraca pełną listę usług dla panelu administratora.
def list_admin_services():
    return success(services_schema.dump(admin_service.list_services()))


@admin_services_bp.post("")
@jwt_required()
@roles_required("ADMIN")
# Endpoint tworzy nową usługę na podstawie zwalidowanego payloadu.
def create_service():
    payload = load_or_400(ServiceCreateSchema(), request.get_json() or {})
    return success(service_schema.dump(admin_service.create_service(payload)), status=201)


@admin_services_bp.patch("/<service_id>")
@jwt_required()
@roles_required("ADMIN")
# Endpoint aktualizuje wskazaną usługę i zwraca jej aktualny stan.
def update_service(service_id):
    payload = load_or_400(ServiceUpdateSchema(), request.get_json() or {})
    return success(service_schema.dump(admin_service.update_service(service_id, payload)))