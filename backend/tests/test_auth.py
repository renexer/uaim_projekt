def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new.patient@example.com",
            "password": "Password123!",
            "firstName": "Nowy",
            "lastName": "Pacjent",
            "phone": "+48123123123",
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["data"]["email"] == "new.patient@example.com"
    assert body["data"]["roles"] == ["PATIENT"]


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "jan@example.com", "password": "Password123!"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert "accessToken" in body["data"]
    assert "refreshToken" in body["data"]
    assert body["data"]["user"]["email"] == "jan@example.com"


def test_me_requires_auth(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_refresh_success(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "jan@example.com", "password": "Password123!"},
    ).get_json()["data"]
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {login['refreshToken']}"},
    )
    assert response.status_code == 200
    assert "accessToken" in response.get_json()["data"]
