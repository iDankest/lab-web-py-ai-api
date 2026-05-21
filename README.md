![logo_ironhack_blue 7](https://user-images.githubusercontent.com/23629340/40541063-a07a0a8a-601a-11e8-91b5-2f13e4e6b441.png)

# Lab | API IA-ready con autenticación

## Objetivo

Construir una API completa con autenticación JWT y los endpoints listos para ser consumidos por un agente de IA.

---

## Setup

```bash
# fork & clone the repository
cd lab-web-py-ai-api
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-dotenv pydantic[email] python-jose[cryptography] passlib[bcrypt] httpx
pip freeze > requirements.txt
```

```shell
# .env
SECRET_KEY=mi-clave-super-secreta-cambiar-en-produccion
PORT=8000
```

---

## Estructura del proyecto

```
lab-web-py-ai-api/
├── main.py
├── config.py
├── models/
│   ├── usuario.py
│   └── nota.py
├── routers/
│   ├── auth.py
│   ├── notas.py
│   └── ia.py
├── auth/
│   └── jwt.py
└── .env
```

---

## Dominio: sistema de notas con búsqueda IA

Los usuarios pueden crear notas de texto. La API expone endpoints para que un agente de IA pueda:

- Consultar el historial de notas de un usuario
- Buscar notas por contenido
- Chat con contexto de las notas del usuario

---

## Requisitos obligatorios

### Autenticación ✅

- [x] `POST /auth/registro` — registro de usuario
- [x] `POST /auth/login` — devuelve JWT
- [x] Middleware que verifica JWT en rutas protegidas

### CRUD de notas (Protegido) ✅

- [x] `GET /notas` — listar notas del usuario autenticado (con `?buscar=` para filtrar por texto)
- [x] `GET /notas/{id}` — obtener una nota (solo si es del usuario)
- [x] `POST /notas` — crear nota
- [x] `PUT /notas/{id}` — editar nota
- [x] `DELETE /notas/{id}` — eliminar nota

### Endpoints IA

- [ ] `POST /api/chat` — chat con historial por sesión (Pendiente)
- [ ] `GET /api/chat/history/{session_id}` — historial
- [ ] `GET /api/search?q=` — busca en las notas del usuario autenticado
- [ ] `GET /api/context` — describe capacidades de la API

---

## Bonus

- Logging estructurado en JSON para todas las peticiones a `/api/`
- `GET /api/context` incluye el número de notas del usuario autenticado
- Endpoint `POST /api/resumir/{nota_id}` que devuelve una simulación de resumen IA

---

## Cómo ejecutar

```bash
uvicorn main:app --reload
```
