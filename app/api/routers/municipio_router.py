from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.municipio_dto import (
    MunicipioCreateDTO,
    MunicipioResponseDTO,
    MunicipioUpdateDTO,
)
from app.services.municipio_service import municipio_service

# municipio_service ya es una instancia singleton, no se instancia de nuevo
municipio_services = municipio_service

router = APIRouter(prefix="/municipios", tags=["Municipios"])

@router.post(
    "",
    response_model=MunicipioResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un municipio",
    description="Crea un nuevo municipio en el sistema."
)
def create_municipio(
    municipio_in: MunicipioCreateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> MunicipioResponseDTO:
    """Crea un nuevo municipio en el sistema.

    - **nombre_municipio**: nombre único del municipio.
    - **id_departamento**: ID del departamento al que pertenece el municipio.
    """
    return municipio_services.create_municipio(db, municipio_in)

@router.get(
    "",
    response_model=list[MunicipioResponseDTO],
    summary="Listar todos los municipios",
    description="Obtiene la lista completa de municipios registrados en el sistema."
)
def get_all_municipios(
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> list[MunicipioResponseDTO]:
    """Obtiene la lista completa de municipios registrados en el sistema."""
    return municipio_services.get_list_municipios(db)

# FIX: @router.get y paréntesis en líneas separadas -> misma línea
@router.get(
    "/{id_municipio}",
    response_model=MunicipioResponseDTO,
    summary="Obtener un municipio por ID",
    description="Obtiene un municipio específico por su ID.",
)
def get_municipio_by_id(
    id_municipio: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> MunicipioResponseDTO:
    """Obtiene un municipio específico por su ID.

    - **id_municipio**: ID del municipio a buscar.
    """
    return municipio_services.get_municipio_by_id(db, id_municipio)

@router.patch(
    "/{id_municipio}",
    response_model=MunicipioResponseDTO,
    summary="Actualizar un municipio",
    description="Actualiza la información de un municipio existente."
)   
def update_municipio(
    id_municipio: int,
    municipio_in: MunicipioUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> MunicipioResponseDTO:
    """Actualiza la información de un municipio existente.

    - **id_municipio**: ID del municipio a actualizar.
    - **nombre_municipio**: nuevo nombre del municipio (opcional).
    - **id_departamento**: nuevo ID del departamento al que pertenece el municipio (opcional).
    """
    return municipio_services.update_municipio(db, id_municipio, municipio_in)

@router.delete(
    "/{id_municipio}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un municipio",
    description="Elimina un municipio existente del sistema."
)
def delete_municipio(
    id_municipio: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> None:
    eliminado = municipio_services.delete_municipio(db, id_municipio)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Municipio con ID {id_municipio} no encontrado",
        )