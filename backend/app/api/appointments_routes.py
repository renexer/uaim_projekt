from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.helpers import load_or_400, success
from app.schemas import AppointmentCancelSchema, AppointmentCreateSchema
from app.services.appointment_service import AppointmentService
from app.utils.auth import get_current_user
from app.utils.pagination import paginate_items


# Blueprint obsługuje endpointy pacjenta dotyczące rezerwacji wizyt.
appointments_bp = Blueprint("appointments", __name__, url_prefix="/api/v1")
# Serwis wizyt zawiera właściwą logikę rezerwacji, pobierania i anulowania terminów.
appointment_service = AppointmentService()


@appointments_bp.post("/appointments")
@jwt_required()
# Endpoint tworzy rezerwację wizyty dla aktualnie zalogowanego pacjenta.
def create_appointment():
    payload = load_or_400(AppointmentCreateSchema(), request.get_json() or {})
    user = get_current_user()
    appointment = appointment_service.create(user, payload)
    return success({
        "id": str(appointment.id),
        "status": appointment.status,
        "startAt": appointment.start_at.isoformat(),
        "endAt": appointment.end_at.isoformat(),
        "cancellationDeadlineAt": appointment.cancellation_deadline_at.isoformat(),
    }, status=201)


@appointments_bp.get("/appointments/me")
@jwt_required()
# Endpoint zwraca paginowaną listę wizyt aktualnego pacjenta.
def get_my_appointments():
    user = get_current_user()
    scope = request.args.get("scope", "upcoming")
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("pageSize", 10)), 1), 100)
    items = appointment_service.list_for_patient(user.id, scope)
    sliced, meta = paginate_items(items, page, page_size)
    return success([
        {
            "id": str(item.id),
            "status": item.status,
            "startAt": item.start_at.isoformat(),
            "endAt": item.end_at.isoformat(),
            "serviceName": item.service_name_snapshot,
            "therapistName": item.therapist_name_snapshot,
        }
        for item in sliced
    ], meta=meta)


@appointments_bp.get("/appointments/<appointment_id>")
@jwt_required()
# Endpoint zwraca szczegóły pojedynczej wizyty należącej do aktualnego pacjenta.
def get_appointment_details(appointment_id):
    user = get_current_user()
    item = appointment_service.get_details_for_patient(user.id, appointment_id)
    return success({
        "id": str(item.id),
        "status": item.status,
        "startAt": item.start_at.isoformat(),
        "endAt": item.end_at.isoformat(),
        "service": {
            "name": item.service_name_snapshot,
            "description": item.service_description_snapshot,
        },
        "therapist": {
            "name": item.therapist_name_snapshot,
            "title": item.therapist_title_snapshot,
        },
    })


@appointments_bp.post("/appointments/<appointment_id>/cancel")
@jwt_required()
# Endpoint anuluje wizytę pacjenta i zapisuje opcjonalny powód anulowania.
def cancel_appointment(appointment_id):
    payload = load_or_400(AppointmentCancelSchema(), request.get_json() or {})
    user = get_current_user()
    item = appointment_service.cancel(user, appointment_id, payload.get("reason"))
    return success({
        "id": str(item.id),
        "status": item.status,
        "cancelledAt": item.cancelled_at.isoformat() if item.cancelled_at else None,
    })