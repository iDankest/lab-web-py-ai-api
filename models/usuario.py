from pydantic import BaseModel, EmailStr

class UsuarioBase(BaseModel):
    email: EmailStr

class UsuarioRegistro(UsuarioBase):
    password: str

class UsuarioLogin(UsuarioBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str