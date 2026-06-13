from flask import Blueprint

from app.api.helpers import success
from app.schemas import ServiceSchema, TherapistPublicSchema
from app.services.catalog_service import CatalogService


# Blueprint publiczny udostępnia katalog usług dostępnych w gabinecie.
services_bp = Blueprint("services", __name__, url_prefix="/api/v1/services")
# Serwis katalogowy pobiera usługi i terapeutów bez przenoszenia logiki do kontrolerów.
catalog_service = CatalogService()
# Schemat pojedynczej usługi do serializacji odpowiedzi.
service_schema = ServiceSchema()
# Schemat listy usług do serializacji wielu rekordów.
services_schema = ServiceSchema(many=True)
# Schemat listy terapeutów przypisanych do wybranej usługi.
therapists_schema = TherapistPublicSchema(many=True)


@services_bp.get("")
# Endpoint zwraca listę aktywnych usług.
def list_services():
    return success(services_schema.dump(catalog_service.list_services()))


@services_bp.get("/<service_id>")
# Endpoint zwraca szczegóły pojedynczej usługi.
def get_service(service_id):
    return success(service_schema.dump(catalog_service.get_service(service_id)))


@services_bp.get("/<service_id>/therapists")
# Endpoint zwraca terapeutów wykonujących wskazaną usługę.
def get_therapists_for_service(service_id):
    return success(therapists_schema.dump(catalog_service.list_therapists_for_service(service_id)))