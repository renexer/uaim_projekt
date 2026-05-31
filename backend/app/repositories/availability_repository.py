from app.models import AvailabilityException, AvailabilityRule, Appointment
from app.repositories.base_repository import BaseRepository


class AvailabilityRepository(BaseRepository):
    model = AvailabilityRule

    def get_rules_for_therapist(self, therapist_id):
        return AvailabilityRule.query.filter_by(therapist_id=therapist_id, is_active=True).all()

    def get_exceptions_in_range(self, therapist_id, start_at, end_at):
        return (
            AvailabilityException.query.filter(
                AvailabilityException.therapist_id == therapist_id,
                AvailabilityException.start_at < end_at,
                AvailabilityException.end_at > start_at,
            )
            .order_by(AvailabilityException.start_at.asc())
            .all()
        )

    def get_blocking_appointments(self, therapist_id, start_at, end_at):
        return (
            Appointment.query.filter(
                Appointment.therapist_id == therapist_id,
                Appointment.status.in_(["BOOKED", "COMPLETED", "NO_SHOW"]),
                Appointment.start_at < end_at,
                Appointment.end_at > start_at,
            )
            .all()
        )
