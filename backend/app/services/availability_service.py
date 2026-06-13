from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.models import TherapistService
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.therapist_repository import TherapistRepository
from app.utils.datetime_utils import combine_local, daterange, round_up_to_slot
from app.utils.errors import ConflictError, NotFoundError, ValidationError


# Prosty obiekt danych opisujący pojedynczy dostępny termin wizyty.
@dataclass
class Slot:
    start_at: datetime
    end_at: datetime


# Warstwa logiki biznesowej wyliczająca dostępne sloty wizyt na podstawie reguł, wyjątków i rezerwacji.
class AvailabilityService:
    SLOT_MINUTES = 15

    # Konstruktor inicjalizuje zależności potrzebne do działania klasy.
    def __init__(
        self,
        availability_repository: AvailabilityRepository | None = None,
        service_repository: ServiceRepository | None = None,
        therapist_repository: TherapistRepository | None = None,
        app_timezone: str = "Europe/Warsaw",
    ):
        self.availability_repository = availability_repository or AvailabilityRepository()
        self.service_repository = service_repository or ServiceRepository()
        self.therapist_repository = therapist_repository or TherapistRepository()
        self.app_timezone = app_timezone

    # Wylicza dostępne sloty dla terapeuty i usługi w wybranym zakresie dat.
    def get_availability(self, service_id, from_dt, to_dt, therapist_id=None):
        service = self.service_repository.get_active(service_id)
        if not service:
            raise NotFoundError("Usługa nie istnieje.", code="SERVICE_NOT_FOUND")
        if from_dt >= to_dt:
            raise ValidationError("Zakres dat jest nieprawidłowy.")

        if therapist_id:
            therapist = self.therapist_repository.get(therapist_id)
            if not therapist or not therapist.is_active:
                raise NotFoundError("Terapeuta nie istnieje.", code="THERAPIST_NOT_FOUND")
            therapists = [therapist]
        else:
            therapists = self.therapist_repository.list_for_service(service_id)

        result = []
        for therapist in therapists:
            link = TherapistService.query.filter_by(
                therapist_id=therapist.id, service_id=service_id, is_active=True
            ).first()
            if not link:
                if therapist_id:
                    raise ConflictError(
                        "Terapeuta nie realizuje wybranej usługi.",
                        code="THERAPIST_NOT_ASSIGNED_TO_SERVICE",
                    )
                continue
            duration_minutes = link.duration_override_minutes or service.duration_minutes
            slots = self._build_slots_for_therapist(therapist.id, duration_minutes, from_dt, to_dt)
            result.append({"therapist": therapist, "slots": slots})
        return {"service": service, "range": {"from": from_dt, "to": to_dt}, "items": result}

    # Sprawdza, czy wskazany slot rzeczywiście istnieje w aktualnie wyliczonej dostępności.
    def slot_exists(self, service_id, therapist_id, start_at):
        service = self.service_repository.get_active(service_id)
        if not service:
            raise NotFoundError("Usługa nie istnieje.", code="SERVICE_NOT_FOUND")

        therapist = self.therapist_repository.get(therapist_id)
        if not therapist or not therapist.is_active:
            raise NotFoundError("Terapeuta nie istnieje.", code="THERAPIST_NOT_FOUND")

        link = TherapistService.query.filter_by(
            therapist_id=therapist.id,
            service_id=service.id,
            is_active=True,
        ).first()
        if not link:
            raise ConflictError(
                "Terapeuta nie realizuje wybranej usługi.",
                code="THERAPIST_NOT_ASSIGNED_TO_SERVICE",
            )

        duration_minutes = link.duration_override_minutes or service.duration_minutes
        end_at = start_at + timedelta(minutes=duration_minutes)
        slots = self._build_slots_for_therapist(therapist.id, duration_minutes, start_at, end_at)
        return any(slot.start_at == start_at and slot.end_at == end_at for slot in slots)

    # Metoda pomocnicza budująca listę slotów na podstawie reguł dostępności.
    def _build_slots_for_therapist(self, therapist_id, duration_minutes: int, from_dt, to_dt):
        rules = self.availability_repository.get_rules_for_therapist(therapist_id)
        exceptions = self.availability_repository.get_exceptions_in_range(therapist_id, from_dt, to_dt)
        blocks = self.availability_repository.get_blocking_appointments(therapist_id, from_dt, to_dt)

        slots = []
        for day in daterange(from_dt.date(), to_dt.date()):
            weekday = day.isoweekday()
            day_rules = [
                rule
                for rule in rules
                if rule.weekday == weekday and rule.valid_from <= day and (rule.valid_to is None or day <= rule.valid_to)
            ]
            for rule in day_rules:
                window_start = combine_local(day, rule.start_time, self.app_timezone)
                window_end = combine_local(day, rule.end_time, self.app_timezone)
                cursor = round_up_to_slot(max(window_start, from_dt), self.SLOT_MINUTES)
                while cursor + timedelta(minutes=duration_minutes) <= min(window_end, to_dt):
                    slot_end = cursor + timedelta(minutes=duration_minutes)
                    if not self._is_blocked(cursor, slot_end, exceptions, blocks):
                        slots.append(Slot(start_at=cursor, end_at=slot_end))
                    cursor += timedelta(minutes=self.SLOT_MINUTES)
        return slots

    # Metoda pomocnicza sprawdzająca, czy slot jest zablokowany przez wyjątek lub wizytę.
    @staticmethod
    def _is_blocked(start_at, end_at, exceptions, appointments):
        # Usuwamy strefę czasową przed porównaniem, aby uniknąć błędu na SQLite/Windows
        start_at = start_at.replace(tzinfo=None)
        end_at = end_at.replace(tzinfo=None)
        
        for item in exceptions:
            item_start = item.start_at.replace(tzinfo=None)
            item_end = item.end_at.replace(tzinfo=None)
            if item.type == "UNAVAILABLE" and item_start < end_at and item_end > start_at:
                return True
        for item in appointments:
            item_start = item.start_at.replace(tzinfo=None)
            item_end = item.end_at.replace(tzinfo=None)
            if item_start < end_at and item_end > start_at:
                return True
        return False
