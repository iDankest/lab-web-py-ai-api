from fastapi import APIRouter, HTTPException, status
from models.usuario import UsuarioRegistro, UsuarioLogin, Token
from auth.jwt import obtener_password_encriptada, verificar_password, crear_token_acceso

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

# Base de datos simulada en memoria
db_usuarios = []

@router.post("/registro", status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioRegistro):
    # 1. Comprobar si el email ya existe
    for u in db_usuarios:
        if u["email"] == usuario.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
    
    # 2. Encriptar la contraseña antes de guardarla (¡Seguridad ante todo!)
    password_hash = obtener_password_encriptada(usuario.password)
    
    # 3. Guardar el usuario en nuestra "BD"
    nuevo_usuario = {
        "email": usuario.email,
        "password": password_hash
    }
    db_usuarios.append(nuevo_usuario)
    
    return {"message": "Usuario registrado correctamente"}


@router.post("/login", response_model=Token)
def login_usuario(usuario: UsuarioLogin):
    # 1. Buscar al usuario por email
    usuario_encontrado = None
    for u in db_usuarios:
        if u["email"] == usuario.email:
            usuario_encontrado = u
            break
            
    # 2. Si no existe, patada con un 401
    if not usuario_encontrado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
        
    # 3. Verificar si la contraseña coincide con el hash encriptado
    if not verificar_password(usuario.password, usuario_encontrado["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
        
    # 4. Si todo está guay, le generamos su preciado token JWT
    # Guardamos el email dentro del token para saber quién es en futuras peticiones
    token_acceso = crear_token_acceso(datos={"sub": usuario_encontrado["email"]})
    
    return {"access_token": token_acceso, "token_type": "bearer"}