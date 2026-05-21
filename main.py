from fastapi import FastAPI
from routers import auth, notas, ia

# Equivale a: const app = express();
app = FastAPI(
    title="API de Notas con IA",
    description="Laboratorio de Ironhack - W9",
    version="1.0.0"
)

# Equivale a: app.use('/auth', authRouter);
# Aquí centralizamos todas las rutas definidas en la carpeta routers
app.include_router(auth.router)
app.include_router(notas.router)
app.include_router(ia.router)

@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a la API de Notas. Ve a /docs para ver la documentación."
    }