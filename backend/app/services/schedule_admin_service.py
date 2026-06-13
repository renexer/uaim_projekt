from app.extensions import db
from app.models import AvailabilityException, AvailabilityRule, TherapistProfile
from app.utils.errors import NotFoundError, ValidationError


# Warstwa logiki biznesowej do administracyjnego zarządzania grafikiem dostępności terapeutów.
class ScheduleAdminService:
    # Sprawdza, czy terapeuta istnieje przed operacją na jego grafiku.
    def _ensure_therapist(self, therapist_id):
        therapist = TherapistProfile.query.get(therapist_id)
        if not therapist:
            raise NotFoundError("Terapeuta nie istnieje.", code="THERAPIST_NOT_FOUND")
        return therapist

    # Pobiera reguły dostępności terapeuty.
    def list_rules(self, therapist_id):
        self._ensure_therapist(therapist_id)
        return AvailabilityRule.query.filter_by(therapist_id=therapist_id).order_by(AvailabilityRule.weekday.asc()).all()

    # Tworzy nową cykliczną regułę dostępności terapeuty.
    def create_rule(self, therapist_id, payload: dict):
        self._ensure_therapist(therapist_id)
        self._validate_times(payload["startTime"], payload["endTime"])
        rule = AvailabilityRule(
            therapist_id=therapist_id,
            weekday=payload["weekday"],
            start_time=payload["startTime"],
            end_time=payload["endTime"],
            valid_from=payload["validFrom"],
            valid_to=payload.get("validTo"),
            is_active=payload.get("isActive", True),
        )
        db.session.add(rule)
        db.session.commit()
        return rule

    # Aktualizuje istniejącą regułę dostępności terapeuty.
    def update_rule(self, rule_id, payload: dict):
        rule = AvailabilityRule.query.get(rule_id)
        if not rule:
            raise NotFoundError("Reguła grafiku nie istnieje.", code="AVAILABILITY_RULE_NOT_FOUND")
        start_time = payload.get("startTime", rule.start_time)
        end_time = payload.get("endTime", rule.end_time)
        self._validate_times(start_time, end_time)
        if "weekday" in payload:
            rule.weekday = payload["weekday"]
        if "startTime" in payload:
            rule.start_time = payload["startTime"]
        if "endTime" in payload:
            rule.end_time = payload["endTime"]
        if "validFrom" in payload:
            rule.valid_from = payload["validFrom"]
        if "validTo" in payload:
            rule.valid_to = payload["validTo"]
        if "isActive" in payload:
            rule.is_active = payload["isActive"]
        db.session.commit()
        return rule

    # Usuwa regułę dostępności terapeuty.
    def delete_rule(self, rule_id):
        rule = AvailabilityRule.query.get(rule_id)
        if not rule:
            raise NotFoundError("Reguła grafiku nie istnieje.", code="AVAILABILITY_RULE_NOT_FOUND")
        db.session.delete(rule)
        db.session.commit()

    # Pobiera wyjątki dostępności terapeuty.
    def list_exceptions(self, therapist_id):
        self._ensure_therapist(therapist_id)
        return AvailabilityException.query.filter_by(therapist_id=therapist_id).order_by(AvailabilityException.start_at.asc()).all()

    # Tworzy wyjątek dostępności, np. blokadę terminu albo dodatkową dostępność.
    def create_exception(self, therapist_id, payload: dict):
        self._ensure_therapist(therapist_id)
        if payload["startAt"] >= payload["endAt"]:
            raise ValidationError("Zakres wyjątku jest nieprawidłowy.")
        exception = AvailabilityException(
            therapist_id=therapist_id,
            type=payload["type"],
            start_at=payload["startAt"],
            end_at=payload["endAt"],
            reason=payload.get("reason"),
        )
        db.session.add(exception)
        db.session.commit()
        return exception

    # Sprawdza, czy godzina rozpoczęcia jest wcześniejsza niż godzina zakończenia.
    @staticmethod
    def _validate_times(start_time, end_time):
        if start_time >= end_time:
            raise ValidationError("Godzina rozpoczęcia musi być wcześniejsza niż godzina zakończenia.")
