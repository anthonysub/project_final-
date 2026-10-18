"""
Router de autenticación — login y perfil del usuario autenticado.

Endpoints:
  - POST /auth/login   → recibe email + password, devuelve JWT.
  - GET  /auth/me      → devuelve los datos del empleado autenticado (protegido).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.models.empleados import Empleado
from app.schemas.auth_dto import TokenResponseDTO
from app.schemas.empleado_dto import EmpleadoResponseDTO

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponseDTO,
    summary="Iniciar sesión",
    description="Autentica a un empleado (username=email, password) y devuelve un token JWT. "
                "Compatible con el botón Authorize de Swagger (OAuth2 password flow).",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponseDTO:
    """
    Autentica a un empleado y devuelve un token de acceso.

    - **username**: correo electrónico registrado del empleado.
    - **password**: contraseña en texto plano.

    El token JWT devuelto debe enviarse en las peticiones protegidas como:
        Authorization: Bearer <access_token>
    """
    email = form_data.username
    password = form_data.password

    # ── 1. Buscar al empleado por email ──────────────────────────────
    empleado = db.query(Empleado).filter(Empleado.email == email).first()
    if empleado is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    # ── 2. Verificar que el empleado esté activo ─────────────────────
    if not empleado.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado. Contacte al administrador.",
        )

    # ── 3. Verificar la contraseña ──────────────────────────────────
    if not verify_password(password, empleado.password_bash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    # ── 4. Crear y devolver el token JWT ────────────────────────────
    access_token = create_access_token(data={"sub": empleado.email})
    return TokenResponseDTO(access_token=access_token)


@router.get(
    "/me",
    response_model=EmpleadoResponseDTO,
    summary="Obtener perfil del usuario autenticado",
    description="Devuelve la información del empleado que inició sesión (requiere token JWT).",
)
def get_me(
    current_user: Empleado = Depends(get_current_user),
) -> EmpleadoResponseDTO:
    """
    Devuelve los datos del empleado autenticado.

    Requiere el token JWT en el header:
        Authorization: Bearer <access_token>

    El token se obtiene llamando a POST /auth/login.
    """
    return current_user