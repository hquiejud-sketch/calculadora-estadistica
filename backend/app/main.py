"""Punto de entrada de la API.

Desarrollo:  uvicorn app.main:app --reload --port 8000
Documentación interactiva: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .database import iniciar_db
from .rutas import analisis, historial, ia


@asynccontextmanager
async def ciclo_de_vida(_app):
    iniciar_db()
    print(f"[OK] SQLite listo en {config.DB_PATH}")
    print("[OK] Gemini configurado" if config.ia_configurada() else "[!] Sin clave de Gemini: el tutor usara modo local")
    yield


app = FastAPI(title="Calculadora Estadística API", version="1.0.0", lifespan=ciclo_de_vida)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(analisis.router)
app.include_router(ia.router)
app.include_router(historial.router)


@app.get("/api/salud")
def salud():
    return {"ok": True, "ia": "gemini" if config.ia_configurada() else "local",
            "modelo": config.GEMINI_MODEL, "base_datos": "sqlite"}


# Si el frontend ya fue compilado (npm run build), FastAPI también lo sirve.
if config.FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=config.FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{ruta:path}", include_in_schema=False)
    def frontend(ruta: str):
        archivo = config.FRONTEND_DIST / ruta
        if ruta and archivo.is_file():
            return FileResponse(archivo)
        return FileResponse(config.FRONTEND_DIST / "index.html")
