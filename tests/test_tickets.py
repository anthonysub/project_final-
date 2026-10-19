"""
Tests del aislamiento del técnico sobre los tickets.

Los tickets de prueba los inserta conftest.py (función _seed_tickets_test):
  - TK-TEST-001: asignado a Sofía (técnico)
  - TK-TEST-002: sin técnico (id_tecnico=None)
"""
from app.models.empleados import Empleado
from app.models.tickets import Ticket


def obtener_token(client, email, password):
    """Helper: hace login y devuelve el access_token."""
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_tecnico_lista_solo_sus_tickets(client, db):
    """En el listado, el técnico SOLO recibe tickets donde él es el técnico."""
    # ID real de Sofía (no lo hardcodeamos: lo sacamos de la BD de test)
    sofia = db.query(Empleado).filter(Empleado.email == "sofia.hernandez@example.com").first()

    token = obtener_token(client, "sofia.hernandez@example.com", "tecnico123")
    r = client.get("/tickets", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

    tickets = r.json()
    assert isinstance(tickets, list)
    for ticket in tickets:
        # Todos los tickets de la lista deben ser suyos
        assert ticket["id_tecnico"] == sofia.id_empleado


def test_tecnico_no_ve_ticket_ajeno(client, db):
    """Un técnico NO puede ver un ticket que no le fue asignado (403)."""
    # El ticket "ajeno" es el que no tiene técnico (id_tecnico=None)
    ticket_ajeno = db.query(Ticket).filter(Ticket.codigo_ticket == "TK-TEST-002").first()
    assert ticket_ajeno is not None  # la fixture lo creó

    token = obtener_token(client, "sofia.hernandez@example.com", "tecnico123")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get(f"/tickets/{ticket_ajeno.id_ticket}", headers=headers)
    assert r.status_code == 403  # no es suyo → bloqueado


def test_admin_ve_mas_que_tecnico(client):
    """El admin ve TODOS los tickets; el técnico solo los suyos (admin ve más)."""
    token_admin = obtener_token(client, "ana.martinez@example.com", "admin123")
    token_tec = obtener_token(client, "sofia.hernandez@example.com", "tecnico123")

    total_admin = len(client.get("/tickets", headers={"Authorization": f"Bearer {token_admin}"}).json())
    total_tec = len(client.get("/tickets", headers={"Authorization": f"Bearer {token_tec}"}).json())

    assert total_admin > total_tec
