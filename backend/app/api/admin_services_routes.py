from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.helpers import load_or_400, success
from app.schemas import ServiceCreateSchema, ServiceSchema, ServiceUpdateSchema
from app.services.admin_service import AdminService
from app.utils.auth import roles_required


admin_services_bp = Blueprint("admin_services", __name__, url_prefix="/api/v1/admin/services")
admin_service = AdminService()
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)


@admin_services_bp.get("")
@jwt_required()
@roles_required("ADMIN")
def list_admin_services():
    return success(services_schema.dump(admin_service.list_services()))


@admin_services_bp.post("")
@jwt_required()
@roles_required("ADMIN")
def create_service():
    payload = load_or_400(ServiceCreateSchema(), request.get_json() or {})
    return success(service_schema.dump(admin_service.create_service(payload)), status=201)


@admin_services_bp.patch("/<service_id>")
@jwt_required()
@roles_required("ADMIN")
def update_service(service_id):
    payload = load_or_400(ServiceUpdateSchema(), request.get_json() or {})
    return success(service_schema.dump(admin_service.update_service(service_id, payload)))
