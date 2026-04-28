from app.extensions import db
from app.models import Role, Service
from app.utils.enums import RoleName


def seed_command():
    for role_name in [role.value for role in RoleName]:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))

    demo_services = [
        {
            "code": "CONSULT_50",
            "name": "Konsultacja psychologiczna",
            "description": "Pierwsza konsultacja w gabinecie.",
            "duration_minutes": 50,
            "base_price": 180,
        },
        {
            "code": "THERAPY_50",
            "name": "Sesja terapeutyczna",
            "description": "Regularna sesja terapeutyczna.",
            "duration_minutes": 50,
            "base_price": 200,
        },
    ]

    for item in demo_services:
        if not Service.query.filter_by(code=item["code"]).first():
            db.session.add(Service(**item))

    db.session.commit()
    print("Seed zakończony.")
