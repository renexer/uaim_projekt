from datetime import datetime, timedelta, timezone


def test_get_availability_for_service_and_therapist(client):
    services = client.get("/api/v1/services").get_json()["data"]
    consultation_id = next(item["id"] for item in services if item["code"] == "CONSULT_50")
    therapists = client.get(f"/api/v1/services/{consultation_id}/therapists").get_json()["data"]
    therapist_id = therapists[0]["id"]

    start = datetime.now(timezone.utc)
    end = start + timedelta(days=14)

    response = client.get(
        "/api/v1/availability",
        query_string={
            "serviceId": consultation_id,
            "therapistId": therapist_id,
            "from": start.isoformat(),
            "to": end.isoformat(),
        },
    )

    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["service"]["id"] == consultation_id
    assert len(body["items"]) == 1
    assert isinstance(body["items"][0]["slots"], list)
