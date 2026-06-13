from app.extensions import db
from app.models import TherapistProfile, TherapistService, User
from app.utils.errors import ConflictError, NotFoundError


# Warstwa logiki biznesowej do zarządzania profilami terapeutów i ich usługami.
class TherapistAdminService:
    # Zwraca listę profili terapeutów w kolejności od najnowszych.
    def list_therapists(self):
        return TherapistProfile.query.order_by(TherapistProfile.created_at.desc()).all()

    # Pobiera profil terapeuty albo zgłasza błąd, gdy profil nie istnieje.
    def get_therapist(self, therapist_id):
        therapist = TherapistProfile.query.get(therapist_id)
        if not therapist:
            raise NotFoundError("Terapeuta nie istnieje.", code="THERAPIST_NOT_FOUND")
        return therapist

    # Tworzy profil terapeuty dla istniejącego użytkownika.
    def create_therapist_profile(self, payload: dict):
        user = User.query.get(payload["userId"])
        if not user:
            raise NotFoundError("Użytkownik nie istnieje.", code="USER_NOT_FOUND")
        if user.therapist_profile:
            raise ConflictError("Profil terapeuty już istnieje.", code="THERAPIST_PROFILE_EXISTS")
        therapist = TherapistProfile(
            user_id=user.id,
            title=payload["title"],
            bio=payload["bio"],
            experience_years=payload.get("experienceYears"),
            photo_url=payload.get("photoUrl"),
            is_active=payload.get("isActive", True),
        )
        db.session.add(therapist)
        db.session.commit()
        return therapist

    # Aktualizuje dane profilu terapeuty.
    def update_therapist_profile(self, therapist_id, payload: dict):
        therapist = self.get_therapist(therapist_id)
        if "title" in payload:
            therapist.title = payload["title"]
        if "bio" in payload:
            therapist.bio = payload["bio"]
        if "experienceYears" in payload:
            therapist.experience_years = payload["experienceYears"]
        if "photoUrl" in payload:
            therapist.photo_url = payload["photoUrl"]
        if "isActive" in payload:
            therapist.is_active = payload["isActive"]
        db.session.commit()
        return therapist

    # Przypisuje usługę do terapeuty albo aktualizuje istniejące powiązanie.
    def assign_service(self, therapist_id, payload: dict):
        self.get_therapist(therapist_id)
        service_id = payload["serviceId"]
        existing = TherapistService.query.filter_by(therapist_id=therapist_id, service_id=service_id).first()
        if existing:
            existing.is_active = payload.get("isActive", True)
            existing.price_override = payload.get("priceOverride")
            existing.duration_override_minutes = payload.get("durationOverrideMinutes")
            db.session.commit()
            return existing
        entity = TherapistService(
            therapist_id=therapist_id,
            service_id=service_id,
            is_active=payload.get("isActive", True),
            price_override=payload.get("priceOverride"),
            duration_override_minutes=payload.get("durationOverrideMinutes"),
        )
        db.session.add(entity)
        db.session.commit()
        return entity

    # Dezaktywuje powiązanie terapeuty z usługą.
    def remove_service(self, therapist_id, service_id):
        link = TherapistService.query.filter_by(therapist_id=therapist_id, service_id=service_id).first()
        if not link:
            raise NotFoundError("Powiązanie terapeuty z usługą nie istnieje.", code="THERAPIST_SERVICE_NOT_FOUND")
        link.is_active = False
        db.session.commit()
        return link
