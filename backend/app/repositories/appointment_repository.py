from app.models import Appointment
from app.repositories.base_repository import BaseRepository


# Repozytorium skupiające zapytania dotyczące wizyt i konfliktów terminów.
class AppointmentRepository(BaseRepository):
    model = Appointment

    # Pobiera listę wizyt przypisanych do wskazanego pacjenta.
    def list_for_patient(self, patient_user_id, scope: str = "upcoming"):
        query = Appointment.query.filter_by(patient_user_id=patient_user_id)
        if scope == "upcoming":
            query = query.filter(Appointment.status == "BOOKED")
        elif scope == "cancelled":
            query = query.filter(Appointment.status.in_(["CANCELLED_BY_PATIENT", "CANCELLED_BY_CLINIC"]))
        return query.order_by(Appointment.start_at.desc()).all()

    # Pobiera pojedynczą wizytę pacjenta i pilnuje, aby użytkownik miał do niej dostęp.
    def get_patient_appointment(self, appointment_id, patient_user_id):
        return Appointment.query.filter_by(id=appointment_id, patient_user_id=patient_user_id).first()

    # Sprawdza, czy wybrany przedział czasu koliduje z istniejącą wizytą terapeuty.
    def has_overlap(self, therapist_id, start_at, end_at):
        return (
            Appointment.query.filter(
                Appointment.therapist_id == therapist_id,
                Appointment.status.in_(["BOOKED", "COMPLETED", "NO_SHOW"]),
                Appointment.start_at < end_at,
                Appointment.end_at > start_at,
            )
            .first()
            is not None
        )
