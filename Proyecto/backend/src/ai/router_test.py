import io
import re
import pytest
from datetime import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.ai.router import ai_router, StateGraph
from src.database import get_db
import src.ai.crud as crud
import src.ai.utils.detect_language as detect_mod


class FakeColumn:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return lambda instance: getattr(instance, self.name) == other


class FakeUser:
    email = FakeColumn("email")
    private_id = FakeColumn("private_id")

    def __init__(self, email=None, private_id=None):
        self.email = email
        self.private_id = private_id
        self.id = None


class FakeMessage:
    def __init__(self, user_id, message, created_at=None):
        self.user_id = user_id
        self.message = message
        self.created_at = created_at or datetime.now()


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, condition):
        self.items = list(filter(condition, self.items))
        return self

    def order_by(self, key_func):
        self.items = sorted(self.items, key=key_func)
        return self

    def first(self):
        return self.items[0] if self.items else None

    def all(self):
        return self.items


class FakeDBSession:
    def __init__(self):
        self.users = []
        self.messages = []
        self._id_counter = 1

    def query(self, model):
        if model.__name__ == "Users":
            return FakeQuery(self.users)
        elif model.__name__ == "Messages":
            return FakeQuery(self.messages)
        return FakeQuery([])

    def add(self, obj):
        if hasattr(obj, "email"):
            if not getattr(obj, "id", None):
                obj.id = self._id_counter
                self._id_counter += 1
            self.users.append(obj)
        elif hasattr(obj, "user_id"):
            self.messages.append(obj)

    def commit(self):
        pass

app = FastAPI()
app.include_router(ai_router)
client = TestClient(app)





@pytest.fixture
def fake_db():
    db = FakeDBSession()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides[get_db] = lambda: FakeDBSession()


def fake_generate_excel(user_email, db):
    return io.BytesIO(b"Contenido de Excel simulado")


crud.generate_excel = fake_generate_excel


class DummyMessage:
    def __init__(self, content):
        self.content = content


class FakeStreamApp:
    def stream(self, payload, config, stream_mode):
        yield {"messages": [DummyMessage("Test AI response NOM-001-SCFI-2023 (dummy)")]}


StateGraph.compile = lambda self, checkpointer: FakeStreamApp()


crud.save_data_into_db = lambda user_email, data, db: None


detect_mod.detect_language = lambda text: "en"




def test_google_login():
    payload = {"email": "test@example.com"}
    response = client.post("/google_login/", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "User logged in successfully"


def test_bot_conversation_no_user():
    response = client.get("/bot_conversation/nonexistent@example.com")
    assert response.status_code == 404


def test_get_excel_no_user():
    response = client.get("/get_excel/?user_email=nonexistent@example.com")
    assert response.status_code == 404


def test_ask_agent_invalid_payload():
   
    payload = {
        "prompt": "Test prompt",
        "user_email": None,
        "user_id": None
    }
    response = client.post("/importation-bot/", json=payload)
   
    assert response.status_code == 400


