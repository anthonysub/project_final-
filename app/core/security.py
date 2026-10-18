"""
Utilidades de seguridad para autenticación JWT.

Funciones puras — no dependen de FastAPI ni de la base de datos.
Se apoyan en las variables de entorno JWT_SECRET_KEY, JWT_ALGORITHM
y ACCESS_TOKEN_EXPIRE_MINUTES definidas en app.core.config.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt

from app.core.config import settings


def hash_password(password: str) -> str:
    """
    Recibe una contraseña en texto plano y devuelve su hash bcrypt.

    Args:
        password: Contraseña en texto plano (ej. "MiClave123").

    Returns:
        String con el hash (ej. "$2b$12$...").

    Ejemplo de uso:
        >>> hash_password("admin123")
        '$2b$12$LJ3m...'
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con un hash bcrypt.

    Args:
        plain_password: Contraseña que ingresó el usuario al hacer login.
        hashed_password: Hash almacenado en la base de datos (campo password_bash).

    Returns:
        True si coinciden, False en caso contrario.

    Ejemplo de uso:
        >>> verify_password("admin123", hash_guardado_en_bd)
        True
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # Hash inválido (no es un hash bcrypt válido) -> nunca coincide
        return False


def create_access_token(data: dict) -> str:
    """
    Crea un token JWT firmado con la clave secreta del proyecto.

    El token incluye:
      - Los datos que recibe en 'data' (típicamente {"sub": email}).
      - Fecha de expiración calculada desde settings.ACCESS_TOKEN_EXPIRE_MINUTES.
      - Fecha de emisión (iat).

    Args:
        data: Diccionario con los claims a incluir en el token.
              La clave "sub" (subject) se usa por convención para el email.

    Returns:
        String con el token JWT codificado.

    Ejemplo de uso:
        >>> create_access_token({"sub": "juan@example.com"})
        'eyJhbGciOiJIUzI1NiIs...'
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica y verifica un token JWT.

    Args:
        token: String del token JWT recibido del cliente.

    Returns:
        Diccionario con los claims del token (incluye "sub", "exp", "iat").

    Raises:
        jwt.JWTError: Si el token expiró, tiene firma inválida o está malformado.
            El llamador (dependencies.py) debe capturar esta excepción
            y convertirla en un HTTPException 401.

    Ejemplo de uso:
        >>> decode_access_token("eyJhbGciOi...")
        {'sub': 'juan@example.com', 'exp': 1721078400, 'iat': 1721076600}
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])