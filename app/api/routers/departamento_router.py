from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.departamento_dto import DepartamentoCreateDTO, DepartamentoResponseDTO, DepartamentoUpdateDTO
from app.services.departament_service import departamento_service

# Corrección: nombre de variable (antes "canal_departamento_services", copiado del canal)
# departamento_service ya es una instancia singleton, no se instancia de nuevo
departamento_services = departamento_service

# ── Configuración del router ────────────────────────────────────────
# prefix: prefijo de la URL (ej: /departamentos)
# tags:   agrupa los endpoints en Swagger bajo "Departamentos"
router = APIRouter(prefix="/departamentos", tags=["Departamentos"])

# router - creacion metodo post

@router.post(
    "",
    response_model=DepartamentoResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un departamento",
    description="Crea un nuevo departamento con los datos proporcionados",
)
def create_departamento(
    departamento_in: DepartamentoCreateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> DepartamentoResponseDTO:
    """Crea un nuevo departamento."""
    # Corrección: comentarios y variable corregidos (antes decía "crea un canal de atención")
    return departamento_services.create_departamento(db, departamento_in)

@router.get(
    "",
    response_model=list[DepartamentoResponseDTO],
    summary="Listar todos los departamentos",
    description="Obtiene la lista completa de departamentos registrados",
)
def get_all_departamentos(
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> list[DepartamentoResponseDTO]:
    """Obtiene la lista completa de departamentos registrados."""
    # Corrección: método renombrado a get_list_departamentos (antes get_all_departamentos no existía en el Service)
    return departamento_services.get_list_departamentos(db)

@router.get(
    "/{id_departamento}",
    response_model=DepartamentoResponseDTO,
    summary="Obtener un departamento por ID",
    description="Obtiene un departamento específico por su ID",
)
def get_departamento_by_id(
    id_departamento: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> DepartamentoResponseDTO:
    """Obtiene un departamento por su ID."""
    # Corrección: se agregó validación 404 (antes no verificaba si el ID existía)
    departamento = departamento_services.get_departamento_by_id(db, id_departamento)
    if departamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento con ID {id_departamento} no encontrado",
        )
    return departamento

@router.patch(
    "/{id_departamento}",
    response_model=DepartamentoResponseDTO,
    summary="Actualizar un departamento por ID",
    description="Actualiza los datos de un departamento específico por su ID",
)
def update_departamento(
    id_departamento: int,
    departamento_in: DepartamentoUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> DepartamentoResponseDTO:
    """Actualiza parcialmente un departamento."""
    # Corrección: se agregó validación 404 (antes no verificaba si el ID existía)
    departamento = departamento_services.update_departamento(db, id_departamento, departamento_in)
    if departamento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento con ID {id_departamento} no encontrado",
        )
    return departamento

@router.delete(
    "/{id_departamento}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un departamento por ID",
    description="Elimina un departamento específico por su ID",
)
def delete_departamento(
    id_departamento: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> None:
    """Elimina un departamento por su ID."""
    # Corrección: typo "elimnado" → "eliminado", variable corregida
    eliminado = departamento_services.delete_departamentos(db, id_departamento)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento con ID {id_departamento} no encontrado",
        )