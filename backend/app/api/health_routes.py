from flask import Blueprint

from app.api.helpers import success


health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


@health_bp.get("/health")
def health():
    return success({"status": "ok"})
