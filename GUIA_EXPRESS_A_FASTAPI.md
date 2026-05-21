# 🔁 Node.js/Express → Python/FastAPI
### Guía de transición con ejemplos reales del proyecto `lab-web-py-ai-api`

> **Cómo leer esta guía:** cada sección muestra primero cómo lo harías en Node/Express, luego el equivalente exacto en FastAPI, y una nota que explica el *por qué* del cambio.

---

## 0. Mentalidad previa: ¿Qué cambia de verdad?

| En Node/Express... | En Python/FastAPI... |
|---|---|
| Tipas *cuando quieres* (o no tipas) | El tipado es parte del framework |
| Validas el body manualmente o con Zod/Joi | El propio esquema **es** la validación |
| Documentas con Swagger a mano | La documentación se genera **sola** en `/docs` |
| Los middlewares se encadenan con `next()` | Las dependencias se *inyectan* como argumentos |
| Gestionas errores en cada middleware | FastAPI lanza errores HTTP automáticamente si falla la validación |

---

## 1. Setup del proyecto

### Node/Express

```bash
npm init -y
npm install express dotenv bcryptjs jsonwebtoken
```

```js
// index.js
const express = require('express')
const app = express()

app.use(express.json()) // sin esto, req.body es undefined

app.listen(3000, () => console.log('Servidor en puerto 3000'))
```

### Python/FastAPI

```bash
pip install fastapi uvicorn python-dotenv passlib[bcrypt] python-jose
```

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

# No necesitas "app.use(express.json())" — FastAPI parsea JSON automáticamente

# Para arrancar:
# uvicorn main:app --reload
```

> **Nota:** `uvicorn --reload` es tu `nodemon`. El `--reload` es el equivalente al watch mode.

---

## 2. Variables de entorno

### Node/Express

```js
// .env
SECRET_JWT=supersecret

// config.js
require('dotenv').config()
const SECRET = process.env.SECRET_JWT
```

### Python/FastAPI

```python
# .env
SECRET_JWT=supersecret

# config.py
from dotenv import load_dotenv
import os

load_dotenv()
SECRET = os.getenv("SECRET_JWT")
```

> **Nota:** Exactamente el mismo concepto, diferente sintaxis. `process.env.X` → `os.getenv("X")`.

---

## 3. Routers / Modularización

### Node/Express

```js
// routers/notas.js
const router = require('express').Router()

router.get('/', (req, res) => { ... })
router.post('/', (req, res) => { ... })

module.exports = router

// app.js
const notasRouter = require('./routers/notas')
app.use('/notas', notasRouter)
```

### Python/FastAPI

```python
# routers/notas.py
from fastapi import APIRouter

router = APIRouter()

@router.get("")
def listar_notas(): ...

@router.post("")
def crear_nota(): ...

# main.py
from routers import notas
app.include_router(notas.router, prefix="/notas")
```

> **Nota:** `express.Router()` → `APIRouter()`. `app.use()` → `app.include_router()`. El `prefix` en FastAPI equivale al primer argumento de `app.use()`.

---

## 4. Endpoints y extracción de datos

### 4a. Parámetros de ruta (`:id`)

#### Node/Express

```js
router.get('/:id', (req, res) => {
  const id = parseInt(req.params.id)
  res.json({ id })
})
```

#### Python/FastAPI

```python
@router.get("/{id}")
def obtener_nota(id: int):  # FastAPI convierte el string a int automáticamente
    return {"id": id}
```

> **Nota:** `:id` → `{id}`. En vez de `req.params.id`, lo declaras como **argumento de la función**. El `int` hace que FastAPI rechace peticiones si mandas algo que no es un número.

---

### 4b. Query strings (`?q=algo`)

#### Node/Express

```js
router.get('/', (req, res) => {
  const busqueda = req.query.q || ''
  res.json({ busqueda })
})
```

#### Python/FastAPI

```python
@router.get("")
def listar_notas(q: str = ""):  # Si no llega, vale cadena vacía
    return {"busqueda": q}
