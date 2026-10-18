from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.estado_ticket_dto import EstadoTicketCreateDTO, EstadoTicketResponseDTO, EstadoTicketUpdateDTO
from app.services.estado_ticket_service import estado_ticket_service

# estado_ticket_service ya es una instancia singleton, no se instancia de nuevo
estado_ticket_services = estado_ticket_service

router = APIRouter(prefix="/estados-ticket", tags=["Estados de Ticket"])

#creación del router

@router.post(
    "",
    response_model = EstadoTicketResponseDTO,
    status_code = status.HTTP_201_CREATED,
    summary = "Crear un estado de ticket",
    description = "Crea un nuevo estado de ticket con los datos proporcionados",
)
def create_estado_ticket(
    canal_in: EstadoTicketCreateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> EstadoTicketResponseDTO:
    """Crea un nuevo estado de ticket."""
    return estado_ticket_services.create_estado_ticket(db, canal_in)

@router.get(
    "",
    response_model = list[EstadoTicketResponseDTO],
    summary = "Listar todos los estados de ticket",
    description = "Obtiene la lista completa de estados de ticket registrados",
)
def get_all_estados_ticket(
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> list[EstadoTicketResponseDTO]:
    """Obtiene la lista completa de estados de ticket registrados."""
    return estado_ticket_services.get_list_estado_tickets(db)

# FIX: reponse_model -> response_model, id_canal -> id_estado_ticket
@router.get(
    "/{id_estado_ticket}",
    response_model=EstadoTicketResponseDTO,
    summary = "Obtener un estado de ticket por ID",
    description = "Obtiene un estado de ticket específico por su ID",
)
def get_estado_ticket_by_id(
    id_estado_ticket: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> EstadoTicketResponseDTO:
    """Obtiene un estado de ticket por su ID."""
    estado_ticket = estado_ticket_services.get_estado_ticket_by_id(db, id_estado_ticket)
    if estado_ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estado de ticket con ID {id_estado_ticket} no encontrado"
        )
    return estado_ticket

@router.patch(
    "/{id_estado_ticket}",
    response_model = EstadoTicketResponseDTO,
    summary = "Actualizar un estado de ticket",
    description = "Actualiza un estado de ticket existente con los datos proporcionados",
)
def update_estado_ticket(
    id_estado_ticket: int,
    estado_ticket_in: EstadoTicketUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> EstadoTicketResponseDTO:
    """Actualiza un estado de ticket existente."""
    estado_ticket_actualizado = estado_ticket_services.update_estado_ticket(db, id_estado_ticket, estado_ticket_in)
    if estado_ticket_actualizado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estado de ticket con ID {id_estado_ticket} no encontrado"
        )
    return estado_ticket_actualizado

@router.delete(
    "/{id_estado_ticket}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un estado de ticket",
    description="Elimina un estado de ticket existente por su ID",
)
def delete_estado_ticket(
    id_estado_ticket: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> None:
    """Elimina un estado de ticket existente por su ID."""
    eliminado = estado_ticket_services.delete_estado_ticket(db, id_estado_ticket)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estado de ticket con ID {id_estado_ticket} no encontrado"
        )
    return None

