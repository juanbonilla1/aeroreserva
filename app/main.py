import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="AeroReserva - Sistema de Reserva de Vuelos",
    description="Plataforma para reservar vuelos nacionales e internacionales",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    logger.info("✅ Archivos estáticos montados correctamente")
except Exception as e:
    logger.error(f"⚠️ Error montando archivos estáticos: {e}")

try:
    from app.rutas import ruta_vuelos, ruta_auth, ruta_reservas, ruta_admin
    app.include_router(ruta_vuelos.router, tags=["Vuelos"])
    app.include_router(ruta_auth.router, tags=["Autenticación"])
    app.include_router(ruta_reservas.router, tags=["Reservas"])
    app.include_router(ruta_admin.router, tags=["Admin"])
    logger.info("✅ Todas las rutas cargadas correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando rutas: {e}")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Iniciando aplicación AeroReserva...")
    try:
        from app.modelos.modelos_base import crear_tablas
        crear_tablas()
        logger.info("✅ Base de datos inicializada correctamente")
        logger.info("🌐 Aplicación disponible en http://localhost:8000")
    except Exception as e:
        logger.error(f"❌ Error durante el startup: {e}")
        raise

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/vuelos")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "aeroreserva",
        "version": "1.0.0"
    }