```

> **Nota:** `req.query.q` → parámetro de función con el mismo nombre que el query param. El valor por defecto (`= ""`) reemplaza el `|| ''` de JS.

---

### 4c. Body del request

#### Node/Express

```js
// Con Zod para validar
const { z } = require('zod')
const NotaSchema = z.object({
  titulo: z.string().min(3).max(100),
  contenido: z.string().min(10)
})

router.post('/', (req, res) => {
  const result = NotaSchema.safeParse(req.body)
  if (!result.success) return res.status(422).json(result.error)

  const { titulo, contenido } = result.data
  res.status(201).json({ titulo, contenido })
})
```

#### Python/FastAPI

```python
# models/nota.py — el esquema ES la validación
from pydantic import BaseModel, Field

class NotaEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=100)
    contenido: str = Field(min_length=10)

# routers/notas.py
@router.post("", status_code=201)
def crear_nota(nota: NotaEntrada):  # si el body no cumple, FastAPI devuelve 422 solo
    return {"titulo": nota.titulo, "contenido": nota.contenido}
```

> **Nota:** En Node necesitas instanciar Zod, llamar `.safeParse()` y manejar el error tú. En FastAPI, declarar el tipo `NotaEntrada` como argumento **ya es** la validación. Si falla, el 422 es automático.

---

## 5. Respuestas HTTP

### Node/Express

```js
res.status(201).json({ mensaje: 'Creado' })
res.status(404).json({ error: 'No encontrado' })
res.status(200).json(datos)
```

### Python/FastAPI

```python
from fastapi import HTTPException

# Éxito con status code personalizado — va en el decorador
@router.post("", status_code=201)
def crear(): return {"mensaje": "Creado"}

# Éxito normal (200 por defecto)
@router.get("")
def listar(): return datos

# Error — lanzas una excepción, no haces return
raise HTTPException(status_code=404, detail="No encontrado")
```

> **Nota:** El 200 es el default, igual que en Express. Para errores, en vez de `res.status(X).json(...)` lanzas una `HTTPException`. Esto puede pasarse desde cualquier parte del código, no solo en el handler.

---

## 6. Middlewares → Dependencies (`Depends`)

Esta es la diferencia más importante del ecosistema.

### Node/Express

```js
// El middleware verifica el token y muta req
const protect = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1]
  if (!token) return res.status(401).json({ error: 'Sin token' })

  try {
    const decoded = jwt.verify(token, process.env.SECRET_JWT)
    req.user = decoded.email  // lo pegas en req para que el siguiente lo use
    next()
  } catch {
    res.status(401).json({ error: 'Token inválido' })
  }
}

// Lo aplicas ruta a ruta
router.get('/notas', protect, (req, res) => {
  const email = req.user  // lo sacas de req
  res.json({ email })
})
```

### Python/FastAPI

```python
# auth/jwt.py — la dependencia devuelve el valor directamente
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
        return email  # esto es lo que se inyecta en el endpoint
    except:
        raise HTTPException(status_code=401, detail="Token inválido")

# routers/notas.py — el usuario llega como argumento, no como req.user
@router.get("")
def listar_notas(usuario: str = Depends(obtener_usuario_actual)):
    return {"email": usuario}  # ya lo tienes limpio, sin tocar req
```

> **Nota:** El flujo mental es distinto. En Express piensas *"el middleware ejecuta antes y me pasa algo en req"*. En FastAPI piensas *"esta función necesita X, y para obtener X se ejecuta esta otra función"*. Es más declarativo.
>
> La ventaja: puedes reutilizar `Depends(obtener_usuario_actual)` en **cualquier** endpoint sin tocar una lista de middlewares ni el objeto `req`.

---

## 7. Hashing de contraseñas

### Node/Express

```js
const bcrypt = require('bcryptjs')

// Al registrar
const hash = await bcrypt.hash(password, 10)

