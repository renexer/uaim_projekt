from flask import Blueprint

from app.api.helpers import success


# Blueprint techniczny używany do sprawdzania, czy backend działa poprawnie.
health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


@health_bp.get("/health")
# Endpoint healthcheck zwraca prosty status aplikacji dla Dockera i monitoringu.
def health():
    return success({"status": "ok"})