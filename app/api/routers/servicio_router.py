from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.servicio_dto import ServicioCreateDTO, ServicioResponseDTO, ServicioUpdateDTO
from app.services.servicio_service import servicio_service

#conexion con service

# servicio_service ya es una instancia singleton, no se instancia de nuevo
servicio_services = servicio_service

router = APIRouter(prefix="/servicios", tags=["Servicios"])

#metodo post

@router.post(
    "",
    response_model=ServicioResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un servicio",
    description="Crea un nuevo servicio con los datos proporcionados",
)
def create_servicio(
    servicio_in: ServicioCreateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> ServicioResponseDTO:
    #crea un servicio
    return servicio_services.create_servicio(db, servicio_in)

@router.get(
    "",
    response_model = list[ServicioResponseDTO],
    summary="Listar todos los servicios",
    description="Obtiene la lista completa de servicios registrados"
)
def get_all_servicios(
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
)-> list[ServicioResponseDTO]:
    return servicio_services.get_all_servicios(db)

@router.get(

    "/{id_servicio}",
    response_model=ServicioResponseDTO,
    summary="Obtener un servicio por ID",
    description="Obtiene un servicio específico por su ID"

)
def get_servicio_by_id(
    id_servicio: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> ServicioResponseDTO:
    servicio = servicio_services.get_servicio_by_id(db, id_servicio)
    if servicio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {id_servicio} no encontrado"
        )
    return servicio


@router.patch(
    "/{id_servicio}",
    response_model=ServicioResponseDTO,
    summary="Actualizar un servicio por ID",
    description="Actualiza los datos de un servicio específico por su ID"
)
def update_servicio(
    id_servicio: int,
    servicio_in: ServicioUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> ServicioResponseDTO:
    servicio_actualizado = servicio_services.update_servicio(db, id_servicio, servicio_in)
    if servicio_actualizado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {id_servicio} no encontrado"
        )
    return servicio_actualizado

@router.delete(
    "/{id_servicio}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un servicio por ID",
    description="Elimina un servicio específico por su ID"
)
def delete_servicio(
    id_servicio: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
):
    servicio = servicio_services.get_servicio_by_id(db, id_servicio)
    if servicio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servicio con ID {id_servicio} no encontrado"
        )
    servicio_services.delete_servicio(db, id_servicio)

