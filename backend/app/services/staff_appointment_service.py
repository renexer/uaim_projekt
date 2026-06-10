from datetime import date

from app.models import Appointment
from app.services.consultation_service import ConsultationService
from app.utils.datetime_utils import to_utc_naive, utc_now_naive
from app.utils.errors import ForbiddenError, NotFoundError


class StaffAppointmentService:
    def __init__(self, consultation_service: ConsultationService | None = None):
        self.consultation_service = consultation_service or ConsultationService()

    def list_appointments(self, filters: dict, current_user):
        query = self._build_query(filters, current_user)
        return query.order_by(Appointment.start_at.desc()).all()

    def dashboard(self, filters: dict, current_user):
        items = self.list_appointments(filters, current_user)
        now = utc_now_naive()
        today = now.date()

        today_items = [item for item in items if to_utc_naive(item.start_at).date() == today]
        upcoming = sorted(
            [item for item in items if to_utc_naive(item.start_at) >= now],
            key=lambda item: to_utc_naive(item.start_at),
        )[:5]

        return {
            "totals": {
                "all": len(items),
                "today": len(today_items),
                "booked": len([item for item in items if item.status == "BOOKED"]),
                "completed": len([item for item in items if item.status == "COMPLETED"]),
                "noShow": len([item for item in items if item.status == "NO_SHOW"]),
            },
            "upcoming": upcoming,
        }

    def update_status(self, appointment_id: str, payload: dict, current_user):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise NotFoundError("Wizyta nie istnieje.", code="APPOINTMENT_NOT_FOUND")
        self._ensure_access(appointment, current_user)

        appointment.status = payload["status"]

        if payload["status"] == "CANCELLED_BY_CLINIC":
            appointment.cancelled_at = utc_now_naive()
            appointment.cancelled_by_user_id = current_user.id
            appointment.cancellation_reason = payload.get("cancellationReason")

        from app.extensions import db

        db.session.commit()
        return appointment

    def upsert_consultation_summary(self, appointment_id: str, current_user, summary_text: str):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise NotFoundError("Wizyta nie istnieje.", code="APPOINTMENT_NOT_FOUND")
        self._ensure_access(appointment, current_user)
        return self.consultation_service.upsert_summary(appointment_id, current_user, summary_text)

    def _build_query(self, filters: dict, current_user):
        query = Appointment.query

        if self._is_therapist_only(current_user):
            therapist_profile = current_user.therapist_profile
            if therapist_profile is None:
                raise ForbiddenError("Użytkownik nie ma profilu terapeuty.")
            query = query.filter(Appointment.therapist_id == therapist_profile.id)

        if filters.get("from_"):
            query = query.filter(Appointment.start_at >= to_utc_naive(filters["from_"]))
        if filters.get("to"):
            query = query.filter(Appointment.start_at <= to_utc_naive(filters["to"]))
        if filters.get("therapistId"):
            query = query.filter(Appointment.therapist_id == filters["therapistId"])
        if filters.get("status"):
            query = query.filter(Appointment.status == filters["status"])
        if filters.get("patientEmail"):
            query = query.join(Appointment.patient).filter(
                Appointment.patient.has(email=filters["patientEmail"].lower())
            )

        return query

    @staticmethod
    def _is_therapist_only(current_user):
        role_names = {role.name for role in current_user.roles}
        return "THERAPIST" in role_names and "ADMIN" not in role_names

    def _ensure_access(self, appointment, current_user):
        if self._is_therapist_only(current_user):
            therapist_profile = current_user.therapist_profile
            if therapist_profile is None or appointment.therapist_id != therapist_profile.id:
                raise ForbiddenError("Brak dostępu do tej wizyty.")