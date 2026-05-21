from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime
from models.nota import NotaEntrada, NotaSalida
from auth.jwt import obtener_usuario_actual

router = APIRouter(
    prefix="/notas",
    tags=["Notas"]
)

# Simulación de base de datos (como un array global en Node)
# En Express usarías un let db_notas = [];

# Base de datos simulada para las notas
db_notas = []
id_contador_notas = 1

@router.post("", response_model=NotaSalida, status_code=status.HTTP_201_CREATED)
def crear_nota(nota: NotaEntrada, usuario_actual: str = Depends(obtener_usuario_actual)):
    # Depends(obtener_usuario_actual) es como un Middleware en Express:
    # (req, res, next) => { ... validar JWT y poner el usuario en req.user }
    
    global id_contador_notas
    
    nueva_nota = {
        "id": id_contador_notas,
        "titulo": nota.titulo,
        "contenido": nota.contenido,
        "creada_en": datetime.now(),
        "usuario_id": usuario_actual  # El email que sacamos del token JWT
    }
    
    db_notas.append(nueva_nota)
    id_contador_notas += 1
    return nueva_nota


@router.get("", response_model=list[NotaSalida])
def listar_notas(buscar: Optional[str] = None, usuario_actual: str = Depends(obtener_usuario_actual)):
    # 1. Filtramos para que SOLO devuelva las notas del usuario autenticado
    mis_notas = [n for n in db_notas if n["usuario_id"] == usuario_actual]
    
    # 2. Si pasan el query param ?buscar=algo, filtramos por texto
    if buscar:
        mis_notas = [
            n for n in mis_notas 
            if buscar.lower() in n["titulo"].lower() or buscar.lower() in n["contenido"].lower()
        ]
        
    return mis_notas


@router.get("/{id}", response_model=NotaSalida)
def obtener_nota(id: int, usuario_actual: str = Depends(obtener_usuario_actual)):
    for nota in db_notas:
        if nota["id"] == id:
            # Verificamos si la nota le pertenece al usuario
            if nota["usuario_id"] != usuario_actual:
                raise HTTPException(status_code=403, detail="No tienes permisos para ver esta nota")
            return nota
            
    raise HTTPException(status_code=404, detail="Nota no encontrada")


@router.put("/{id}", response_model=NotaSalida)
def editar_nota(id: int, nota_editada: NotaEntrada, usuario_actual: str = Depends(obtener_usuario_actual)):
    for nota in db_notas:
        if nota["id"] == id:
            if nota["usuario_id"] != usuario_actual:
                raise HTTPException(status_code=403, detail="No tienes permisos para editar esta nota")
            
            # Machacamos los campos
            nota["titulo"] = nota_editada.titulo
            nota["contenido"] = nota_editada.contenido
            return nota
            
    raise HTTPException(status_code=404, detail="Nota no encontrada")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_nota(id: int, usuario_actual: str = Depends(obtener_usuario_actual)):
    global db_notas
    for nota in db_notas:
        if nota["id"] == id:
            if nota["usuario_id"] != usuario_actual:
                raise HTTPException(status_code=403, detail="No tienes permisos para eliminar esta nota")
            
            # La borramos de la lista
            db_notas = [n for n in db_notas if n["id"] != id]
            return
            
    raise HTTPException(status_code=404, detail="Nota no encontrada")