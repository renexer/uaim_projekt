from app.extensions import db
from app.models import Appointment, Review, TherapistProfile
from app.repositories.review_repository import ReviewRepository
from app.utils.enums import AppointmentStatus, ReviewStatus
from app.utils.errors import ConflictError, ForbiddenError, NotFoundError


# Warstwa logiki biznesowej obsługująca tworzenie opinii i aktualizację średnich ocen.
class ReviewService:
    # Konstruktor inicjalizuje zależności potrzebne do działania klasy.
    def __init__(self, review_repository: ReviewRepository | None = None):
        self.review_repository = review_repository or ReviewRepository()

    # Tworzy opinię tylko dla zakończonej wizyty pacjenta i odświeża statystyki terapeuty.
    def create(self, patient, appointment_id, rating: int, comment: str | None = None):
        appointment = Appointment.query.filter_by(id=appointment_id, patient_user_id=patient.id).first()
        if not appointment:
            raise NotFoundError("Wizyta nie istnieje.", code="APPOINTMENT_NOT_FOUND")
        if appointment.status != AppointmentStatus.COMPLETED.value:
            raise ForbiddenError(
                "Opinię można dodać tylko do zakończonej wizyty.", code="REVIEW_ONLY_FOR_COMPLETED_APPOINTMENT"
            )
        if appointment.review:
            raise ConflictError("Opinia dla tej wizyty już istnieje.", code="REVIEW_ALREADY_EXISTS")

        review = Review(
            appointment_id=appointment.id,
            patient_user_id=patient.id,
            therapist_id=appointment.therapist_id,
            rating=rating,
            comment=comment,
            status=ReviewStatus.PUBLISHED.value,
        )
        db.session.add(review)
        db.session.commit()
        self.refresh_therapist_rating(appointment.therapist_id)
        return review

    # Przelicza średnią ocenę i liczbę opinii zapisane w profilu terapeuty.
    def refresh_therapist_rating(self, therapist_id):
        avg_rating, reviews_count = self.review_repository.get_stats_for_therapist(therapist_id)
        therapist = TherapistProfile.query.get(therapist_id)
        if therapist:
            therapist.average_rating = avg_rating
            therapist.reviews_count = reviews_count
            db.session.commit()
