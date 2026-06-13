from sqlalchemy import func

from app.models import Review
from app.repositories.base_repository import BaseRepository


# Repozytorium obsługujące odczyt opinii i statystyk ocen terapeutów.
class ReviewRepository(BaseRepository):
    model = Review

    # Pobiera opublikowane opinie dla wskazanego terapeuty.
    def list_published_for_therapist(self, therapist_id):
        return (
            Review.query.filter_by(therapist_id=therapist_id, status="PUBLISHED")
            .order_by(Review.created_at.desc())
            .all()
        )

    # Oblicza średnią ocenę i liczbę opinii dla wskazanego terapeuty.
    def get_stats_for_therapist(self, therapist_id):
        avg_rating, reviews_count = (
            Review.query.with_entities(func.avg(Review.rating), func.count(Review.id))
            .filter_by(therapist_id=therapist_id, status="PUBLISHED")
            .first()
        )
        return avg_rating or 0, reviews_count or 0
