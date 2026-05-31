from flask import Blueprint, request
from marshmallow import EXCLUDE, Schema, fields

from app.api.helpers import load_or_400, success
from app.schemas import TherapistPublicSchema
from app.services.catalog_service import CatalogService


class TherapistsQuerySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    serviceId = fields.String(load_default=None)
    q = fields.String(load_default=None)


therapists_bp = Blueprint("therapists", __name__, url_prefix="/api/v1/therapists")
catalog_service = CatalogService()
therapist_schema = TherapistPublicSchema()
therapists_schema = TherapistPublicSchema(many=True)


@therapists_bp.get("")
def list_therapists():
    params = load_or_400(TherapistsQuerySchema(), request.args.to_dict())
    items = catalog_service.list_therapists(
        service_id=params.get("serviceId"),
        search_query=params.get("q"),
    )
    return success(therapists_schema.dump(items))


@therapists_bp.get("/<therapist_id>")
def get_therapist(therapist_id):
    return success(therapist_schema.dump(catalog_service.get_therapist_public(therapist_id)))