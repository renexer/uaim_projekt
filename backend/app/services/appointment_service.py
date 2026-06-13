from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import Appointment, TherapistProfile, TherapistService
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.service_repository import ServiceRepository
from app.services.availability_service import AvailabilityService
from app.services.notification_service import NotificationService
from app.utils.enums import AppointmentStatus
from app.utils.errors import ConflictError, ForbiddenError, NotFoundError


# Warstwa logiki biznesowej odpowiedzialna za rezerwowanie, anulowanie i odczyt wizyt pacjenta.
class AppointmentService:
    # Konstruktor inicjalizuje zależności potrzebne do działania klasy.
    def __init__(
        self,
        appointment_repository: AppointmentRepository | None = None,
        service_repository: ServiceRepository | None = None,
        notification_service: NotificationService | None = None,
        availability_service: AvailabilityService | None = None,
    ):
        self.appointment_repository = appointment_repository or AppointmentRepository()
        self.service_repository = service_repository or ServiceRepository()
        self.notification_service = notification_service or NotificationService()
        self.availability_service = availability_service or AvailabilityService()

    # Tworzy wizytę pacjenta, waliduje slot, zapisuje snapshot usługi/terapeuty i kolejkuje powiadomienia.
    def create(self, patient, payload: dict):
        service = self.service_repository.get_active(payload["serviceId"])
        therapist = TherapistProfile.query.filter_by(id=payload["therapistId"], is_active=True).first()
        if not service:
            raise NotFoundError("Usługa nie istnieje.", code="SERVICE_NOT_FOUND")
        if not therapist:
            raise NotFoundError("Terapeuta nie istnieje.", code="THERAPIST_NOT_FOUND")

        link = TherapistService.query.filter_by(
            therapist_id=therapist.id, service_id=service.id, is_active=True
        ).first()
        if not link:
            raise ConflictError(
                "Terapeuta nie realizuje wybranej usługi.", code="THERAPIST_NOT_ASSIGNED_TO_SERVICE"
            )

        start_at = payload["startAt"]
        if start_at <= datetime.now(timezone.utc):
            raise ConflictError("Nie można rezerwować wizyty w przeszłości.", code="APPOINTMENT_IN_PAST")

        if not self.availability_service.slot_exists(service.id, therapist.id, start_at):
            raise ConflictError("Wybrany termin nie jest dostępny.", code="APPOINTMENT_SLOT_NOT_AVAILABLE")

        duration = link.duration_override_minutes or service.duration_minutes
        price = link.price_override or service.base_price
        end_at = start_at + timedelta(minutes=duration)

        if self.appointment_repository.has_overlap(therapist.id, start_at, end_at):
            raise ConflictError("Wybrany termin nie jest już dostępny.", code="APPOINTMENT_SLOT_NOT_AVAILABLE")

        appointment = Appointment(
            patient_user_id=patient.id,
            therapist_id=therapist.id,
            service_id=service.id,
            start_at=start_at,
            end_at=end_at,
            status=AppointmentStatus.BOOKED.value,
            booked_at=datetime.now(timezone.utc),
            cancellation_deadline_at=start_at - timedelta(hours=24),
            service_name_snapshot=service.name,
            service_description_snapshot=service.description,
            duration_minutes_snapshot=duration,
            price_snapshot=price,
            therapist_name_snapshot=therapist.user.full_name(),
            therapist_title_snapshot=therapist.title,
        )
        db.session.add(appointment)
        db.session.commit()
        db.session.refresh(appointment)
        self.notification_service.schedule_booking_email(appointment)
        return appointment

    # Anuluje wizytę pacjenta oraz zapisuje informację o anulowaniu.
    def cancel(self, patient, appointment_id, reason=None):
        appointment = self.appointment_repository.get_patient_appointment(appointment_id, patient.id)
        if not appointment:
            raise NotFoundError("Wizyta nie istnieje.", code="APPOINTMENT_NOT_FOUND")
        if appointment.status != AppointmentStatus.BOOKED.value:
            raise ConflictError("Tylko aktywną wizytę można anulować.", code="APPOINTMENT_NOT_CANCELABLE")

        deadline = appointment.cancellation_deadline_at
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) > deadline:
            raise ForbiddenError(
                "Wizytę można anulować najpóźniej 24 godziny przed rozpoczęciem.",
                code="APPOINTMENT_TOO_LATE_TO_CANCEL",
            )

        appointment.status = AppointmentStatus.CANCELLED_BY_PATIENT.value
        appointment.cancelled_at = datetime.now(timezone.utc)
        appointment.cancelled_by_user_id = patient.id
        appointment.cancellation_reason = reason
        db.session.commit()
        self.notification_service.schedule_cancellation_email(appointment)
        return appointment

    # Pobiera listę wizyt przypisanych do wskazanego pacjenta.
    def list_for_patient(self, patient_user_id, scope="upcoming"):
        return self.appointment_repository.list_for_patient(patient_user_id, scope)

    # Pobiera szczegóły wizyty dostępne dla konkretnego pacjenta.
    def get_details_for_patient(self, patient_user_id, appointment_id):
        appointment = self.appointment_repository.get_patient_appointment(appointment_id, patient_user_id)
        if not appointment:
            raise NotFoundError("Wizyta nie istnieje.", code="APPOINTMENT_NOT_FOUND")
        return appointment
