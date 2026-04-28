from datetime import date, datetime, time, timedelta, timezone

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import (
    Appointment,
    AvailabilityRule,
    ConsultationSummary,
    EmailNotification,
    Review,
    Role,
    Service,
    TherapistProfile,
    TherapistService,
    User,
    UserRole,
)
from app.utils.enums import (
    AppointmentStatus,
    EmailNotificationStatus,
    EmailNotificationType,
    ReviewStatus,
    RoleName,
)


def seed_database():
    create_roles()
    users = create_users()
    therapists = create_therapists(users)
    services = create_services()
    create_therapist_services(therapists, services)
    create_availability_rules(therapists)
    create_sample_appointments(users, therapists, services)
    db.session.commit()


def create_roles():
    for role_name in [role.value for role in RoleName]:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))
    db.session.commit()


def assign_role(user, role_name):
    role = Role.query.filter_by(name=role_name).first()
    existing = UserRole.query.filter_by(user_id=user.id, role_id=role.id).first()
    if not existing:
        db.session.add(UserRole(user_id=user.id, role_id=role.id))


def get_or_create_user(email, first_name, last_name, password, phone=None):
    user = User.query.filter_by(email=email).first()
    if user:
        return user

    user = User(
        email=email,
        password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        is_active=True,
        is_email_verified=True,
    )
    db.session.add(user)
    db.session.flush()
    return user


def create_users():
    admin = get_or_create_user(
        "admin@example.com",
        "Admin",
        "Systemu",
        "Admin123!",
        "+48111111111",
    )
    therapist_anna_user = get_or_create_user(
        "anna@example.com",
        "Anna",
        "Nowak",
        "Password123!",
        "+48222222222",
    )
    therapist_piotr_user = get_or_create_user(
        "piotr@example.com",
        "Piotr",
        "Kowalczyk",
        "Password123!",
        "+48333333333",
    )
    patient_jan = get_or_create_user(
        "jan@example.com",
        "Jan",
        "Kowalski",
        "Password123!",
        "+48444444444",
    )
    patient_ola = get_or_create_user(
        "ola@example.com",
        "Ola",
        "Wiśniewska",
        "Password123!",
        "+48555555555",
    )

    assign_role(admin, RoleName.ADMIN.value)
    assign_role(therapist_anna_user, RoleName.THERAPIST.value)
    assign_role(therapist_piotr_user, RoleName.THERAPIST.value)
    assign_role(patient_jan, RoleName.PATIENT.value)
    assign_role(patient_ola, RoleName.PATIENT.value)

    db.session.commit()

    return {
        "admin": admin,
        "therapist_anna_user": therapist_anna_user,
        "therapist_piotr_user": therapist_piotr_user,
        "patient_jan": patient_jan,
        "patient_ola": patient_ola,
    }


def create_therapists(users):
    anna = TherapistProfile.query.filter_by(user_id=users["therapist_anna_user"].id).first()
    if not anna:
        anna = TherapistProfile(
            user_id=users["therapist_anna_user"].id,
            title="Psycholog",
            bio="Specjalizuje się w pracy z osobami dorosłymi i stresem.",
            experience_years=8,
            photo_url=None,
            is_active=True,
            average_rating=5.0,
            reviews_count=1,
        )
        db.session.add(anna)
        db.session.flush()

    piotr = TherapistProfile.query.filter_by(user_id=users["therapist_piotr_user"].id).first()
    if not piotr:
        piotr = TherapistProfile(
            user_id=users["therapist_piotr_user"].id,
            title="Psychoterapeuta",
            bio="Pracuje z młodzieżą i osobami dorosłymi.",
            experience_years=5,
            photo_url=None,
            is_active=True,
            average_rating=0,
            reviews_count=0,
        )
        db.session.add(piotr)
        db.session.flush()

    db.session.commit()
    return {"anna": anna, "piotr": piotr}


def create_services():
    consultation = Service.query.filter_by(code="CONSULT_50").first()
    if not consultation:
        consultation = Service(
            code="CONSULT_50",
            name="Konsultacja psychologiczna",
            description="Pierwsza konsultacja w gabinecie.",
            duration_minutes=50,
            base_price=180.00,
            currency="PLN",
            is_active=True,
        )
        db.session.add(consultation)
        db.session.flush()

    therapy = Service.query.filter_by(code="THERAPY_50").first()
    if not therapy:
        therapy = Service(
            code="THERAPY_50",
            name="Sesja terapeutyczna",
            description="Regularna sesja terapeutyczna.",
            duration_minutes=50,
            base_price=200.00,
            currency="PLN",
            is_active=True,
        )
        db.session.add(therapy)
        db.session.flush()

    db.session.commit()
    return {"consultation": consultation, "therapy": therapy}


def create_therapist_services(therapists, services):
    links = [
        (therapists["anna"].id, services["consultation"].id, 180.00),
        (therapists["anna"].id, services["therapy"].id, 200.00),
        (therapists["piotr"].id, services["therapy"].id, 210.00),
    ]

    for therapist_id, service_id, price in links:
        existing = TherapistService.query.filter_by(
            therapist_id=therapist_id,
            service_id=service_id,
        ).first()
        if not existing:
            db.session.add(
                TherapistService(
                    therapist_id=therapist_id,
                    service_id=service_id,
                    is_active=True,
                    price_override=price,
                    duration_override_minutes=None,
                )
            )
    db.session.commit()


