from app.extensions import db
from app.models import Appointment, ConsultationSummary
from app.utils.enums import AppointmentStatus
from app.utils.errors import ForbiddenError, NotFoundError


# Warstwa logiki biznesowej obsługująca podsumowania konsultacji.
class ConsultationService:
    # Tworzy albo aktualizuje podsumowanie konsultacji dla zakończonej wizyty.
    def upsert_summary(self, appointment_id, current_user, summary_text: str):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise NotFoundError("Wizyta nie istnieje.", code="APPOINTMENT_NOT_FOUND")
        if appointment.status not in [AppointmentStatus.COMPLETED.value, AppointmentStatus.NO_SHOW.value]:
            raise ForbiddenError("Opis konsultacji można dodać dopiero po zakończeniu wizyty.")

        summary = appointment.consultation_summary
        if summary is None:
            summary = ConsultationSummary(
                appointment_id=appointment.id,
                created_by_user_id=current_user.id,
                summary_text=summary_text,
            )
            db.session.add(summary)
        else:
            summary.summary_text = summary_text
        db.session.commit()
        return summary

    # Pobiera listę wizyt przypisanych do wskazanego pacjenta.
    def list_for_patient(self, patient_user_id):
        return (
            Appointment.query.filter_by(patient_user_id=patient_user_id, status=AppointmentStatus.COMPLETED.value)
            .order_by(Appointment.start_at.desc())
            .all()
        )
