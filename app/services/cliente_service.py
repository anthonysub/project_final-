import math

from sqlalchemy.orm import Session

from app.models.clientes import Cliente
from app.repositories.cliente_repository import cliente_repository
from app.schemas.cliente_dto import ClienteCreateDTO, ClienteResponseDTO, ClienteUpdateDTO
from app.schemas.common import PaginatedResponse

class ClienteService:
    
    def create_cliente(
            self,
            db: Session,
            cliente_in: ClienteCreateDTO,
    ) -> ClienteResponseDTO:

        cliente_db = Cliente(
            nombres=cliente_in.nombres,
            apellidos=cliente_in.apellidos,
            dpi=cliente_in.dpi,
            celular=cliente_in.celular,
            email=cliente_in.email,
        )

        cliente_creado = cliente_repository.create_cliente(db, cliente_db)

        return ClienteResponseDTO.model_validate(cliente_creado)
    
    # ── READ (uno solo) ─────────────────────────────────────────────
    def get_cliente_by_id(
            self,
            db: Session,
            id_cliente: int,
    ) -> ClienteResponseDTO | None:

        cliente = cliente_repository.get_cliente_by_id(db, id_cliente)

        if cliente is None:
            return None
        return ClienteResponseDTO.model_validate(cliente)
    
    def get_cliente_by_email(
            self,
            db: Session,
            email: str,
    ) -> ClienteResponseDTO | None:

        cliente = cliente_repository.get_cliente_by_email(db, email)

        if cliente is None:
            return None
        return ClienteResponseDTO.model_validate(cliente)
    
    def get_list_clientes(
            self,
            db: Session,
    ) -> list[ClienteResponseDTO]:

        clientes = cliente_repository.get_list_clientes(db)

        return [ClienteResponseDTO.model_validate(cliente) for cliente in clientes]

    # ── Paginación ───────────────────────────────────────────────────
    def get_list_clientes_paginated(
            self,
            db: Session,
            page: int = 1,
            size: int = 20,
    ) -> PaginatedResponse[ClienteResponseDTO]:
        # offset: cuántos registros saltar, limit: cuántos traer
        offset = (page - 1) * size
        total = cliente_repository.count_clientes(db)
        items_db = cliente_repository.get_list_clientes_paginated(db, offset, size)
        items = [ClienteResponseDTO.model_validate(c) for c in items_db]
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if total > 0 else 0,
        )

    def update_cliente(
            self,
            db: Session,
            id_cliente: int,
            cliente_update: ClienteUpdateDTO,
    ) -> ClienteResponseDTO | None:

        datos = cliente_update.model_dump(exclude_unset=True)
        if not datos:
            cliente = cliente_repository.get_cliente_by_id(db, id_cliente)
            return ClienteResponseDTO.model_validate(cliente) if cliente else None
        cliente_actualizado = cliente_repository.update_cliente(
            db, id_cliente, datos
        )
        if cliente_actualizado is None:
            return None
        return ClienteResponseDTO.model_validate(cliente_actualizado)
    
    def delete_cliente(
            self,
            db: Session,
            id_cliente: int,
    ) -> bool:

        return cliente_repository.delete_cliente(db, id_cliente)

cliente_service = ClienteService()