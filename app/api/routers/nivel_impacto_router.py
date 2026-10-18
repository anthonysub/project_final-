from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.nivel_impacto_dto import NivelImpactoCreateDTO, NivelImpactoResponseDTO, NivelImpactoUpdateDTO
from app.services.nivel_impacto_service import nivel_impacto_service

#creacion de conexion con services

router = APIRouter(prefix="/niveles-impacto", tags=["Niveles de Impacto"])

#router - creacion de metodo post

@router.post(
    "",
    response_model=NivelImpactoResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nivel de impacto",
    description="Crea un nuevo nivel de impacto con los datos proporcionados",
)
def create_nivel_impacto(
    nivel_impacto_in: NivelImpactoCreateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> NivelImpactoResponseDTO:
    """Crea un nuevo nivel de impacto."""
    return nivel_impacto_service.create_nivel_impacto(db, nivel_impacto_in)

@router.get(
    "",
    response_model=list[NivelImpactoResponseDTO],
    summary="Listar todos los niveles de impacto",
    description="Obtiene la lista completa de niveles de impacto registrados",
) 
def get_all_niveles_impacto(
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> list[NivelImpactoResponseDTO]:
    """Obtiene la lista completa de niveles de impacto registrados."""
    return nivel_impacto_service.get_list_niveles_impacto(db)

@router.get(
    "/{id_nivel_impacto}",
    response_model=NivelImpactoResponseDTO,
    summary="Obtener un nivel de impacto por ID",
    description="Obtiene un nivel de impacto específico por su ID",
)
def get_nivel_impacto_by_id(
    id_nivel_impacto: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> NivelImpactoResponseDTO:
    """Obtiene un nivel de impacto por su ID."""
    nivel_impacto = nivel_impacto_service.get_nivel_impacto_by_id(db, id_nivel_impacto)
    if nivel_impacto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nivel de impacto con ID {id_nivel_impacto} no encontrado"
        )
    return nivel_impacto    

@router.patch(
    "/{id_nivel_impacto}",
    response_model=NivelImpactoResponseDTO,
    summary="Actualizar un nivel de impacto por ID",
    description="Actualiza los datos de un nivel de impacto específico por su ID",
)
def update_nivel_impacto(
    id_nivel_impacto: int,
    nivel_impacto_in: NivelImpactoUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> NivelImpactoResponseDTO:
    """Actualiza un nivel de impacto por su ID."""
    nivel_impacto_actualizado = nivel_impacto_service.update_nivel_impacto(db, id_nivel_impacto, nivel_impacto_in)
    if nivel_impacto_actualizado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nivel de impacto con ID {id_nivel_impacto} no encontrado"
        )
    return nivel_impacto_actualizado

@router.delete(
    "/{id_nivel_impacto}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un nivel de impacto por ID",
    description="Elimina un nivel de impacto específico por su ID",
)
def delete_nivel_impacto(
    id_nivel_impacto: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> None:
    """Elimina un nivel de impacto por su ID."""
    eliminado = nivel_impacto_service.delete_nivel_impacto(db, id_nivel_impacto)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nivel de impacto con ID {id_nivel_impacto} no encontrado"
        )