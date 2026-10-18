from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.database import get_db
from app.schemas.cliente_dto import ClienteCreateDTO, ClienteResponseDTO, ClienteUpdateDTO
from app.schemas.common import PaginatedResponse
from app.services.cliente_service import cliente_service

# cliente_service ya es una instancia singleton, no se instancia de nuevo
cliente_services = cliente_service

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    # ── PERMISO: Admin y Gestor gestionan clientes ────────────────────
    dependencies=[Depends(require_role("Administrador", "Gestor"))],
)

@router.post(
    "",
    response_model=ClienteResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un cliente",
    description="Crea un nuevo cliente en el sistema.",
)
def create_cliente(
    cliente_in: ClienteCreateDTO,
    db: Session = Depends(get_db),
) -> ClienteResponseDTO:
    """Crea un nuevo cliente en el sistema."""
    return cliente_services.create_cliente(db, cliente_in)

@router.get(
    "",
    response_model=PaginatedResponse[ClienteResponseDTO],
    summary="Listar todos los clientes (paginado)",
    description="Obtiene la lista de clientes con paginación. Usa ?page=1&size=20.",
)
def get_all_clientes(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
) -> PaginatedResponse[ClienteResponseDTO]:
    """Obtiene clientes paginados. page: página (1-based), size: registros por página."""
    return cliente_services.get_list_clientes_paginated(db, page=page, size=size)

@router.get(
    "/{id_cliente}",
    response_model=ClienteResponseDTO,
    summary="Obtener un cliente por ID",
    description="Obtiene un cliente específico por su ID.",
)
def get_cliente_by_id(
    id_cliente: int,
    db: Session = Depends(get_db),
) -> ClienteResponseDTO:
    """Obtiene un cliente específico por su ID."""
    cliente = cliente_services.get_cliente_by_id(db, id_cliente)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con ID {id_cliente} no encontrado",
        )
    return cliente

@router.patch(
    "/{id_cliente}",
    response_model=ClienteResponseDTO,
    summary="Actualizar un cliente por ID",
    description="Actualiza la información de un cliente específico por su ID.",
)
def update_cliente(
    id_cliente: int,
    cliente_in: ClienteUpdateDTO,
    db: Session = Depends(get_db),
) -> ClienteResponseDTO:
    """Actualiza la información de un cliente específico por su ID."""
    cliente = cliente_services.update_cliente(db, id_cliente, cliente_in)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con ID {id_cliente} no encontrado",
        )
    return cliente

@router.delete(
    "/{id_cliente}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un cliente por ID",
    description="Elimina un cliente específico por su ID.",
)
def delete_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
) -> None:
    """Elimina un cliente específico por su ID."""
    eliminado = cliente_services.delete_cliente(db, id_cliente)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con ID {id_cliente} no encontrado",
        )