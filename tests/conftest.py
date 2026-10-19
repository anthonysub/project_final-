"""
Configuración de pytest para la app project_final.

La clave aquí es usar una base de datos SEPARADA (user_db_test) para que
los tests NO toquen los datos reales (user_db). A esto se le llama
"aislamiento de la base de datos".

Cómo funciona:
  1. Creamos un engine hacia user_db_test.
  2. Creamos las tablas (Base.metadata.create_all).
  3. Sembramos datos de ejemplo (seed).
  4. Sobrescribimos get_db para que la app use user_db_test en vez de user_db.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.db.seed import seed_catalogos, seed_clientes, seed_usuarios
from app.models.canales import Canal
from app.models.clientes import Cliente
from app.models.empleados import Empleado
from app.models.estado_ticket import EstadoTicket
from app.models.niveles_impacto import NivelImpacto
from app.models.plantilla_formulario import PlantillaFormulario
from app.models.tickets import Ticket
from app.models.tipos_ticket import TipoTicket
from app.main import app

# ── Conexión a la BD de TEST (NO la real) ──────────────────────────
TEST_DATABASE_URL = "postgresql+psycopg2://postgres:12345678@localhost:5432/user_db_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _seed_tickets_test(db):
    """Inserta tickets de ejemplo en la BD de test (idempotente).

    El seed principal (seed_catalogos/clientes/usuarios) NO crea tickets
    ni plantillas, así que este helper los agrega para que los tests de
    tickets tengan datos sobre los que consultar.

    Crea 2 tickets:
      - TK-TEST-001: asignado a Sofía (técnico) → ella SÍ puede verlo.
      - TK-TEST-002: sin técnico (id_tecnico=None) → ella NO (403).
    """
    # 1) Plantilla: el ticket la exige por FK (id_plantilla NOT NULL)
    plantilla = db.query(PlantillaFormulario).first()
    if plantilla is None:
        plantilla = PlantillaFormulario(
            nombre_plantilla="Plantilla de prueba",
            estructura_preguntas={"p1": "¿Qué ocurrió?"},
        )
        db.add(plantilla)
        db.commit()
        db.refresh(plantilla)

    # 2) Idempotencia: si ya hay tickets, no insertar de nuevo
    if db.query(Ticket).count() > 0:
        return

    # 3) Resolver los IDs por "clave natural" (los IDs los asigna la BD,
    #    así que NO los hardcodeamos: los buscamos por email/nombre)
    cliente = db.query(Cliente).filter(Cliente.email == "juan.perez@example.com").first()
    receptor = db.query(Empleado).filter(Empleado.email == "ana.martinez@example.com").first()
    tecnica = db.query(Empleado).filter(Empleado.email == "sofia.hernandez@example.com").first()
    canal = db.query(Canal).first()
    estado = db.query(EstadoTicket).first()
    tipo = db.query(TipoTicket).first()
    impacto = db.query(NivelImpacto).first()

    tickets = [
        Ticket(
            codigo_ticket="TK-TEST-001",
            id_cliente=cliente.id_cliente,
            id_receptor=receptor.id_empleado,
            id_tecnico=tecnica.id_empleado,  # asignado a Sofía
            id_canal=canal.id_canal,
            id_estado=estado.id_estado,
            id_tipo_ticket=tipo.id_tipo_ticket,
            id_impacto=impacto.id_impacto,
            id_plantilla=plantilla.id_plantilla,
            datos_respuesta={},  # JSONB: dict vacío
        ),
        Ticket(
            codigo_ticket="TK-TEST-002",
            id_cliente=cliente.id_cliente,
            id_receptor=receptor.id_empleado,
            id_tecnico=None,  # sin técnico asignado
            id_canal=canal.id_canal,
            id_estado=estado.id_estado,
            id_tipo_ticket=tipo.id_tipo_ticket,
            id_impacto=impacto.id_impacto,
            id_plantilla=plantilla.id_plantilla,
            datos_respuesta={},
        ),
    ]
    db.add_all(tickets)
    db.commit()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crea tablas y siembra datos UNA sola vez por sesión de tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_catalogos(db)
        seed_clientes(db)
        seed_usuarios(db)
        _seed_tickets_test(db)
    finally:
        db.close()
    yield


@pytest.fixture()
def db():
    """Sesión de BD de test (para consultar datos directamente en los tests)."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    """Cliente HTTP de prueba. Usa la BD de test, no la real."""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Reemplaza la dependencia get_db de FastAPI por la de test
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # Limpia el override al terminar cada test
    app.dependency_overrides.clear()
