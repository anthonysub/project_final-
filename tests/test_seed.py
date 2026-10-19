"""
Test de idempotencia del seed.

El seed ya corrió en conftest.py (fixture setup_database). Este test lo
re-ejecuta y verifica que NO duplique registros.
"""
from app.db.seed import seed_catalogos
from app.models.roles import Rol


def test_seed_no_duplica(db):
    # Contar roles ANTES de re-ejecutar el seed
    antes = db.query(Rol).count()

    # Re-ejecutar el seed de catálogos (es idempotente)
    seed_catalogos(db)

    # Contar roles DESPUÉS
    despues = db.query(Rol).count()

    # La cantidad no debe cambiar: el seed no duplica
    assert antes == despues
