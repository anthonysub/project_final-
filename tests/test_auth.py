"""
Tests del flujo de autenticación (login).

Estos usan el fixture "client" (definido en conftest.py) que simula
peticiones HTTP usando la BD de test.
"""


def test_login_correcto(client):
    r = client.post(
        "/auth/login",
        data={"username": "ana.martinez@example.com", "password": "admin123"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_password_incorrecta(client):
    r = client.post(
        "/auth/login",
        data={"username": "ana.martinez@example.com", "password": "mala"},
    )
    assert r.status_code == 401


def test_me_sin_token(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_tecnico_no_puede_borrar_ticket(client):
    # Login como técnico (Sofía)
    r = client.post(
        "/auth/login",
        data={"username": "sofia.hernandez@example.com", "password": "tecnico123"},
    )
    token = r.json()["access_token"]

    # Un técnico intenta borrar un ticket → debe ser bloqueado con 403
    r2 = client.delete(
        "/tickets/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 403
