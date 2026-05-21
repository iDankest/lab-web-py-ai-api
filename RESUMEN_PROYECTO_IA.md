# 📝 Resumen del Proyecto: lab-web-py-ai-api

Este proyecto consiste en una **API RESTful construida con FastAPI (Python)**, diseñada para gestionar un sistema de notas personales con autenticación JWT y capacidades preparadas para agentes de Inteligencia Artificial (AI-ready).

## 🎯 Objetivo

Construir un backend seguro que permita a un usuario (y eventualmente a una IA) gestionar información textual, realizando búsquedas semánticas y manteniendo conversaciones con contexto.

## 🛠️ Stack Tecnológico (y equivalencias con Node.js)

| Tecnología           | Propósito                      | Equivalente en Node.js             |
| :------------------- | :----------------------------- | :--------------------------------- |
| **FastAPI**          | Framework Web                  | Express.js                         |
| **Pydantic**         | Validación de esquemas y tipos | Joi / Zod / TypeScript             |
| **Uvicorn**          | Servidor ASGI                  | Server.js (Node runtime) / Nodemon |
| **JOSE / JWT**       | Seguridad y Tokens             | jsonwebtoken                       |
| **Passlib (Bcrypt)** | Hashing de contraseñas         | bcryptjs                           |
| **Python-dotenv**    | Variables de entorno           | dotenv                             |

## 📂 Estructura y Módulos

1.  **`main.py`**: El "Entry Point". Donde se instancia la app y se montan los routers (similar a `app.use()` en Express).
2.  **`auth/jwt.py`**: Lógica de seguridad. Contiene el "Middleware" de autenticación (`obtener_usuario_actual`) y utilidades para tokens.
3.  **`models/`**: Definición de la forma de los datos.
    - `usuario.py`: Esquemas para registro y login.
    - `nota.py`: Reglas de validación para los datos de las notas (títulos, longitud, etc.).
4.  **`routers/`**: Los controladores de la API.
    - `auth.py`: Endpoints de `/registro` y `/login`.
    - `notas.py`: CRUD completo protegido por JWT.
    - `ia.py`: Lógica de búsqueda y chat (simulada con memoria en sesión).

## 🔐 Lógica de Autenticación

- **Hashing**: Se usa Bcrypt para no guardar contraseñas en texto plano.
- **JWT**: Al hacer login, se genera un token que expira en 60 minutos.
- **Dependencias**: Se utiliza el sistema `Depends` de FastAPI. Es el equivalente a los middlewares de Express, pero inyecta el retorno (el email del usuario) directamente en la función del endpoint.

## 🤖 Funcionalidades de IA (AI-Ready)

- **Contexto**: Un endpoint que informa a la IA sobre cuántas notas tiene el usuario.
- **Búsqueda**: Filtrado de notas por coincidencia de texto.
- **Chat con Memoria**: Sistema que guarda el historial de mensajes por `session_id` y utiliza el contenido de las notas del usuario para generar respuestas (Base para un sistema RAG - Retrieval-Augmented Generation).

## 📋 Comparativa Rápida para Desarrolladores JS

### Declaración de Rutas

- **Express**: `router.get('/path', (req, res) => ...)`
- **FastAPI**: `@router.get("/path") def function(): ...`

### Extracción de Datos

- **Express**: `req.body`, `req.params`, `req.query`.
- **FastAPI**: Se declaran como argumentos de la función (`nota: NotaEntrada`, `id: int`, `q: str`).

### Middleware de Seguridad

- **Express**: `router.get('/secret', authMiddleware, controller)`
- **FastAPI**: `def controller(user = Depends(auth_func)):`

## 🚀 Próximos Pasos

1.  **Persistencia**: Cambiar las listas en memoria por una base de datos (PostgreSQL/MongoDB).
2.  **Integración Real**: Conectar `ia.py` con el SDK de Google Generative AI (Gemini) o OpenAI.
3.  **Embeddings**: Implementar búsqueda vectorial para que la IA entienda el "significado" de las notas y no solo palabras clave.

---

_Documento generado para facilitar la transición de conceptos entre ecosistemas de JavaScript y Python._
