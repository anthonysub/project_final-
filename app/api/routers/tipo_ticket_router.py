# FIX: HTTTPException -> HTTPException (doble T), reponse_model -> response_model, faltaba ':' en get_by_id
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.tipo_ticket_dto import TipoTicketCreateDTO, TipoTicketResponseDTO, TipoTicketUpdateDTO
from app.services.tipo_ticket_service import tipo_ticket_service

# tipo_ticket_service ya es una instancia singleton, no se instancia de nuevo
tipo_ticket_services = tipo_ticket_service

router = APIRouter(prefix="/tipos-ticket", tags=["Tipos de Ticket"])

@router.post(
    "",
    response_model=TipoTicketResponseDTO,
    status_code = status.HTTP_201_CREATED,
    summary = "crear un tipo de ticker",
    description = "Crea un nuevo tipo de ticket con los datos proporcionados",
)
def create_tipo_ticket(
    tipo_ticket_in: TipoTicketCreateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> TipoTicketResponseDTO:
    """Crea un nuevo tipo de ticket."""
    return tipo_ticket_services.create_tipo_ticket(db, tipo_ticket_in)

@router.get(
    "",
    response_model = list[TipoTicketResponseDTO],
    summary = "Listar todos los tipos de ticket",
    description = "Obtiene la lista completa de tipos de ticket registrados",
)
def get_all_tipos_ticket(
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> list[TipoTicketResponseDTO]:
    """Obtiene la lista completa de tipos de ticket registrados."""
    return tipo_ticket_services.get_all_tipos_ticket(db)

@router.get(
    "/{id_tipo_ticket}",
    response_model = TipoTicketResponseDTO,
    summary = "Obtener un tipo de ticket por ID",
    description = "Obtiene un tipo de ticket específico por su ID",
)
def get_tipo_ticket_by_id(
    id_tipo_ticket: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> TipoTicketResponseDTO:
    """Obtiene un tipo de ticket para su ID"""
    return tipo_ticket_services.get_tipo_ticket_by_id(db, id_tipo_ticket)

@router.patch(
    "/{id_tipo_ticket}",
    response_model = TipoTicketResponseDTO,
    summary = "Actualizar un tipo de ticket por ID",
    description = "Actualiza un tipo de ticket específico por su ID con los datos proporcionados",
)
def update_tipo_ticket(
    id_tipo_ticket: int,
    tipo_ticket_in: TipoTicketUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> TipoTicketResponseDTO:
    """Actualiza un tipo de ticket específico por su ID con los datos proporcionados."""    
    tipo_ticket_actualizado = tipo_ticket_services.update_tipo_ticket(db, id_tipo_ticket, tipo_ticket_in)
    if tipo_ticket_actualizado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de ticket con ID {id_tipo_ticket} no encontrado"
        )
    return tipo_ticket_actualizado

@router.delete(
    "/{id_tipo_ticket}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un tipo de ticket por ID",
    description="Elimina un tipo de ticket específico por su ID",
)
def delete_tipo_ticket(
    id_tipo_ticket: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> None:
    """Elimina un tipo de ticket específico por su ID."""
    eliminado = tipo_ticket_services.delete_tipo_ticket(db, id_tipo_ticket)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de ticket con ID {id_tipo_ticket} no encontrado"
        )
    

    