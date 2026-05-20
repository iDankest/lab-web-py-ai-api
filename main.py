from fastapi import FastAPI
from config import settings

from routers import auth, notas

# Inicializamos FastAPI con el título del laboratorio
app = FastAPI(title="API IA-Ready con Autenticación")

# Conectamos el router de autenticación
app.include_router(auth.router)
app.include_router(notas.router)


@app.get("/")
def home():
    return {
        "message": "Bienvenido a la API IA-Ready de Kilian",
        "docs": "/docs"
    }

# Código para poder arrancar el archivo directamente con 'python main.py' si quieres
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings.PORT), reload=True)