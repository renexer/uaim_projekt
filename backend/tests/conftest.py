import pytest

from app import create_app
from app.extensions import db
from app.seed_data import seed_database


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "jan@example.com", "password": "Password123!"},
    )
    payload = response.get_json()["data"]
    return {"Authorization": f"Bearer {payload['accessToken']}"}


@pytest.fixture()
def admin_headers(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Admin123!"},
    )
    payload = response.get_json()["data"]
    return {"Authorization": f"Bearer {payload['accessToken']}"}


@pytest.fixture()
def therapist_headers(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "anna@example.com", "password": "Password123!"},
    )
    payload = response.get_json()["data"]
    return {"Authorization": f"Bearer {payload['accessToken']}"}
