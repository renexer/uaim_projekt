from app.api.admin_availability_routes import admin_availability_bp
from app.api.admin_services_routes import admin_services_bp
from app.api.admin_therapists_routes import admin_therapists_bp
from app.api.appointments_routes import appointments_bp
from app.api.auth_routes import auth_bp
from app.api.availability_routes import availability_bp
from app.api.consultations_routes import consultations_bp
from app.api.health_routes import health_bp
from app.api.reviews_routes import reviews_bp
from app.api.services_routes import services_bp
from app.api.staff_appointments_routes import staff_appointments_bp
from app.api.therapists_routes import therapists_bp

all_blueprints = [
    health_bp,
    auth_bp,
    services_bp,
    therapists_bp,
    availability_bp,
    appointments_bp,
    consultations_bp,
    reviews_bp,
    admin_services_bp,
    admin_therapists_bp,
    admin_availability_bp,
    staff_appointments_bp,
]
