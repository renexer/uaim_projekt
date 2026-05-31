from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.helpers import load_or_400, success
from app.schemas import TherapistProfileCreateSchema, TherapistProfileUpdateSchema, TherapistPublicSchema, TherapistServiceAssignSchema
from app.services.therapist_admin_service import TherapistAdminService
from app.utils.auth import roles_required


admin_therapists_bp = Blueprint("admin_therapists", __name__, url_prefix="/api/v1/admin/therapists")
therapist_admin_service = TherapistAdminService()
therapist_schema = TherapistPublicSchema()
therapists_schema = TherapistPublicSchema(many=True)


@admin_therapists_bp.get("")
@jwt_required()
@roles_required("ADMIN")
def list_therapists():
    return success(therapists_schema.dump(therapist_admin_service.list_therapists()))


@admin_therapists_bp.post("")
@jwt_required()
@roles_required("ADMIN")
def create_therapist():
    payload = load_or_400(TherapistProfileCreateSchema(), request.get_json() or {})
    return success(therapist_schema.dump(therapist_admin_service.create_therapist_profile(payload)), status=201)


@admin_therapists_bp.patch("/<therapist_id>")
@jwt_required()
@roles_required("ADMIN")
def update_therapist(therapist_id):
    payload = load_or_400(TherapistProfileUpdateSchema(), request.get_json() or {})
    return success(therapist_schema.dump(therapist_admin_service.update_therapist_profile(therapist_id, payload)))


@admin_therapists_bp.post("/<therapist_id>/services")
@jwt_required()
@roles_required("ADMIN")
def assign_service(therapist_id):
    payload = load_or_400(TherapistServiceAssignSchema(), request.get_json() or {})
    link = therapist_admin_service.assign_service(therapist_id, payload)
    return success({
        "id": str(link.id),
        "therapistId": link.therapist_id,
        "serviceId": link.service_id,
        "isActive": link.is_active,
    }, status=201)


@admin_therapists_bp.delete("/<therapist_id>/services/<service_id>")
@jwt_required()
@roles_required("ADMIN")
def remove_service(therapist_id, service_id):
    link = therapist_admin_service.remove_service(therapist_id, service_id)
    return success({
        "id": str(link.id),
        "therapistId": link.therapist_id,
        "serviceId": link.service_id,
        "isActive": link.is_active,
    })