def create_availability_rules(therapists):
    today = date.today()
    rules = [
        {
            "therapist_id": therapists["anna"].id,
            "weekday": 1,
            "start_time": time(9, 0),
            "end_time": time(15, 0),
        },
        {
            "therapist_id": therapists["anna"].id,
            "weekday": 3,
            "start_time": time(10, 0),
            "end_time": time(18, 0),
        },
        {
            "therapist_id": therapists["piotr"].id,
            "weekday": 2,
            "start_time": time(8, 0),
            "end_time": time(14, 0),
        },
        {
            "therapist_id": therapists["piotr"].id,
            "weekday": 4,
            "start_time": time(12, 0),
            "end_time": time(19, 0),
        },
    ]

    for item in rules:
        existing = AvailabilityRule.query.filter_by(
            therapist_id=item["therapist_id"],
            weekday=item["weekday"],
            start_time=item["start_time"],
            end_time=item["end_time"],
        ).first()
        if not existing:
            db.session.add(
                AvailabilityRule(
                    therapist_id=item["therapist_id"],
                    weekday=item["weekday"],
                    start_time=item["start_time"],
                    end_time=item["end_time"],
                    valid_from=today,
                    valid_to=None,
                    is_active=True,
                )
            )
    db.session.commit()


def create_sample_appointments(users, therapists, services):
    completed_start = datetime.now(timezone.utc) - timedelta(days=7, hours=2)
    completed_end = completed_start + timedelta(minutes=50)

    completed = Appointment.query.filter_by(
        patient_user_id=users["patient_jan"].id,
        therapist_id=therapists["anna"].id,
        start_at=completed_start,
    ).first()

    if not completed:
        completed = Appointment(
            patient_user_id=users["patient_jan"].id,
            therapist_id=therapists["anna"].id,
            service_id=services["consultation"].id,
            start_at=completed_start,
            end_at=completed_end,
            status=AppointmentStatus.COMPLETED.value,
            booked_at=completed_start - timedelta(days=5),
            cancellation_deadline_at=completed_start - timedelta(hours=24),
            cancelled_at=None,
            cancelled_by_user_id=None,
            cancellation_reason=None,
            service_name_snapshot=services["consultation"].name,
            service_description_snapshot=services["consultation"].description,
            duration_minutes_snapshot=50,
            price_snapshot=180.00,
            therapist_name_snapshot=users["therapist_anna_user"].full_name(),
            therapist_title_snapshot=therapists["anna"].title,
        )
        db.session.add(completed)
        db.session.flush()

    summary = ConsultationSummary.query.filter_by(appointment_id=completed.id).first()
    if not summary:
        db.session.add(
            ConsultationSummary(
                appointment_id=completed.id,
                created_by_user_id=users["therapist_anna_user"].id,
                summary_text="Konsultacja dotyczyła omówienia trudności związanych ze stresem i zaplanowania dalszej pracy.",
            )
        )

    review = Review.query.filter_by(appointment_id=completed.id).first()
    if not review:
        db.session.add(
            Review(
                appointment_id=completed.id,
                patient_user_id=users["patient_jan"].id,
                therapist_id=therapists["anna"].id,
                rating=5,
                comment="Bardzo spokojna i profesjonalna konsultacja.",
                status=ReviewStatus.PUBLISHED.value,
            )
        )

    booked_start = datetime.now(timezone.utc) + timedelta(days=3)
    booked_end = booked_start + timedelta(minutes=50)

    booked = Appointment.query.filter_by(
        patient_user_id=users["patient_ola"].id,
        therapist_id=therapists["piotr"].id,
        start_at=booked_start,
    ).first()

    if not booked:
        booked = Appointment(
            patient_user_id=users["patient_ola"].id,
            therapist_id=therapists["piotr"].id,
            service_id=services["therapy"].id,
            start_at=booked_start,
            end_at=booked_end,
            status=AppointmentStatus.BOOKED.value,
            booked_at=datetime.now(timezone.utc),
            cancellation_deadline_at=booked_start - timedelta(hours=24),
            cancelled_at=None,
            cancelled_by_user_id=None,
            cancellation_reason=None,
            service_name_snapshot=services["therapy"].name,
            service_description_snapshot=services["therapy"].description,
            duration_minutes_snapshot=50,
            price_snapshot=210.00,
            therapist_name_snapshot=users["therapist_piotr_user"].full_name(),
            therapist_title_snapshot=therapists["piotr"].title,
        )
        db.session.add(booked)
        db.session.flush()

    booking_email = EmailNotification.query.filter_by(
        appointment_id=booked.id,
        type=EmailNotificationType.APPOINTMENT_BOOKED.value,
    ).first()
    if not booking_email:
        db.session.add(
            EmailNotification(
                appointment_id=booked.id,
                recipient_email=users["patient_ola"].email,
                type=EmailNotificationType.APPOINTMENT_BOOKED.value,
                status=EmailNotificationStatus.SENT.value,
                scheduled_at=datetime.now(timezone.utc),
                sent_at=datetime.now(timezone.utc),
                error_message=None,
            )
        )

    reminder_email = EmailNotification.query.filter_by(
        appointment_id=booked.id,
        type=EmailNotificationType.APPOINTMENT_REMINDER_24H.value,
    ).first()
    if not reminder_email:
        db.session.add(
            EmailNotification(
                appointment_id=booked.id,
                recipient_email=users["patient_ola"].email,
                type=EmailNotificationType.APPOINTMENT_REMINDER_24H.value,
                status=EmailNotificationStatus.PENDING.value,
                scheduled_at=booked_start - timedelta(hours=24),
                sent_at=None,
                error_message=None,
            )
        )

    db.session.commit()