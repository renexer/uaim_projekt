from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from app.api.helpers import load_or_400, success
from app.schemas import AppointmentStatusUpdateSchema, ConsultationSummaryUpsertSchema
from app.services.staff_appointment_service import StaffAppointmentService
from app.utils.auth import get_current_user, roles_required
from app.utils.pagination import paginate_items


class StaffAppointmentsQuerySchema(Schema):
    from_ = fields.DateTime(load_default=None, data_key="from")
    to = fields.DateTime(load_default=None)
    therapistId = fields.String(load_default=None)
    status = fields.String(load_default=None)
    patientEmail = fields.Email(load_default=None)


staff_appointments_bp = Blueprint("staff_appointments", __name__, url_prefix="/api/v1/staff")
staff_service = StaffAppointmentService()


@staff_appointments_bp.get("/appointments")
@jwt_required()
@roles_required("ADMIN", "THERAPIST")
def list_staff_appointments():
    filters = load_or_400(StaffAppointmentsQuerySchema(), request.args.to_dict())
    current_user = get_current_user()
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("pageSize", 10)), 1), 100)
    items = staff_service.list_appointments(filters, current_user)
    sliced, meta = paginate_items(items, page, page_size)
    return success([
        {
            "id": item.id,
            "status": item.status,
            "startAt": item.start_at.isoformat(),
            "endAt": item.end_at.isoformat(),
            "patientEmail": item.patient.email,
            "serviceName": item.service_name_snapshot,
            "therapistName": item.therapist_name_snapshot,
        }
        for item in sliced
    ], meta=meta)


@staff_appointments_bp.patch("/appointments/<appointment_id>/status")
@jwt_required()
@roles_required("ADMIN", "THERAPIST")
def update_appointment_status(appointment_id):
    payload = load_or_400(AppointmentStatusUpdateSchema(), request.get_json() or {})
    current_user = get_current_user()
    item = staff_service.update_status(appointment_id, payload, current_user)
    return success({
        "id": item.id,
        "status": item.status,
        "cancelledAt": item.cancelled_at.isoformat() if item.cancelled_at else None,
        "cancellationReason": item.cancellation_reason,
    })


@staff_appointments_bp.put("/appointments/<appointment_id>/consultation-summary")
@jwt_required()
@roles_required("ADMIN", "THERAPIST")
def upsert_consultation_summary(appointment_id):
    payload = load_or_400(ConsultationSummaryUpsertSchema(), request.get_json() or {})
    current_user = get_current_user()
    item = staff_service.upsert_consultation_summary(appointment_id, current_user, payload["summaryText"])
    return success({
        "id": item.id,
        "appointmentId": item.appointment_id,
        "summaryText": item.summary_text,
    })
