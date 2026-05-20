from pydantic import BaseModel, EmailStr, Field

class UsuarioRegistro(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str