from datetime import datetime, timezone

from app.extensions import db
from app.models import Appointment
from app.services.consultation_service import ConsultationService
from app.utils.enums import AppointmentStatus
from app.utils.errors import ForbiddenError, NotFoundError


class StaffAppointmentService:
    def __init__(self, consultation_service: ConsultationService | None = None):
        self.consultation_service = consultation_service or ConsultationService()

    def list_appointments(self, filters: dict, current_user):
        query = Appointment.query
        if self._is_therapist_only(current_user):
            therapist_profile = current_user.therapist_profile
            if therapist_profile is None:
                raise ForbiddenError("Użytkownik nie ma profilu terapeuty.")
            query = query.filter(Appointment.therapist_id == therapist_profile.id)

        if filters.get("from_"):
            query = query.filter(Appointment.start_at >= filters["from_"])
        if filters.get("to"):
            query = query.filter(Appointment.start_at <= filters["to"])
        if filters.get("therapistId"):
            query = query.filter(Appointment.therapist_id == filters["therapistId"])
        if filters.get("status"):
            query = query.filter(Appointment.status == filters["status"])
        if filters.get("patientEmail"):
            query = query.join(Appointment.patient).filter(Appointment.patient.has(email=filters["patientEmail"].lower()))
        return query.order_by(Appointment.start_at.desc()).all()

    def update_status(self, appointment_id: str, payload: dict, current_user):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise NotFoundError("Wizyta nie istnieje.", code="APPOINTMENT_NOT_FOUND")
        self._ensure_access(appointment, current_user)
        appointment.status = payload["status"]
        if payload["status"] == AppointmentStatus.CANCELLED_BY_CLINIC.value:
            appointment.cancelled_at = datetime.now(timezone.utc)
            appointment.cancelled_by_user_id = current_user.id
            appointment.cancellation_reason = payload.get("cancellationReason")
        db.session.commit()
        return appointment

    def upsert_consultation_summary(self, appointment_id: str, current_user, summary_text: str):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise NotFoundError("Wizyta nie istnieje.", code="APPOINTMENT_NOT_FOUND")
        self._ensure_access(appointment, current_user)
        return self.consultation_service.upsert_summary(appointment_id, current_user, summary_text)

    @staticmethod
    def _is_therapist_only(current_user):
        role_names = {role.name for role in current_user.roles}
        return "THERAPIST" in role_names and "ADMIN" not in role_names

    def _ensure_access(self, appointment, current_user):
        if self._is_therapist_only(current_user):
            therapist_profile = current_user.therapist_profile
            if therapist_profile is None or appointment.therapist_id != therapist_profile.id:
                raise ForbiddenError("Brak dostępu do tej wizyty.")
