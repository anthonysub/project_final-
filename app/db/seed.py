"""
Script de carga inicial de datos (seed).

Ejecutar:
    python -m app.db.seed

Crea de forma idempotente:
  - Catálogos básicos: roles, canales, estados, impactos, tipos, departamentos, servicios.
  - Clientes de ejemplo (3).
  - Usuarios/empleados de ejemplo (3) con contraseñas en hash bcrypt.

Idempotente: verifica por nombre/email antes de insertar, así puede
correrse varias veces sin duplicar registros.
"""

from app.db.database import SessionLocal
from app.core.security import hash_password

from app.models.roles import Rol
from app.models.canales import Canal
from app.models.estado_ticket import EstadoTicket
from app.models.niveles_impacto import NivelImpacto
from app.models.tipos_ticket import TipoTicket
from app.models.departamentos import Departamento
from app.models.servicios import Servicio
from app.models.clientes import Cliente
from app.models.empleados import Empleado

from app.schemas.rol_dto import RolCreateDTO
from app.schemas.canal_dto import CanalCreateDTO
from app.schemas.estado_ticket_dto import EstadoTicketCreateDTO
from app.schemas.nivel_impacto_dto import NivelImpactoCreateDTO
from app.schemas.tipo_ticket_dto import TipoTicketCreateDTO
from app.schemas.departamento_dto import DepartamentoCreateDTO
from app.schemas.servicio_dto import ServicioCreateDTO
from app.schemas.cliente_dto import ClienteCreateDTO
from app.schemas.empleado_dto import EmpleadoCreateDTO

from app.services.rol_service import rol_service
from app.services.canal_service import canal_service
from app.services.estado_ticket_service import estado_ticket_service
from app.services.nivel_impacto_service import nivel_impacto_service
from app.services.tipo_ticket_service import tipo_ticket_service
from app.services.departament_service import departamento_service
from app.services.servicio_service import servicio_service
from app.services.cliente_service import cliente_service
from app.services.empleado_service import empleado_service


def _existe(db, modelo, campo, valor) -> bool:
    """Devuelve True si ya existe una fila con ese campo/valor."""
    return db.query(modelo).filter(getattr(modelo, campo) == valor).first() is not None


def seed_catalogos(db) -> int:
    """Siembra los catálogos básicos (idempotente). Devuelve nº de inserts."""
    inserts = 0

    roles = [
        ("Administrador", "Usuario con acceso completo a todas las funcionalidades del sistema."),
        ("Gestor", "Usuario con acceso a la gestión de tickets y clientes."),
        ("Técnico", "Usuario responsable de resolver tickets asignados."),
    ]
    for nombre, descripcion in roles:
        if _existe(db, Rol, "nombre_rol", nombre):
            print(f"  - Rol ya existe: {nombre}")
            continue
        rol_service.create_rol(db, RolCreateDTO(nombre_rol=nombre, descripcion=descripcion))
        inserts += 1
        print(f"  + Rol creado: {nombre}")

    canales = ["Presencial", "Teléfono", "Correo electrónico", "Portal web"]
    for nombre in canales:
        if _existe(db, Canal, "nombre_canal", nombre):
            print(f"  - Canal ya existe: {nombre}")
            continue
        canal_service.create_canal(db, CanalCreateDTO(nombre_canal=nombre))
        inserts += 1
        print(f"  + Canal creado: {nombre}")

    estados = ["Abierto", "En proceso", "Pendiente cliente", "Resuelto", "Cerrado"]
    for nombre in estados:
        if _existe(db, EstadoTicket, "nombre_estado", nombre):
            print(f"  - Estado ya existe: {nombre}")
            continue
        estado_ticket_service.create_estado_ticket(db, EstadoTicketCreateDTO(nombre_estado=nombre))
        inserts += 1
        print(f"  + Estado creado: {nombre}")

    impactos = [("Bajo", 1), ("Medio", 3), ("Alto", 5), ("Crítico", 10)]
    for nombre, peso in impactos:
        if _existe(db, NivelImpacto, "nombre_impacto", nombre):
            print(f"  - Nivel impacto ya existe: {nombre}")
            continue
        nivel_impacto_service.create_nivel_impacto(
            db, NivelImpactoCreateDTO(nombre_impacto=nombre, peso_impacto=peso)
        )
        inserts += 1
        print(f"  + Nivel impacto creado: {nombre}")

    tipos = ["Incidencia", "Consulta", "Reclamo", "Solicitud de servicio"]
    for nombre in tipos:
        if _existe(db, TipoTicket, "nombre_tipo_ticket", nombre):
            print(f"  - Tipo ticket ya existe: {nombre}")
            continue
        tipo_ticket_service.create_tipo_ticket(db, TipoTicketCreateDTO(nombre_tipo_ticket=nombre))
        inserts += 1
        print(f"  + Tipo ticket creado: {nombre}")

    departamentos = [
        "Alta Verapaz", "Baja Verapaz", "Chimaltenango", "Chiquimula",
        "El Progreso", "Escuintla", "Guatemala", "Huehuetenango",
        "Izabal", "Jalapa", "Jutiapa", "Petén",
        "Quetzaltenango", "Quiché", "Retalhuleu", "Sacatepéquez",
        "San Marcos", "Santa Rosa", "Sololá", "Suchitepéquez",
        "Totonicapán", "Zacapa",
    ]
    for nombre in departamentos:
        if _existe(db, Departamento, "nombre_departamento", nombre):
            print(f"  - Departamento ya existe: {nombre}")
            continue
        departamento_service.create_departamento(db, DepartamentoCreateDTO(nombre_departamento=nombre))
        inserts += 1
        print(f"  + Departamento creado: {nombre}")

    servicios = [
        "Internet residencial", "Internet empresarial", "Televisión por cable",
        "Telefonía fija", "Telefonía móvil",
    ]
    for nombre in servicios:
        if _existe(db, Servicio, "nombre_servicio", nombre):
            print(f"  - Servicio ya existe: {nombre}")
            continue
        servicio_service.create_servicio(db, ServicioCreateDTO(nombre_servicio=nombre))
        inserts += 1
        print(f"  + Servicio creado: {nombre}")

    db.commit()
    return inserts


