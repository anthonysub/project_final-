from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.database import get_db
from app.schemas.direccion_dto import (
    DireccionCreateDTO,
    DireccionResponseDTO,
    DireccionUpdateDTO,
)
from app.services.direccion_service import direccion_service

# direccion_service ya es una instancia singleton, no se instancia de nuevo
direccion_services = direccion_service

router = APIRouter(
    prefix="/direcciones",
    tags=["Direcciones"],
    # ── PERMISO: Admin y Gestor gestionan direcciones ─────────────────
    dependencies=[Depends(require_role("Administrador", "Gestor"))],
)

@router.post(
    "",
    response_model=DireccionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una dirección",
    description="Crea una nueva dirección en el sistema."
)
def create_direccion(
    direccion_in: DireccionCreateDTO,
    db: Session = Depends(get_db)
) -> DireccionResponseDTO:
    """Crea una nueva dirección en el sistema.

    - **descripcion**: Descripción de la dirección.
    - **calle**: Calle de la dirección.
    - **zona**: Zona de la dirección.
    - **avenida**: Avenida (opcional).
    - **referencia**: Referencia (opcional).
    - **detalles_direccion**: Detalles adicionales.
    - **id_cliente**: ID del cliente asociado.
    - **id_municipio**: ID del municipio asociado.
    """
    return direccion_services.create_direccion(db, direccion_in)

@router.get(
    "",
    response_model=list[DireccionResponseDTO],
    summary="Listar todas las direcciones",
    description="Obtiene la lista completa de direcciones registradas en el sistema."
)
def get_list_direcciones(
    db: Session = Depends(get_db)
) -> list[DireccionResponseDTO]:
    """Obtiene la lista completa de direcciones registradas en el sistema."""
    return direccion_services.get_list_direcciones(db)

@router.get(
    "/{id_direccion}",
    response_model=DireccionResponseDTO,
    summary="Obtener una dirección por ID",
    description="Obtiene una dirección específica por su ID."
)
def get_direccion_by_id(
    id_direccion: int,
    db: Session = Depends(get_db)
) -> DireccionResponseDTO:
    """Obtiene una dirección específica por su ID.

    - **id_direccion**: ID de la dirección a buscar.
    """
    direccion = direccion_services.get_direccion_by_id(db, id_direccion)
    if direccion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dirección con ID {id_direccion} no encontrada",
        )
    return direccion

@router.patch(
    "/{id_direccion}",
    response_model=DireccionResponseDTO,
    summary="Actualizar una dirección por ID",
    description="Actualiza los datos de una dirección específica por su ID."
)
def update_direccion(
    id_direccion: int,
    direccion_in: DireccionUpdateDTO,
    db: Session = Depends(get_db)
) -> DireccionResponseDTO:
    """Actualiza los datos de una dirección específica por su ID.

    - **id_direccion**: ID de la dirección a actualizar.
    - **direccion_in**: Datos a actualizar de la dirección.
    """
    direccion = direccion_services.update_direccion(db, id_direccion, direccion_in)
    if direccion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dirección con ID {id_direccion} no encontrada",
        )
    return direccion

@router.delete(
    "/{id_direccion}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una dirección por ID",
    description="Elimina una dirección específica por su ID."
)
def delete_direccion(
    id_direccion: int,
    db: Session = Depends(get_db)
) -> None:
    """Elimina una dirección específica por su ID.

    - **id_direccion**: ID de la dirección a eliminar.
    """
    eliminado = direccion_services.delete_direccion(db, id_direccion)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dirección con ID {id_direccion} no encontrada",
        )