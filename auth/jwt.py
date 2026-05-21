from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from config import settings

# Configuración de encriptación (Como usar la librería 'bcrypt' en Node)

# Configuración de Passlib para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obtener_password_encriptada(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password_plana: str, password_encriptada: str) -> bool:
    return pwd_context.verify(password_plana, password_encriptada)

def crear_token_acceso(datos: dict, expires_delta: Optional[timedelta] = None) -> str:
    datos_a_encriptar = datos.copy()
    if expires_delta:
        tiempo_expiracion = datetime.now(timezone.utc) + expires_delta
    else:
        tiempo_expiracion = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    datos_a_encriptar.update({"exp": tiempo_expiracion})
    token_jwt = jwt.encode(datos_a_encriptar, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token_jwt

# Esta línea configura la extracción del token del header "Authorization: Bearer <TOKEN>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> str:
    # Esta es nuestra función "Middleware". 
    # Si falla, lanza un 401 automático, igual que un middleware de Passport o JWT en Express.
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Desencriptamos el token con nuestra clave secreta
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credenciales_exception
        return email  # Devolvemos el email del usuario dueño del token
    except JWTError:
        raise credenciales_exception