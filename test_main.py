from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200

def test_register():
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200

def test_duplicate_register():
    client.post(
        "/register",
        json={
            "username": "duplicate",
            "password": "test123"
        }
    )
    response = client.post(
        "/register",
        json={
            "username": "duplicate",
            "password": "test123"
        }
    )
    assert response.status_code == 400
