"""
Canal Router — Endpoints HTTP para la entidad Canal.

Flujo: Cliente -> Router -> Service -> Repository -> BD
El router solo maneja HTTP: recibe requests, delega al Service, responde.

Patrón canónico para TODOS los routers del proyecto.
Usa este archivo como plantilla para crear los demás routers de catálogos.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.canal_dto import CanalCreateDTO, CanalResponseDTO, CanalUpdateDTO
from app.services.canal_service import canal_service

 
# canal_service ya es una instancia singleton (CanalService())
# importada de app.services.canal_service. No se instancia de nuevo.
canal_services = canal_service

# ── Configuración del router ────────────────────────────────────────
# prefix: prefijo de la URL (ej: /canales)
# tags:   agrupa los endpoints en Swagger bajo "Canales"
router = APIRouter(prefix="/canales", tags=["Canales"])


# ── CREATE ──────────────────────────────────────────────────────────
@router.post(
    "",
    response_model=CanalResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un canal",
)
def create_canal(
    canal_in: CanalCreateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> CanalResponseDTO:
    """Crea un nuevo canal (ej: Teléfono, Correo, Presencial).

    - **nombre_canal**: nombre único del canal de atención.
    """
    return canal_services.create_canal(db, canal_in)


# ── READ (listado) ──────────────────────────────────────────────────
@router.get(
    "",
    response_model=list[CanalResponseDTO],
    summary="Listar todos los canales",
)
def get_all_canales(
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> list[CanalResponseDTO]:
    """Obtiene la lista completa de canales registrados."""
    return canal_services.get_all_canales(db)


# ── READ (uno solo) ─────────────────────────────────────────────────
@router.get(
    "/{id_canal}",
    response_model=CanalResponseDTO,
    summary="Obtener un canal por ID",
)
def get_canal_by_id(
    id_canal: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> CanalResponseDTO:
    """Obtiene un canal específico por su ID.

    - **id_canal**: identificador único del canal.
    """
    canal = canal_services.get_canal_by_id(db, id_canal)
    if canal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canal con ID {id_canal} no encontrado",
        )
    return canal


# ── UPDATE ──────────────────────────────────────────────────────────
@router.patch(
    "/{id_canal}",
    response_model=CanalResponseDTO,
    summary="Actualizar un canal (parcial)",
)
def update_canal(
    id_canal: int,
    canal_update: CanalUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> CanalResponseDTO:
    """Actualiza parcialmente un canal. Solo los campos enviados se modifican.

    - **id_canal**: ID del canal a modificar.
    - **nombre_canal** (opcional): nuevo nombre del canal.
    """
    canal = canal_services.update_canal(db, id_canal, canal_update)
    if canal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canal con ID {id_canal} no encontrado",
        )
    return canal


# ── DELETE ──────────────────────────────────────────────────────────
@router.delete(
    "/{id_canal}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un canal",
)
def delete_canal(
    id_canal: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> None:
    """Elimina un canal por su ID. Retorna 204 si fue exitoso, 404 si no existe.

    - **id_canal**: ID del canal a eliminar.
    """
    eliminado = canal_services.delete_canal(db, id_canal)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canal con ID {id_canal} no encontrado",
        )