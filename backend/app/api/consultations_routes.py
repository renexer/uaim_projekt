from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.helpers import success
from app.services.consultation_service import ConsultationService
from app.utils.auth import get_current_user
from app.utils.pagination import paginate_items


# Blueprint udostępnia pacjentowi historię zrealizowanych konsultacji.
consultations_bp = Blueprint("consultations", __name__, url_prefix="/api/v1")
# Serwis konsultacji pobiera zakończone wizyty i powiązane podsumowania.
consultation_service = ConsultationService()


@consultations_bp.get("/consultations/me")
@jwt_required()
# Endpoint zwraca paginowaną historię konsultacji aktualnie zalogowanego pacjenta.
def list_my_consultations():
    user = get_current_user()
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("pageSize", 10)), 1), 100)
    items = consultation_service.list_for_patient(user.id)
    sliced, meta = paginate_items(items, page, page_size)
    return success([
        {
            "appointmentId": str(item.id),
            "completedAt": item.end_at.isoformat(),
            "service": {
                "name": item.service_name_snapshot,
                "description": item.service_description_snapshot,
            },
            "therapist": {
                "name": item.therapist_name_snapshot,
                "title": item.therapist_title_snapshot,
            },
            "summary": {
                "text": item.consultation_summary.summary_text if item.consultation_summary else None,
            },
            "review": {
                "exists": item.review is not None,
            },
        }
        for item in sliced
    ], meta=meta)