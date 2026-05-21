from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Optional
from pydantic import BaseModel
from auth.jwt import obtener_usuario_actual
from routers.notas import db_notas # Importamos la DB simulada

router = APIRouter(
    prefix="/api",
    tags=["IA"]
)

# --- Modelos de Pydantic ---
class ChatRequest(BaseModel):
    mensaje: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    respuesta: str
    contexto_utilizado: List[str]

# --- Memoria de Chat Simulada ---
# Estructura: { "session_id": [{"role": "user", "content": "..."}, ...] }
historial_chats: Dict[str, List[Dict[str, str]]] = {}

@router.get("/context")
def obtener_contexto(usuario_actual: str = Depends(obtener_usuario_actual)):
    """Describe las capacidades de la IA al agente."""
    mis_notas = [n for n in db_notas if n["usuario_id"] == usuario_actual]
    return {
        "descripcion": "Soy un asistente que tiene acceso a tus notas personales.",
        "total_notas": len(mis_notas),
        "capacidades": ["buscar en notas", "resumir contenido", "responder dudas sobre tus textos"]
    }

@router.get("/search")
def buscar_en_notas(q: str = Query(..., min_length=1), usuario_actual: str = Depends(obtener_usuario_actual)):
    """Busca fragmentos relevantes en las notas del usuario."""
    # Filtramos por usuario y luego por coincidencia de texto
    resultados = [
        n["contenido"] for n in db_notas 
        if n["usuario_id"] == usuario_actual and q.lower() in n["contenido"].lower()
    ]
    return {"query": q, "resultados": resultados}

@router.post("/chat", response_model=ChatResponse)
async def chat_con_ia(request: ChatRequest, usuario_actual: str = Depends(obtener_usuario_actual)):
    """
    Endpoint principal de chat. 
    En un caso real, aquí llamarías a OpenAI/Gemini pasando las notas como contexto.
    """
    # 1. Obtener contexto (notas del usuario)
    contexto = [n["contenido"] for n in db_notas if n["usuario_id"] == usuario_actual]
    contexto_str = "\n".join(contexto)

    # 2. Lógica de respuesta (Simulada)
    # Si el usuario pregunta por algo que está en sus notas:
    respuesta_ia = f"Basándome en tus {len(contexto)} notas, puedo decirte que has mencionado temas relacionados con tu búsqueda. (Simulación de LLM)"
    
    if not contexto:
        respuesta_ia = "Aún no tienes notas creadas. No puedo darte información específica."

    # 3. Guardar en historial
    if request.session_id not in historial_chats:
        historial_chats[request.session_id] = []
    
    historial_chats[request.session_id].append({"role": "user", "content": request.mensaje})
    historial_chats[request.session_id].append({"role": "assistant", "content": respuesta_ia})

    return {
        "respuesta": respuesta_ia,
        "contexto_utilizado": contexto[:2] # Devolvemos un par de ejemplos de notas usadas
    }

@router.get("/chat/history/{session_id}")
def obtener_historial(session_id: str, usuario_actual: str = Depends(obtener_usuario_actual)):
    """Devuelve la conversación de una sesión específica."""
    if session_id not in historial_chats:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    return {"session_id": session_id, "mensajes": historial_chats[session_id]}