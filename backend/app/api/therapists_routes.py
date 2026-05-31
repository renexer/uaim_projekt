from flask import Blueprint

from app.api.helpers import success
from app.schemas import TherapistPublicSchema
from app.services.catalog_service import CatalogService


therapists_bp = Blueprint("therapists", __name__, url_prefix="/api/v1/therapists")
catalog_service = CatalogService()
therapist_schema = TherapistPublicSchema()


@therapists_bp.get("/<therapist_id>")
def get_therapist(therapist_id):
    return success(therapist_schema.dump(catalog_service.get_therapist_public(therapist_id)))
