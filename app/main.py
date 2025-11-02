import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AeroReserva - Sistema de Reserva de Vuelos",
    description="Plataforma para reservar vuelos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Montar archivos estáticos
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info("✅ Archivos estáticos montados")

# Importar rutas
try:
    from app.rutas import ruta_vuelos, ruta_auth, ruta_reservas, ruta_admin
    
    app.include_router(ruta_auth.router, tags=["Auth"])
    app.include_router(ruta_vuelos.router, tags=["Vuelos"])
    app.include_router(ruta_reservas.router, tags=["Reservas"])
    app.include_router(ruta_admin.router, tags=["Admin"])
    
    logger.info("✅ Rutas cargadas correctamente")
except Exception as e:
    logger.error(f"❌ Error cargando rutas: {e}")
    raise

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Iniciando AeroReserva...")
    try:
        from app.modelos.modelos_base import crear_tablas
        crear_tablas()
        logger.info("✅ Base de datos inicializada")
        logger.info("🌐 Aplicación en http://localhost:8000")
    except Exception as e:
        logger.error(f"❌ Error en startup: {e}")
        import traceback
        traceback.print_exc()

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/vuelos")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "aeroreserva"}