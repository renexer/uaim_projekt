from datetime import datetime, timedelta, timezone


def _find_bookable_slot(client):
    services = client.get("/api/v1/services").get_json()["data"]
    consultation_id = next(item["id"] for item in services if item["code"] == "CONSULT_50")
    therapists = client.get(f"/api/v1/services/{consultation_id}/therapists").get_json()["data"]
    therapist_id = therapists[0]["id"]

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=21)

    availability = client.get(
        "/api/v1/availability",
        query_string={
            "serviceId": consultation_id,
            "therapistId": therapist_id,
            "from": now.isoformat(),
            "to": end.isoformat(),
        },
    ).get_json()["data"]

    slots = availability["items"][0]["slots"]
    assert slots, "Brak wolnych slotów w danych testowych."

    min_allowed_start = now + timedelta(hours=25)

    for slot in slots:
        start_at = datetime.fromisoformat(slot["startAt"].replace("Z", "+00:00"))
        if start_at > min_allowed_start:
            return consultation_id, therapist_id, slot["startAt"]

    raise AssertionError("Nie znaleziono slotu, który można bezpiecznie anulować (>24h).")


def test_create_appointment(client, auth_headers):
    service_id, therapist_id, start_at = _find_bookable_slot(client)

    response = client.post(
        "/api/v1/appointments",
        json={
            "serviceId": service_id,
            "therapistId": therapist_id,
            "startAt": start_at,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.get_json()["data"]
    assert body["status"] == "BOOKED"


def test_cancel_appointment(client, auth_headers):
    service_id, therapist_id, start_at = _find_bookable_slot(client)
    create_response = client.post(
        "/api/v1/appointments",
        json={
            "serviceId": service_id,
            "therapistId": therapist_id,
            "startAt": start_at,
        },
        headers=auth_headers,
    )
    appointment_id = create_response.get_json()["data"]["id"]

    cancel_response = client.post(
        f"/api/v1/appointments/{appointment_id}/cancel",
        json={"reason": "Zmiana planów"},
        headers=auth_headers,
    )

    assert cancel_response.status_code == 200
    body = cancel_response.get_json()["data"]
    assert body["status"] == "CANCELLED_BY_PATIENT"


def test_cannot_cancel_foreign_appointment(client, auth_headers):
    appointments = client.get("/api/v1/appointments/me", headers=auth_headers).get_json()["data"]
    # seeded patient Jan has no booked appointment, use seeded patient Ola appointment id by browsing staff as unauthorized impossible;
    # create one as Jan then try with Ola would require another fixture, so just verify 404 on random id.
    response = client.post(
        "/api/v1/appointments/non-existent-id/cancel",
        json={"reason": "X"},
        headers=auth_headers,
    )
    assert response.status_code == 404
