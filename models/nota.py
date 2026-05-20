from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Lo que el usuario nos envía al crear o actualizar una nota
class NotaEntrada(BaseModel):
    titulo: str = Field(min_length=1, max_length=100)
    contenido: str = Field(min_length=1)

# Lo que la API devuelve (incluye metadatos)
class NotaSalida(BaseModel):
    id: int
    titulo: str
    contenido: str
    creada_en: datetime
    usuario_id: str  # Guardaremos el email del usuario para saber de quién es