"""
Plantilla Formulario Router — Endpoints HTTP para Plantillas de Formulario.

Flujo: Cliente -> Router -> Service -> Repository -> BD
El router solo maneja HTTP: recibe requests, delega al Service, responde.

Particularidades de este router frente a otros catálogos:
1. El campo `estructura_preguntas` es JSONB (Dict[str, Any]) — se valida que
   sea un diccionario antes de pasarlo al service (defensa en profundidad).
2. `estado_plantilla` es bool con default=True en creación — solo una plantilla
   debería estar activa a la vez (lógica de negocio en el service, no aquí).
3. DELETE debe considerar si hay tickets asociados a la plantilla
   (soft-delete recomendado a futuro, hoy es hard-delete).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.plantilla_formulario_dto import (
    PlantillaFormularioCreateDTO,
    PlantillaFormularioResponseDTO,
    PlantillaFormularioUpdateDTO,
)
from app.services.plantilla_service import plantilla_service

# ── Instancia del service (singleton importado) ──────────────────────
# plantilla_service ya viene instanciado desde plantilla_service.py
# No se instancia aquí porque el módulo ya exporta la instancia.

# ── Configuración del router ────────────────────────────────────────
# prefix: todas las rutas de este archivo empiezan con /plantillas
# tags:   agrupa los endpoints en Swagger bajo "Plantillas de Formulario"
router = APIRouter(prefix="/plantillas", tags=["Plantillas de Formulario"])


# ══════════════════════════════════════════════════════════════════════
# CREATE — POST /plantillas
# ══════════════════════════════════════════════════════════════════════
@router.post(
    "",
    response_model=PlantillaFormularioResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una plantilla de formulario",
    description=(
        "Crea una nueva plantilla con preguntas dinámicas en formato JSON. "
        "`estructura_preguntas` debe ser un diccionario JSON válido "
        '(ej: {"pregunta1": {"tipo": "texto", "label": "Nombre"}}). '
        "`estado_plantilla` por defecto es True (activa)."
    ),
)
def create_plantilla(
    plantilla_in: PlantillaFormularioCreateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> PlantillaFormularioResponseDTO:
    """Crea una nueva plantilla de formulario.

    Parameters
    ----------
    plantilla_in : PlantillaFormularioCreateDTO
        - nombre_plantilla: str — nombre descriptivo de la plantilla
        - estructura_preguntas: dict — preguntas en formato JSONB
        - estado_plantilla: bool (default=True) — si está activa o no
    db : Session
        Sesión de BD inyectada por FastAPI via Depends(get_db).

    Returns
    -------
    PlantillaFormularioResponseDTO con status 201 Created.

    Raises
    ------
    HTTPException 422
        Si estructura_preguntas no es un dict (Pydantic lo rechaza antes).
    """
    # Validación extra (defensa en profundidad): aunque Pydantic ya validó
    # que el tipo sea Dict[str, Any], un valor malicioso podría colarse.
    if not isinstance(plantilla_in.estructura_preguntas, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="estructura_preguntas debe ser un diccionario JSON válido",
        )
    return plantilla_service.create_plantilla(db, plantilla_in)


# ══════════════════════════════════════════════════════════════════════
# READ (listado) — GET /plantillas
# ══════════════════════════════════════════════════════════════════════
@router.get(
    "",
    response_model=list[PlantillaFormularioResponseDTO],
    summary="Listar todas las plantillas",
    description="Obtiene la lista completa de plantillas de formulario registradas.",
)
def get_all_plantillas(
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> list[PlantillaFormularioResponseDTO]:
    """Lista todas las plantillas de formulario.

    Returns
    -------
    list[PlantillaFormularioResponseDTO]
        Lista de plantillas (vacía si no hay ninguna). Cada elemento incluye
        id_plantilla, nombre_plantilla, estructura_preguntas y estado_plantilla.
    """
    return plantilla_service.get_all_plantillas(db)


# ══════════════════════════════════════════════════════════════════════
# READ (uno solo) — GET /plantillas/{id_plantilla}
# ══════════════════════════════════════════════════════════════════════
@router.get(
    "/{id_plantilla}",
    response_model=PlantillaFormularioResponseDTO,
    summary="Obtener una plantilla por ID",
    description="Obtiene una plantilla específica por su ID.",
)
def get_plantilla_by_id(
    id_plantilla: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(get_current_user),
) -> PlantillaFormularioResponseDTO:
    """Obtiene una plantilla por su ID.

    Parameters
    ----------
    id_plantilla : int
        ID de la plantilla a buscar.
    db : Session
        Sesión de BD inyectada por FastAPI.

    Returns
    -------
    PlantillaFormularioResponseDTO con la plantilla encontrada.

    Raises
    ------
    HTTPException 404
        Si no existe una plantilla con ese ID.
    """
    plantilla = plantilla_service.get_plantilla_by_id(db, id_plantilla)
    if plantilla is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla con ID {id_plantilla} no encontrada",
        )
    return plantilla


# ══════════════════════════════════════════════════════════════════════
# UPDATE — PATCH /plantillas/{id_plantilla}
# ══════════════════════════════════════════════════════════════════════
@router.patch(
    "/{id_plantilla}",
    response_model=PlantillaFormularioResponseDTO,
    summary="Actualizar una plantilla (parcial)",
    description=(
        "Actualiza parcialmente una plantilla. Solo los campos enviados "
        "se modifican. `estructura_preguntas` si se envía debe ser un dict."
    ),
)
def update_plantilla(
    id_plantilla: int,
    plantilla_update: PlantillaFormularioUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> PlantillaFormularioResponseDTO:
    """Actualiza parcialmente una plantilla de formulario.

    Parameters
    ----------
    id_plantilla : int
        ID de la plantilla a modificar.
    plantilla_update : PlantillaFormularioUpdateDTO
        Campos opcionales a actualizar:
        - nombre_plantilla: str | None
        - estructura_preguntas: dict | None
        - estado_plantilla: bool | None
    db : Session
        Sesión de BD inyectada por FastAPI.

    Returns
    -------
    PlantillaFormularioResponseDTO con los datos actualizados.

    Raises
    ------
    HTTPException 404
        Si no existe una plantilla con ese ID.
    HTTPException 422
        Si estructura_preguntas se envía pero no es un diccionario.
    """
    # Validación extra para JSONB en modo update también.
    # Si el cliente envía estructura_preguntas, nos aseguramos de que sea dict.
    if (
        plantilla_update.estructura_preguntas is not None
        and not isinstance(plantilla_update.estructura_preguntas, dict)
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="estructura_preguntas debe ser un diccionario JSON válido",
        )

    plantilla = plantilla_service.update_plantilla(
        db, id_plantilla, plantilla_update
    )
    if plantilla is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla con ID {id_plantilla} no encontrada",
        )
    return plantilla


# ══════════════════════════════════════════════════════════════════════
# DELETE — DELETE /plantillas/{id_plantilla}
# ══════════════════════════════════════════════════════════════════════
@router.delete(
    "/{id_plantilla}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una plantilla",
    description="Elimina una plantilla por su ID. Retorna 204 si fue exitoso.",
)
def delete_plantilla(
    id_plantilla: int,
    db: Session = Depends(get_db),
    current_user: Empleado = Depends(require_role("Administrador")),
) -> None:
    """Elimina una plantilla de formulario por su ID.

    Parameters
    ----------
    id_plantilla : int
        ID de la plantilla a eliminar.
    db : Session
        Sesión de BD inyectada por FastAPI.

    Returns
    -------
    None — FastAPI responde automáticamente 204 No Content al terminar la función
    sin errores.

    Raises
    ------
    HTTPException 404
        Si no existe una plantilla con ese ID.

    Nota técnica
    ------------
    El tipo de retorno es `-> None`. Cuando el decorador tiene
    `status_code=HTTP_204_NO_CONTENT`, FastAPI envía una respuesta vacía
    con código 204 automáticamente si la función termina sin lanzar excepciones.
    No hace falta `return` ni `return None` explícito.

    ADVERTENCIA (deuda técnica)
    ---------------------------
    Actualmente es un hard-delete. Si hay tickets asociados a esta plantilla,
    la eliminación podría fallar por foreign key constraint en la BD.
    A futuro se recomienda implementar soft-delete (campo `activo=False`).
    """
    # ⚠️ BUG CONOCIDO EN EL SERVICE:
    # `delete_plantilla` está definido FUERA de la clase PlantillaService
    # (líneas 199-204 de plantilla_service.py). Tiene `self` como primer
    # parámetro pero no pertenece a la clase, lo que causará un error
    # al llamarlo como método de instancia.
    #
    # Solución: mover `delete_plantilla` dentro de la clase PlantillaService.
    # Mientras tanto, este endpoint fallará hasta que se corrija el service.
    eliminado = plantilla_service.delete_plantilla(db, id_plantilla)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plantilla con ID {id_plantilla} no encontrada",
        )
    # Sin return explícito → FastAPI envía 204 No Content automáticamente.