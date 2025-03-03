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


# =============================================================================
# Configuración de la aplicación y sobreescritura de dependencias
# =============================================================================


# Se crea la aplicación FastAPI e incluye el router de las rutas de AI.
app = FastAPI()
app.include_router(ai_router)
client = TestClient(app)


# Fixture que provee una sesión fake para la base de datos


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

# Se sobrescribe save_data_into_db para que durante las pruebas no realice acción alguna.
crud.save_data_into_db = lambda user_email, data, db: None

# Para simplificar, se fuerza que detect_language siempre retorne "en"
detect_mod.detect_language = lambda text: "en"

# =============================================================================
# PRUEBAS UNITARIAS PARA CADA ENDPOINT
# =============================================================================

# --- 1. Prueba para el endpoint POST /google_login/ ---

# Tests adicionales para casos de borde y escenarios no cubiertos previamente

def test_google_login_multiple(fake_db):
    """
    Prueba para el endpoint /google_login/ con múltiples usuarios.
    
    - Se envían payloads con distintos emails.
    - Se verifica que se crean usuarios distintos en la base de datos.
    
    Herramienta/Framework: Pytest, FastAPI TestClient
    """
    emails = ["user1@example.com", "user2@example.com", "user3@example.com"]
    for email in emails:
        response = client.post("/google_login/", json={"email": email})
        assert response.status_code == 200
    # Se espera que la cantidad de usuarios sea igual al número de emails enviados.
    assert len(fake_db.users) == len(emails)


def test_bot_conversation_ordered(fake_db):
    """
    Prueba para el endpoint /bot_conversation/{user_email} verificando el orden de los mensajes.
    
    - Se crea un usuario con mensajes agregados con marcas de tiempo desordenadas.
    - Se invoca el endpoint y se verifica que la lista de mensajes se retorna en orden ascendente de 'created_at'.
    
    Herramienta/Framework: Pytest, FastAPI TestClient
    """
    user = FakeUser(email="ordered@example.com")
    fake_db.add(user)
    
    # Se crean mensajes con tiempos desordenados
    from datetime import datetime, timedelta
    now = datetime.now()
    message1 = FakeMessage(
        user_id=user.id, 
        message={"owner": "human", "message": "Primero", "lang": "en"}, 
        created_at=now + timedelta(minutes=5)
    )
    message2 = FakeMessage(
        user_id=user.id, 
        message={"owner": "ai", "message": "Segundo", "lang": "en"}, 
        created_at=now
    )
    message3 = FakeMessage(
        user_id=user.id, 
        message={"owner": "human", "message": "Tercero", "lang": "en"}, 
        created_at=now + timedelta(minutes=10)
    )
    fake_db.messages.extend([message1, message2, message3])
    
    response = client.get("/bot_conversation/ordered@example.com")
    assert response.status_code == 200
    data = response.json()
    # Se espera que los mensajes se ordenen de forma ascendente por 'created_at':
    # El orden esperado es: message2, message1, message3.
    expected_order = [message2.message, message1.message, message3.message]
    assert data["conversation"] == expected_order


def test_ask_agent_success(fake_db):
    """
    Prueba para el endpoint /importation-bot/ con payload válido y usuario existente.
    
    - Se crea previamente un usuario con un email determinado.
    - Se envía un payload con un prompt y el user_email correspondiente.
    - Se verifica que la respuesta sea exitosa (HTTP 200) y que incluya los campos "message", "noms" y "lang".
    
    Herramienta/Framework: Pytest, FastAPI TestClient
    """
    # Se crea un usuario existente
    user = FakeUser(email="existing_agent@example.com")
    fake_db.add(user)
    
    payload = {
        "prompt": "Test prompt for agent",
        "user_email": "existing_agent@example.com",
        "user_id": None
    }
    response = client.post("/importation-bot/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "noms" in data
    assert "lang" in data


