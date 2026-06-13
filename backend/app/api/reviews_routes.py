from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.api.helpers import load_or_400, success
from app.schemas import ReviewCreateSchema
from app.services.catalog_service import CatalogService
from app.services.review_service import ReviewService
from app.utils.auth import get_current_user
from app.utils.pagination import paginate_items


# Blueprint obsługuje opinie pacjentów o terapeutach i wizytach.
reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/v1")
# Serwis katalogu służy tutaj do pobierania opublikowanych opinii terapeuty.
catalog_service = CatalogService()
# Serwis opinii odpowiada za walidację i zapis nowej recenzji.
review_service = ReviewService()


@reviews_bp.get("/therapists/<therapist_id>/reviews")
# Endpoint zwraca paginowaną listę opublikowanych opinii dla terapeuty.
def get_reviews(therapist_id):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("pageSize", 10)), 1), 100)
    items = catalog_service.list_published_reviews(therapist_id)
    sliced, meta = paginate_items(items, page, page_size)
    payload = [
        {
            "id": str(item.id),
            "rating": item.rating,
            "comment": item.comment,
            "createdAt": item.created_at.isoformat() if item.created_at else None,
        }
        for item in sliced
    ]
    return success(payload, meta=meta)


@reviews_bp.post("/appointments/<appointment_id>/review")
@jwt_required()
# Endpoint pozwala pacjentowi dodać opinię po zakończonej wizycie.
def create_review(appointment_id):
    payload = load_or_400(ReviewCreateSchema(), request.get_json() or {})
    user = get_current_user()
    review = review_service.create(user, appointment_id, payload["rating"], payload.get("comment"))
    return success({
        "id": str(review.id),
        "rating": review.rating,
        "comment": review.comment,
        "status": review.status,
    }, status=201)