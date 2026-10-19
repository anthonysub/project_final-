def obtener_token(client, email, password):
    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200
    return r.json()["access_token"]



def test_admin_puede_crear_canal(client):
    # Login como admin
    token = obtener_token(client, "ana.martinez@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/canales",
        json={"nombre_canal": "Canal de prueba"},
        headers=headers,
    )
    assert r.status_code == 201


def test_gestor_no_puede_crear_canal(client):
    # Login como gestor
    token = obtener_token(client, "luis.rodriguez@example.com", "gestor123")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/canales",
        json={"nombre_canal": "Canal de prueba"},
        headers=headers,
    )
    assert r.status_code == 403

def test_tecnico_no_puede_crear_canal(client):
    # Login como gestor
    token = obtener_token(client, "sofia.hernandez@example.com", "tecnico123")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/canales",
        json={"nombre_canal": "Canal de prueba"},
        headers=headers,
    )
    assert r.status_code == 403

def test_gestor_puede_ver_canales(client):
    # Login como gestor
    token = obtener_token(client, "luis.rodriguez@example.com", "gestor123")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get(
        "/canales",
        headers=headers
    )
    assert r.status_code == 200

def test_tecnico_puede_ver_canales(client):
    # Login como tecnico
    token = obtener_token(client, "sofia.hernandez@example.com", "tecnico123")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get(
        "/canales",
        headers=headers
    )
    assert r.status_code == 200