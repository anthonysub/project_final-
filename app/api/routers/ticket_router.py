"""
Ticket Router — Endpoints HTTP para la entidad Ticket.

Flujo: Cliente -> Router -> Service -> Repository -> BD
El router solo maneja HTTP: recibe requests, delega al Service, responde.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.ticket_dto import TicketCreateDTO, TicketResponseDTO, TicketUpdateDTO
from app.services.ticket_service import ticket_service


router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponseDTO, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_in: TicketCreateDTO,
    id_receptor: int = Query(..., description="ID del empleado que recibe el ticket"),
    id_estado: int = Query(..., description="ID del estado inicial del ticket"),
    id_tecnico: int | None = Query(None, description="ID del técnico asignado, si aplica"),
    db: Session = Depends(get_db),
    # ── PERMISO: solo Admin y Gestor pueden crear tickets ────────────
    current_user: Empleado = Depends(require_role("Administrador", "Gestor")),
) -> TicketResponseDTO:
    return ticket_service.create_ticket(db, ticket_in, id_receptor, id_estado, id_tecnico)


@router.get("/{id_ticket}", response_model=TicketResponseDTO)
def get_ticket_by_id(
    id_ticket: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> TicketResponseDTO:
    ticket = ticket_service.get_ticket_by_id(db, id_ticket)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")

    # ── AISLAMIENTO POR EMPLEADO ─────────────────────────────────────
    # Regla: un Técnico solo puede ver los tickets que le fueron asignados
    # (ticket.id_tecnico == su id_empleado). Administrador y Gestor ven todo.
    if current_user.rol.nombre_rol == "Técnico" and ticket.id_tecnico != current_user.id_empleado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este ticket",
        )

    return ticket


@router.get("/cliente/{id_cliente}", response_model=list[TicketResponseDTO])
def get_tickets_by_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> list[TicketResponseDTO]:
    # ── AISLAMIENTO: el técnico solo ve los tickets de ese cliente que son suyos ──
    id_tecnico = current_user.id_empleado if current_user.rol.nombre_rol == "Técnico" else None
    return ticket_service.get_tickets_by_cliente(db, id_cliente, id_tecnico)


@router.patch("/{id_ticket}", response_model=TicketResponseDTO)
def update_ticket(
    id_ticket: int,
    ticket_update: TicketUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> TicketResponseDTO:
    ticket = ticket_service.update_ticket(db, id_ticket, ticket_update)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")

    if current_user.rol.nombre_rol == "Técnico" and ticket.id_tecnico != current_user.id_empleado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este ticket",
            )
    return ticket


# GET /tickets — Listado paginado con filtros (Fase 4.3)
@router.get("", response_model=list[TicketResponseDTO])
def get_all_tickets(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(50, ge=1, le=100, description="Maximo de registros"),
    id_estado: int | None = Query(None, description="Filtrar por ID de estado"),
    id_tecnico: int | None = Query(None, description="Filtrar por ID de tecnico"),
    id_cliente: int | None = Query(None, description="Filtrar por ID de cliente"),
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> list[TicketResponseDTO]:
    """Lista tickets con paginacion y filtros opcionales."""
    # ── AISLAMIENTO EN LISTA (técnica del WHERE) ─────────────────────
    # En vez de traer TODOS los tickets y filtrar en Python, forzamos el
    # filtro id_tecnico para que el Técnico solo vea los SUYOS. El repo
    # ya hace .filter(Ticket.id_tecnico == id_tecnico) → ese .filter es
    # el "WHERE" en SQL. Así el filtrado ocurre en la base de datos.
    if current_user.rol.nombre_rol == "Técnico":
        id_tecnico = current_user.id_empleado

    return ticket_service.get_all_tickets(
        db,
        skip=skip,
        limit=limit,
        id_estado=id_estado,
        id_tecnico=id_tecnico,
        id_cliente=id_cliente,
    )


# DELETE /tickets/{id_ticket} — Eliminar un ticket (Fase 4.3)
@router.delete("/{id_ticket}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    id_ticket: int,
    db: Session = Depends(get_db),
    # ── PERMISO (delegación correcta) ────────────────────────────────
    # require_role("Administrador") valida el rol ANTES de ejecutar el
    # cuerpo. Si el rol no es Administrador → 403 y NO corre nada de abajo.
    #
    # BUG anterior: se hacía delete_ticket(...) PRIMERO y la validación
    # DESPUÉS, por eso el ticket se borraba aunque la validación fallara.
    # Regla de oro: PRIMERO validar, DESPUÉS actuar.
    current_user: Empleado = Depends(require_role("Administrador")),
) -> None:
    """Elimina un ticket. Retorna 204 si se elimino, 404 si no existe."""
    eliminado = ticket_service.delete_ticket(db, id_ticket)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado",
        )

 