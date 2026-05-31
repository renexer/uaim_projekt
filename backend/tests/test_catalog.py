def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json()["data"]["status"] == "ok"


def test_list_services(client):
    response = client.get("/api/v1/services")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["data"]) >= 2
    assert any(item["code"] == "CONSULT_50" for item in body["data"])


def test_get_therapists_for_service(client):
    services = client.get("/api/v1/services").get_json()["data"]
    consultation_id = next(item["id"] for item in services if item["code"] == "CONSULT_50")

    response = client.get(f"/api/v1/services/{consultation_id}/therapists")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["data"]) == 1
    assert body["data"][0]["fullName"] == "Anna Nowak"
