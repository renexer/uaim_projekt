from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.helpers import load_or_400, success
from app.schemas import AvailabilityExceptionCreateSchema, AvailabilityRuleCreateSchema, AvailabilityRuleUpdateSchema
from app.services.schedule_admin_service import ScheduleAdminService
from app.utils.auth import roles_required


admin_availability_bp = Blueprint("admin_availability", __name__, url_prefix="/api/v1/admin")
schedule_service = ScheduleAdminService()


@admin_availability_bp.get("/therapists/<therapist_id>/availability-rules")
@jwt_required()
@roles_required("ADMIN")
def list_rules(therapist_id):
    items = schedule_service.list_rules(therapist_id)
    return success([
        {
            "id": item.id,
            "weekday": item.weekday,
            "startTime": item.start_time.isoformat(),
            "endTime": item.end_time.isoformat(),
            "validFrom": item.valid_from.isoformat(),
            "validTo": item.valid_to.isoformat() if item.valid_to else None,
            "isActive": item.is_active,
        }
        for item in items
    ])


@admin_availability_bp.post("/therapists/<therapist_id>/availability-rules")
@jwt_required()
@roles_required("ADMIN")
def create_rule(therapist_id):
    payload = load_or_400(AvailabilityRuleCreateSchema(), request.get_json() or {})
    item = schedule_service.create_rule(therapist_id, payload)
    return success({
        "id": item.id,
        "weekday": item.weekday,
        "startTime": item.start_time.isoformat(),
        "endTime": item.end_time.isoformat(),
        "validFrom": item.valid_from.isoformat(),
        "validTo": item.valid_to.isoformat() if item.valid_to else None,
        "isActive": item.is_active,
    }, status=201)


@admin_availability_bp.patch("/availability-rules/<rule_id>")
@jwt_required()
@roles_required("ADMIN")
def update_rule(rule_id):
    payload = load_or_400(AvailabilityRuleUpdateSchema(), request.get_json() or {})
    item = schedule_service.update_rule(rule_id, payload)
    return success({
        "id": item.id,
        "weekday": item.weekday,
        "startTime": item.start_time.isoformat(),
        "endTime": item.end_time.isoformat(),
        "validFrom": item.valid_from.isoformat(),
        "validTo": item.valid_to.isoformat() if item.valid_to else None,
        "isActive": item.is_active,
    })


@admin_availability_bp.delete("/availability-rules/<rule_id>")
@jwt_required()
@roles_required("ADMIN")
def delete_rule(rule_id):
    schedule_service.delete_rule(rule_id)
    return success({"deleted": True})


@admin_availability_bp.get("/therapists/<therapist_id>/availability-exceptions")
@jwt_required()
@roles_required("ADMIN")
def list_exceptions(therapist_id):
    items = schedule_service.list_exceptions(therapist_id)
    return success([
        {
            "id": item.id,
            "type": item.type,
            "startAt": item.start_at.isoformat(),
            "endAt": item.end_at.isoformat(),
            "reason": item.reason,
        }
        for item in items
    ])


@admin_availability_bp.post("/therapists/<therapist_id>/availability-exceptions")
@jwt_required()
@roles_required("ADMIN")
def create_exception(therapist_id):
    payload = load_or_400(AvailabilityExceptionCreateSchema(), request.get_json() or {})
    item = schedule_service.create_exception(therapist_id, payload)
    return success({
        "id": item.id,
        "type": item.type,
        "startAt": item.start_at.isoformat(),
        "endAt": item.end_at.isoformat(),
        "reason": item.reason,
    }, status=201)
