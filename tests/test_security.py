"""
Tests de funciones puras de seguridad (NO usan base de datos).
"""
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_hash_no_guarda_texto_plano():
    hashed = hash_password("admin123")
    # El hash NO debe ser igual a la contraseña original
    assert hashed != "admin123"
    # Debe empezar con el prefijo de bcrypt
    assert hashed.startswith("$2")


def test_verify_password():
    hashed = hash_password("admin123")
    # Con la contraseña correcta → True
    assert verify_password("admin123", hashed) is True
    # Con una incorrecta → False
    assert verify_password("mala", hashed) is False


def test_token_roundtrip():
    token = create_access_token({"sub": "ana@example.com"})
    payload = decode_access_token(token)
    # El claim "sub" debe conservarse tras codificar/decodificar
    assert payload["sub"] == "ana@example.com"
