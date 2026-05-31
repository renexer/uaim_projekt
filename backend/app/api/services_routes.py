from flask import Blueprint

from app.api.helpers import success
from app.schemas import ServiceSchema, TherapistPublicSchema
from app.services.catalog_service import CatalogService


services_bp = Blueprint("services", __name__, url_prefix="/api/v1/services")
catalog_service = CatalogService()
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)
therapists_schema = TherapistPublicSchema(many=True)


@services_bp.get("")
def list_services():
    return success(services_schema.dump(catalog_service.list_services()))


@services_bp.get("/<service_id>")
def get_service(service_id):
    return success(service_schema.dump(catalog_service.get_service(service_id)))


@services_bp.get("/<service_id>/therapists")
def get_therapists_for_service(service_id):
    return success(therapists_schema.dump(catalog_service.list_therapists_for_service(service_id)))
