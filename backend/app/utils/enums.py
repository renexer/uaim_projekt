from enum import Enum


class RoleName(str, Enum):
    PATIENT = "PATIENT"
    THERAPIST = "THERAPIST"
    ADMIN = "ADMIN"


class AvailabilityExceptionType(str, Enum):
    UNAVAILABLE = "UNAVAILABLE"
    EXTRA_AVAILABLE = "EXTRA_AVAILABLE"


class AppointmentStatus(str, Enum):
    BOOKED = "BOOKED"
    CANCELLED_BY_PATIENT = "CANCELLED_BY_PATIENT"
    CANCELLED_BY_CLINIC = "CANCELLED_BY_CLINIC"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class ReviewStatus(str, Enum):
    PUBLISHED = "PUBLISHED"
    HIDDEN = "HIDDEN"


class EmailNotificationType(str, Enum):
    APPOINTMENT_BOOKED = "APPOINTMENT_BOOKED"
    APPOINTMENT_CANCELLED = "APPOINTMENT_CANCELLED"
    APPOINTMENT_REMINDER_24H = "APPOINTMENT_REMINDER_24H"


class EmailNotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
