import io
import re
import pytest
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

# IMPORTACIONES DE LA APLICACIÓN
# Se asume que el código de las rutas se encuentra en, por ejemplo, "src/ai/routes.py"
from src.ai.router import ai_router, StateGraph
from src.database import get_db
from src.models import Users, Messages
import src.ai.crud as crud
import src.ai.utils.detect_language as detect_mod

# =============================================================================
# Clases "fake" para simular el comportamiento de la base de datos y algunas
# funcionalidades de SQLAlchemy, de modo que las pruebas sean aisladas.
# =============================================================================

# Se crea un "fake" para simular columnas de un modelo (para que la comparación
# Users.email == email retorne una función que se pueda aplicar a cada instancia).


class FakeColumn:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        # Devuelve una función que, dada una instancia, verifica si el atributo
        # coincide con el valor esperado.
        return lambda instance: getattr(instance, self.name) == other

# Simulamos un modelo mínimo para el usuario (similar a lo que se espera en Users)


class FakeUser:
    email = FakeColumn('email')
    private_id = FakeColumn('private_id')

    def __init__(self, email=None, private_id=None):
        self.email = email
        self.private_id = private_id
        self.id = None  # Se asignará al agregarse a la sesión

# Simulamos un modelo mínimo para un mensaje


class FakeMessage:
    def __init__(self, user_id, message, created_at=None):
        self.user_id = user_id
        self.message = message
        self.created_at = created_at or datetime.now()

# Una clase fake para simular el resultado de una consulta (query) de SQLAlchemy.


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

# Una sesión fake para la base de datos que almacena usuarios y mensajes en memoria.


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
        # Si es un usuario, se asigna un id y se almacena
        if hasattr(obj, "email"):
            if not getattr(obj, "id", None):
                obj.id = self._id_counter
                self._id_counter += 1
            self.users.append(obj)
        # Si es un mensaje, se almacena en la lista de mensajes
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
    # Sobrescribimos la dependencia get_db para que retorne nuestra sesión fake
    app.dependency_overrides[get_db] = lambda: db
    yield db
    # Al finalizar, se puede restablecer la dependencia (opcional)
    app.dependency_overrides[get_db] = lambda: FakeDBSession()

# =============================================================================
# Sobrescritura de funciones externas para que las pruebas sean predecibles
# =============================================================================

# Para el endpoint /get_excel/ se sobrescribe generate_excel para que retorne
# un buffer de BytesIO con contenido simulado.


def fake_generate_excel(user_email, db):
    return io.BytesIO(b"Contenido de Excel simulado")


crud.generate_excel = fake_generate_excel

# Para el endpoint ask_agent se sobrescribe el método compile de StateGraph para
# que retorne un objeto con un método stream que simula una respuesta de la IA.


class DummyMessage:
    def __init__(self, content):
        self.content = content


class FakeStreamApp:
    def stream(self, payload, config, stream_mode):
        # Se retorna un único evento con un mensaje simulado
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


def test_google_login(fake_db):
    payload = {"email": "test@example.com"}
    response = client.post("/google_login/", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "User logged in successfully"

# --- 2. Pruebas para el endpoint GET /bot_conversation/{user_email} ---

# Caso cuando el usuario no existe (se espera error 404)


def test_bot_conversation_no_user(fake_db):
    response = client.get("/bot_conversation/nonexistent@example.com")
    assert response.status_code == 404

# Caso con usuario existente y mensajes previos


def test_bot_conversation_with_messages(fake_db):
    # Creamos un usuario fake y lo agregamos a la sesión
    user = FakeUser(email="test@example.com")
    fake_db.add(user)
    # Agregamos dos mensajes simulados (por ejemplo, uno de "human" y otro de "ai")
    message1 = FakeMessage(user_id=user.id, message={
                           "owner": "human", "message": "Hola", "lang": "en"})
    message2 = FakeMessage(user_id=user.id, message={
                           "owner": "ai", "message": "Hola, ¿en qué puedo ayudarte?", "lang": "en"})
    fake_db.messages.extend([message1, message2])
    response = client.get("/bot_conversation/test@example.com")
    assert response.status_code == 200
    data = response.json()
    # Se verifica que la respuesta contenga la lista de mensajes
    assert "conversation" in data
    assert data["conversation"] == [message1.message, message2.message]

# --- 3. Pruebas para el endpoint GET /get_excel/ ---

# Caso cuando el usuario no existe (se espera error 404)


def test_get_excel_no_user(fake_db):
    response = client.get("/get_excel/?user_email=nonexistent@example.com")
    assert response.status_code == 404

# Caso con usuario existente: se verifica que se retorna el Excel simulado


def test_get_excel_success(fake_db):
    user = FakeUser(email="test@example.com")
    fake_db.add(user)
    response = client.get("/get_excel/?user_email=test@example.com")
    assert response.status_code == 200
    # Se comprueba que el header Content-Disposition incluya el nombre del archivo
    assert "attachment;filename=products.xlsx" in response.headers.get(
        "content-disposition", "")
    # Se verifica que el contenido del archivo incluya el texto simulado
    assert b"Contenido de Excel simulado" in response.content

# --- 4. Prueba para el endpoint POST /importation-bot/ (ask_agent) ---


def test_ask_agent(fake_db):
    payload = {
        "prompt": "Test prompt",
        "user_email": "test@example.com",
        "user_id": None
    }
    response = client.post("/importation-bot/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Se verifica que la respuesta incluya los campos "message", "noms" y "lang"
    assert "message" in data
    assert "noms" in data
    assert "lang" in data
    # Se comprueba que el mensaje simulado de la IA incluya el código NOM esperado
    assert re.search(r"NOM-\d{3}-[A-Z]+-\d{4}", data["message"])
