from flask import Blueprint, request
from marshmallow import EXCLUDE, Schema, fields

from app.api.helpers import load_or_400, success
from app.schemas import TherapistPublicSchema
from app.services.catalog_service import CatalogService


# Schemat waliduje parametry filtrowania listy terapeutów.
class TherapistsQuerySchema(Schema):
    # Konfiguracja ignoruje nieznane parametry zapytania, aby endpoint był odporny na dodatkowe pola.
    class Meta:
        unknown = EXCLUDE

    serviceId = fields.String(load_default=None)
    q = fields.String(load_default=None)


# Blueprint publiczny udostępnia listę terapeutów oraz szczegóły profilu.
therapists_bp = Blueprint("therapists", __name__, url_prefix="/api/v1/therapists")
# Serwis katalogowy dostarcza dane terapeutów i ich powiązania z usługami.
catalog_service = CatalogService()
# Schemat pojedynczego terapeuty używany w szczegółach profilu.
therapist_schema = TherapistPublicSchema()
# Schemat listy terapeutów używany przy wyszukiwaniu.
therapists_schema = TherapistPublicSchema(many=True)


@therapists_bp.get("")
# Endpoint zwraca terapeutów opcjonalnie filtrowanych po usłudze i frazie wyszukiwania.
def list_therapists():
    params = load_or_400(TherapistsQuerySchema(), request.args.to_dict())
    items = catalog_service.list_therapists(
        service_id=params.get("serviceId"),
        search_query=params.get("q"),
    )
    return success(therapists_schema.dump(items))


@therapists_bp.get("/<therapist_id>")
# Endpoint zwraca publiczne szczegóły wybranego terapeuty.
def get_therapist(therapist_id):
    return success(therapist_schema.dump(catalog_service.get_therapist_public(therapist_id)))