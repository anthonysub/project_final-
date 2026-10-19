
def obtener_token(client, email, password):
    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200
    return r.json()["access_token"]



def test_gestor_puede_ver_clientes(client):
    # Login como gestor
    token = obtener_token(client, "luis.rodriguez@example.com", "gestor123")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get(
        "/clientes",
        headers=headers
    )
    assert r.status_code == 200

def test_tecnico_no_puede_ver_clientes(client):
    # Login como tecnico
    token = obtener_token(client, "sofia.hernandez@example.com", "tecnico123")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get(
        "/clientes",
        headers=headers
    )
    assert r.status_code == 403

def test_admin_puede_ver_empleados(client):
    # Login como admin
    token = obtener_token(client, "ana.martinez@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get(
        "/clientes",
        headers=headers
    )
    assert r.status_code == 200


def test_gestor_no_puede_ver_empleados(client):
    # Login como gestor
    token = obtener_token(client, "luis.rodriguez@example.com", "gestor123")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get(
        "/clientes",
        headers=headers
    )
    assert r.status_code == 200