from datetime import datetime, timezone
from secrets import token_hex

from sqlalchemy.orm import Session

from app.models.tickets import Ticket
from app.repositories.ticket_repository import ticket_repository
from app.schemas.ticket_dto import TicketCreateDTO, TicketResponseDTO, TicketUpdateDTO


class TicketService:

    def _build_ticket_entity(
        self,
        ticket_in: TicketCreateDTO,
        id_receptor: int,
        id_estado: int,
        id_tecnico: int | None,
    ) -> Ticket:
        codigo_ticket = f"TK-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{token_hex(4)}"
        return Ticket(
            codigo_ticket=codigo_ticket,
            id_cliente=ticket_in.id_cliente,
            id_receptor=id_receptor,
            id_tecnico=id_tecnico,
            id_canal=ticket_in.id_canal,
            id_estado=id_estado,
            id_tipo_ticket=ticket_in.id_tipo_ticket,
            id_impacto=ticket_in.id_impacto,
            id_plantilla=ticket_in.id_plantilla,
            datos_respuesta=ticket_in.respuestas_extra or {},
        )

    def create_ticket(
        self,
        db: Session,
        ticket_in: TicketCreateDTO,
        id_receptor: int,
        id_estado: int,
        id_tecnico: int | None,
    ) -> TicketResponseDTO:
        ticket_db = self._build_ticket_entity(ticket_in, id_receptor, id_estado, id_tecnico)
        ticket_created = ticket_repository.create_ticket(db, ticket_db)
        return TicketResponseDTO.model_validate(ticket_created)

    def get_ticket_by_id(self, db: Session, id_ticket: int) -> TicketResponseDTO | None:
        ticket = ticket_repository.get_ticket_by_id(db, id_ticket)
        if ticket is None:
            return None
        return TicketResponseDTO.model_validate(ticket)

    def get_tickets_by_cliente(self, db: Session, id_cliente: int, id_tecnico: int | None = None) -> list[TicketResponseDTO]:
        tickets = ticket_repository.get_tickets_by_cliente(db, id_cliente, id_tecnico)
        return [TicketResponseDTO.model_validate(ticket) for ticket in tickets]

    def update_ticket(  
        self,
        db: Session,
        id_ticket: int,
        ticket_update: TicketUpdateDTO,
    ) -> TicketResponseDTO | None:

        datos = ticket_update.model_dump(exclude_unset=True)
        if not datos:
            ticket = ticket_repository.get_ticket_by_id(db, id_ticket)
            if ticket is None:
                return None
            return TicketResponseDTO.model_validate(ticket)
        ticket_actualizado = ticket_repository.update_ticket(db, id_ticket, datos)
        if ticket_actualizado is None:
            return None
        return TicketResponseDTO.model_validate(ticket_actualizado)


    def delete_ticket(self, db: Session, id_ticket: int) -> bool:
        """Elimina un ticket de la base de datos.

        Parameters
        ----------
        db : Session
            Sesión activa de SQLAlchemy.
        id_ticket : int
            ID del ticket a eliminar.

        Returns
        -------
        bool
            True si se eliminó correctamente; False si el ticket no existía.
        """
        return ticket_repository.delete_ticket(db, id_ticket)


    def get_all_tickets(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        id_estado: int | None = None,
        id_tecnico: int | None = None,
        id_cliente: int | None = None,
    ) -> list[TicketResponseDTO]:
        """Listado paginado de tickets con filtros opcionales."""
        tickets = ticket_repository.get_all_tickets(
            db,
            skip=skip,
            limit=limit,
            id_estado=id_estado,
            id_tecnico=id_tecnico,
            id_cliente=id_cliente,
        )
        return [
            TicketResponseDTO.model_validate(ticket) for ticket in tickets
        ]


  

ticket_service = TicketService()
