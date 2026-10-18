from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.database import get_db
from app.schemas.cliente_servicio_dto import (
    ClienteServicioCreateDTO,
    ClienteServicioResponseDTO,
    ClienteServicioUpdateDTO,
)
from app.services.cliente_servicio_service import cliente_servicio_service

# cliente_servicio_service ya es una instancia singleton, no se instancia de nuevo
cliente_servicio_services = cliente_servicio_service

router = APIRouter(
    prefix="/cliente_servicios",
    tags=["ClienteServicios"],
    # ── PERMISO: Admin y Gestor gestionan cliente-servicios ───────────
    dependencies=[Depends(require_role("Administrador", "Gestor"))],
)

@router.post(
    "",
    response_model = ClienteServicioResponseDTO,
    status_code = status.HTTP_201_CREATED,
    summary = "Crear un cliente_servicio",
    description = "Crea un nuevo cliente_servicio en el sistema."
)
def create_cliente_servicio(
    cliente_servicio_in: ClienteServicioCreateDTO,
    db: Session = Depends(get_db)
) -> ClienteServicioResponseDTO:
    """Crea un nuevo cliente_servicio en el sistema.

    - **id_cliente**: ID del cliente asociado.
    - **id_servicio**: ID del servicio asociado.
    """
    return cliente_servicio_services.create_cliente_servicio(db, cliente_servicio_in)

@router.get(
    "",
    response_model = list[ClienteServicioResponseDTO],
    summary = "Listar todos los cliente_servicios",
    description = "Obtiene la lista completa de cliente_servicios registrados en el sistema."
    
)
def get_all_cliente_servicios(
    db: Session = Depends(get_db)
) -> list[ClienteServicioResponseDTO]:
    """Obtiene la lista completa de cliente_servicios registrados en el sistema."""
    return cliente_servicio_services.get_list_clientes_servicios(db)

@router.get(
    "/{id_cliente_servicio}",
    response_model = ClienteServicioResponseDTO,
    summary = "Obtener un cliente_servicio por ID",
    description = "Obtiene un cliente_servicio específico por su ID."
)
def get_cliente_servicio_by_id(
    id_cliente_servicio: int,
    db: Session = Depends(get_db)
) -> ClienteServicioResponseDTO:
    """Obtiene un cliente_servicio específico por su ID.

    - **id_cliente_servicio**: ID del cliente_servicio a buscar.
    """
    return cliente_servicio_services.get_cliente_servicio_by_id(db, id_cliente_servicio)

@router.patch(
    "/{id_cliente_servicio}",
    response_model = ClienteServicioResponseDTO,
    summary = "Actualizar un cliente_servicio por ID",
    description = "Actualiza los datos de un cliente_servicio específico por su ID."
)
def update_cliente_servicio(
    id_cliente_servicio: int,
    cliente_servicio_in: ClienteServicioUpdateDTO,
    db: Session = Depends(get_db)
) -> ClienteServicioResponseDTO:
    """Actualiza los datos de un cliente_servicio específico por su ID.

    - **id_cliente_servicio**: ID del cliente_servicio a actualizar.
    - **cliente_servicio_in**: Datos a actualizar del cliente_servicio.
    """
    return cliente_servicio_services.update_cliente_servicio(db, id_cliente_servicio, cliente_servicio_in)

@router.delete(
    "/{id_cliente_servicio}",
    status_code = status.HTTP_204_NO_CONTENT,
    summary = "Eliminar un cliente_servicio por ID",
    description = "Elimina un cliente_servicio específico por su ID."
)
def delete_cliente_servicio(
    id_cliente_servicio: int,
    db: Session = Depends(get_db)
) -> None:
    """Elimina un cliente_servicio específico por su ID.

    - **id_cliente_servicio**: ID del cliente_servicio a eliminar.
    """
    eliminado = cliente_servicio_services.delete_cliente_servicio(db, id_cliente_servicio)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClienteServicio con ID {id_cliente_servicio} no encontrado"
        )
    
    