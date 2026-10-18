from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.database import get_db
from app.schemas.rol_dto import RolCreateDTO, RolResponseDTO, RolUpdateDTO
from app.services.rol_service import rol_service

# rol_service ya es una instancia singleton, no se instancia de nuevo
rol_services = rol_service

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    # ── PERMISO: solo Administrador gestiona roles ───────────────────
    dependencies=[Depends(require_role("Administrador"))],
)

@router.post(
    "",
    response_model=RolResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un rol",
    description="Crea un nuevo rol con los datos proporcionados",
)
def create_rol(
    rol_in: RolCreateDTO,
    db: Session = Depends(get_db)
) -> RolResponseDTO:
    """Crea un nuevo rol."""
    return rol_services.create_rol(db, rol_in)

@router.get(
    "",
    response_model=list[RolResponseDTO],
    summary="Listar todos los roles",
    description="Obtiene la lista completa de roles registrados",
)
def get_all_roles(
    db: Session = Depends(get_db)
) -> list[RolResponseDTO]:
    """Obtiene la lista completa de roles registrados."""
    return rol_services.get_list_roles(db)

@router.get(
    "/{id_rol}",
    response_model=RolResponseDTO,
    summary="Obtener un rol por ID",
    description="Obtiene un rol específico por su ID",
)
def get_rol_by_id(
    id_rol: int,
    db: Session = Depends(get_db)
) -> RolResponseDTO:
    """Obtiene un rol por su ID."""
    rol = rol_services.get_rol_by_id(db, id_rol)
    if rol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {id_rol} no encontrado"
        )
    return rol  

@router.patch(
    "/{id_rol}",
    response_model=RolResponseDTO,
    summary="Actualizar un rol por ID",
    description="Actualiza un rol específico por su ID con los datos proporcionados",
)
def update_rol(
    id_rol: int,
    rol_in: RolUpdateDTO,
    db: Session = Depends(get_db)
) -> RolResponseDTO:
    """Actualiza un rol específico por su ID con los datos proporcionados."""
    rol_actualizado = rol_services.update_rol(db, id_rol, rol_in)
    if rol_actualizado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {id_rol} no encontrado"
        )
    return rol_actualizado

@router.delete(
    "/{id_rol}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un rol por ID",
    description="Elimina un rol específico por su ID",
)
def delete_rol(
    id_rol: int,
    db: Session = Depends(get_db)
) -> None:
    """Elimina un rol específico por su ID."""
    rol_eliminado = rol_services.delete_rol(db, id_rol)
    if not rol_eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {id_rol} no encontrado"
        )