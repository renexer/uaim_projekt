from datetime import datetime, timedelta, timezone


def test_review_requires_completed_appointment(client, auth_headers):
    services = client.get("/api/v1/services").get_json()["data"]
    consultation_id = next(item["id"] for item in services if item["code"] == "CONSULT_50")
    therapists = client.get(f"/api/v1/services/{consultation_id}/therapists").get_json()["data"]
    therapist_id = therapists[0]["id"]
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=21)
    availability = client.get(
        "/api/v1/availability",
        query_string={"serviceId": consultation_id, "therapistId": therapist_id, "from": start.isoformat(), "to": end.isoformat()},
    ).get_json()["data"]
    slot = availability["items"][0]["slots"][0]["startAt"]
    appointment = client.post(
        "/api/v1/appointments",
        json={"serviceId": consultation_id, "therapistId": therapist_id, "startAt": slot},
        headers=auth_headers,
    ).get_json()["data"]
    response = client.post(
        f"/api/v1/appointments/{appointment['id']}/review",
        json={"rating": 5, "comment": "Super"},
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_admin_can_create_service(client, admin_headers):
    response = client.post(
        "/api/v1/admin/services",
        json={
            "code": "CONSULT_80",
            "name": "Konsultacja 80 min",
            "description": "Dłuższa konsultacja.",
            "durationMinutes": 80,
            "basePrice": "300.00",
            "currency": "PLN",
            "isActive": True,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    assert response.get_json()["data"]["code"] == "CONSULT_80"


def test_staff_can_complete_appointment_and_add_summary(client, therapist_headers):
    staff_list = client.get("/api/v1/staff/appointments", headers=therapist_headers)
    assert staff_list.status_code == 200
    appointment_id = staff_list.get_json()["data"][0]["id"]

    status_response = client.patch(
        f"/api/v1/staff/appointments/{appointment_id}/status",
        json={"status": "COMPLETED"},
        headers=therapist_headers,
    )
    assert status_response.status_code == 200

    summary_response = client.put(
        f"/api/v1/staff/appointments/{appointment_id}/consultation-summary",
        json={"summaryText": "Wizyta zakończona i opisana przez terapeutę."},
        headers=therapist_headers,
    )
    assert summary_response.status_code == 200
    assert summary_response.get_json()["data"]["summaryText"]
