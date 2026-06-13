from flask import Blueprint, current_app, request

from app.api.helpers import load_or_400, success
from app.schemas import AvailabilityQuerySchema, SlotSchema, TherapistPublicSchema
from app.services.availability_service import AvailabilityService


# Blueprint publiczny do pobierania dostępnych terminów wizyt.
availability_bp = Blueprint("availability", __name__, url_prefix="/api/v1")
# Schemat listy slotów formatuje dostępne terminy do odpowiedzi JSON.
slot_schema = SlotSchema(many=True)
# Schemat terapeuty dołącza informacje o specjaliście przy zwracaniu dostępności.
therapist_schema = TherapistPublicSchema()


@availability_bp.get("/availability")
# Endpoint oblicza dostępne sloty dla usługi, terapeuty i zakresu dat.
def get_availability():
    payload = load_or_400(AvailabilityQuerySchema(), request.args.to_dict())
    service = AvailabilityService(app_timezone=current_app.config["APP_TIMEZONE"])
    result = service.get_availability(
        service_id=payload["serviceId"],
        therapist_id=payload.get("therapistId"),
        from_dt=payload["from_"],
        to_dt=payload["to"],
    )
    return success({
        "service": {
            "id": str(result["service"].id),
            "name": result["service"].name,
            "durationMinutes": result["service"].duration_minutes,
        },
        "range": {
            "from": result["range"]["from"].isoformat(),
            "to": result["range"]["to"].isoformat(),
        },
        "items": [
            {
                "therapist": therapist_schema.dump(item["therapist"]),
                "slots": slot_schema.dump(item["slots"]),
            }
            for item in result["items"]
        ],
    })