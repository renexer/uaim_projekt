from enum import Enum


# Enum definiujący role dostępne w systemie autoryzacji.
class RoleName(str, Enum):
    PATIENT = "PATIENT"
    THERAPIST = "THERAPIST"
    ADMIN = "ADMIN"


# Enum definiujący typy wyjątków dostępności terapeuty.
class AvailabilityExceptionType(str, Enum):
    UNAVAILABLE = "UNAVAILABLE"
    EXTRA_AVAILABLE = "EXTRA_AVAILABLE"


# Enum definiujący możliwe statusy wizyty.
class AppointmentStatus(str, Enum):
    BOOKED = "BOOKED"
    CANCELLED_BY_PATIENT = "CANCELLED_BY_PATIENT"
    CANCELLED_BY_CLINIC = "CANCELLED_BY_CLINIC"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


# Enum definiujący status publikacji opinii.
class ReviewStatus(str, Enum):
    PUBLISHED = "PUBLISHED"
    HIDDEN = "HIDDEN"


# Enum definiujący status przetworzenia powiadomienia e-mail.
class EmailNotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# Enum definiujący typy powiadomień e-mail wysyłanych przez system.
class EmailNotificationType(str, Enum):
    APPOINTMENT_BOOKED = "APPOINTMENT_BOOKED"
    APPOINTMENT_CANCELLED = "APPOINTMENT_CANCELLED"
    APPOINTMENT_REMINDER_24H = "APPOINTMENT_REMINDER_24H"