def seed_clientes(db) -> int:
    """Siembra 3 clientes de ejemplo (idempotente por email)."""
    inserts = 0
    clientes = [
        ("Juan", "Pérez", "1234567890101", "555-1234", "juan.perez@example.com"),
        ("María", "Gómez", "1098765432101", "555-5678", "maria.gomez@example.com"),
        ("Carlos", "López", "1111222233303", "555-9012", "carlos.lopez@example.com"),
    ]
    for nombres, apellidos, dpi, celular, email in clientes:
        if _existe(db, Cliente, "email", email):
            print(f"  - Cliente ya existe: {email}")
            continue
        cliente_service.create_cliente(
            db,
            ClienteCreateDTO(nombres=nombres, apellidos=apellidos, dpi=dpi, celular=celular, email=email),
        )
        inserts += 1
        print(f"  + Cliente creado: {nombres} {apellidos}")
    db.commit()
    return inserts


def seed_usuarios(db) -> int:
    """Siembra 3 empleados/usuarios con contraseña bcrypt (idempotente por email)."""
    inserts = 0
    usuarios = [
        ("Ana Martínez", "ana.martinez@example.com", "admin123", "Administrador"),
        ("Luis Rodríguez", "luis.rodriguez@example.com", "gestor123", "Gestor"),
        ("Sofía Hernández", "sofia.hernandez@example.com", "tecnico123", "Técnico"),
    ]
    for nombre, email, password, nombre_rol in usuarios:
        if _existe(db, Empleado, "email", email):
            print(f"  - Empleado ya existe: {email}")
            continue
        rol = db.query(Rol).filter(Rol.nombre_rol == nombre_rol).first()
        if rol is None:
            print(f"  ! No existe el rol '{nombre_rol}', se omite {email}")
            continue
        empleado_service.create_empleado(
            db,
            EmpleadoCreateDTO(
                nombre_empleado=nombre,
                email=email,
                password_bash=hash_password(password),
                activo=True,
                id_rol=rol.id_rol,
            ),
        )
        inserts += 1
        print(f"  + Empleado creado: {nombre} ({nombre_rol})")
    db.commit()
    return inserts


def run() -> None:
    db = SessionLocal()
    try:
        print("🌱 Insertando datos iniciales (seed)...")
        total = 0
        total += seed_catalogos(db)
        total += seed_clientes(db)
        total += seed_usuarios(db)
        print(f"\n✅ Seed completado. {total} registros nuevos insertados.")
        print("\nCredenciales de acceso:")
        print("  Administrador: ana.martinez@example.com / admin123")
        print("  Gestor:        luis.rodriguez@example.com / gestor123")
        print("  Técnico:       sofia.hernandez@example.com / tecnico123")
    except Exception as exc:
        db.rollback()
        print(f"❌ Error durante el seed: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    run()