// Al hacer login
const esValida = await bcrypt.compare(password, hashGuardado)
if (!esValida) return res.status(401).json({ error: 'Credenciales inválidas' })
```

### Python/FastAPI

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

# Al registrar
hash = pwd_context.hash(password)

# Al hacer login
es_valida = pwd_context.verify(password, hash_guardado)
if not es_valida:
    raise HTTPException(status_code=401, detail="Credenciales inválidas")
```

> **Nota:** `bcryptjs` → `passlib`. La API es casi idéntica: `hash()` para encriptar, `verify()` / `compare()` para comprobar.

---

## 8. JWT

### Node/Express

```js
const jwt = require('jsonwebtoken')

// Generar
const token = jwt.sign({ email }, process.env.SECRET_JWT, { expiresIn: '1h' })

// Verificar
const payload = jwt.verify(token, process.env.SECRET_JWT)
const email = payload.email
```

### Python/FastAPI

```python
from jose import jwt
from datetime import datetime, timedelta

# Generar
payload = {"sub": email, "exp": datetime.utcnow() + timedelta(minutes=60)}
token = jwt.encode(payload, SECRET, algorithm="HS256")

# Verificar
payload = jwt.decode(token, SECRET, algorithms=["HS256"])
email = payload.get("sub")
```

> **Nota:** El claim estándar para el "sujeto" del token en JWT es `sub` (subject). En Node muchas veces usas el nombre que quieras, pero en Python/JOSE es buena práctica usar `sub`. La lógica es idéntica.

---

## 9. Variables globales (simulando DB en memoria)

### Node/Express

```js
// Fuera de los handlers, en el módulo
let usuarios = []
let notas = []

// Dentro del handler
usuarios.push({ email, hash })
```

### Python/FastAPI

```python
# A nivel de módulo
db_usuarios = []
db_notas = []

# Dentro de una función, si solo lees → sin problema
def listar(): return db_notas

# Si modificas la lista → también sin problema (append muta el objeto)
def crear(nota): db_notas.append(nota)

# ⚠️ Si reasignas la variable (caso raro) → necesitas `global`
contador = 0
def incrementar():
    global contador  # solo si haces contador = contador + 1
    contador += 1
```

> **Nota:** En JS puedes mutar arrays globales desde cualquier función sin problema. En Python igual, excepto si **reasignas** la variable (la apuntas a otro objeto). Si solo haces `.append()`, no necesitas `global`.

---

## 10. Swagger / Documentación automática

### Node/Express

```js
// Necesitas instalar y configurar swagger-jsdoc + swagger-ui-express
// Y documentar cada ruta con comentarios JSDoc manualmente 😩
```

### Python/FastAPI

```python
# No haces nada. Solo arranca el servidor y visita:
# http://localhost:8000/docs   → Swagger UI interactivo
# http://localhost:8000/redoc  → Redoc (alternativa más limpia)
```

> **Nota:** FastAPI genera la documentación a partir de tus tipos Pydantic y las firmas de las funciones. Es probablemente la mayor ventaja de DX que tiene sobre Express.

---

## Resumen rápido (chuleta final)

| Acción | Express.js | FastAPI |
|---|---|---|
| Leer param de ruta | `req.params.id` | argumento `id` en la función |
| Leer query string | `req.query.q` | argumento `q` en la función |
| Leer body | `req.body.campo` | `nota.campo` (modelo Pydantic) |
| Validar body | Zod / Joi manual | Pydantic automático |
| Error HTTP | `res.status(X).json(...)` | `raise HTTPException(status_code=X)` |
| Éxito con status | `res.status(201).json(...)` | `status_code=201` en el decorador |
| Auth middleware | `router.get('/', protect, handler)` | `usuario = Depends(obtener_usuario_actual)` |
| Usuario autenticado | `req.user` | argumento inyectado directamente |
| Variables de entorno | `process.env.VAR` | `os.getenv("VAR")` |
| Arrancar servidor | `nodemon index.js` | `uvicorn main:app --reload` |
| Documentación API | Manual con swagger-jsdoc | Automática en `/docs` |

---

*Basado en el proyecto `lab-web-py-ai-api` — Ironhack Full Stack JS → Python/AI track*