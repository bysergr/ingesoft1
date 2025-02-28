import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_user_conversation_valid(client):
    user_email = "test@example.com"
    response = client.get(f"/ai/bot_conversation/{user_email}")

    assert response.status_code == 200, "El endpoint debería responder con 200 OK"
    assert "conversation" in response.json(
    ), "La respuesta debería contener la clave 'conversation'"


def test_get_user_conversation_invalid(client):
    user_email = "invalid-email"
    response = client.get(f"/ai/bot_conversation/{user_email}")

    assert response.status_code == 400, "El endpoint debería responder con 400 Bad Request para un email inválido"
