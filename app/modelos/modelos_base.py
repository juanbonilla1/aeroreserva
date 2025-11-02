from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from .base import Base
from ..config import settings
import time
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    user = settings.POSTGRES_USER
    pwd = settings.POSTGRES_PASSWORD
    host = settings.POSTGRES_HOST
    port = settings.POSTGRES_PORT
    db = settings.POSTGRES_DB
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

def create_engine_with_retry():
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(get_database_url(), echo=False)
            # Test connection
            with engine.connect() as conn:
                pass
            logger.info("✅ Conexión a BD establecida exitosamente")
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"⚠️  Intento {attempt + 1}/{max_retries} falló. Reintentando en {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"❌ No se pudo conectar a BD después de {max_retries} intentos: {e}")
                raise

ENGINE = create_engine_with_retry()
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

def crear_tablas():
    # Import aquí para evitar circularidad
    from .usuario import Usuario
    from .vuelo import Vuelo
    from .reserva import Reserva
    
    Base.metadata.create_all(bind=ENGINE)
    
    # seed admin and sample vuelos
    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.email == settings.ADMIN_EMAIL).first()
        if not admin:
            u = Usuario(nombre="Administrador", email=settings.ADMIN_EMAIL, telefono="", es_admin=True)
            u.set_password(settings.ADMIN_PASSWORD)  # Ahora usa la contraseña truncada
            db.add(u)
            db.commit()
            logger.info("✅ Usuario admin creado exitosamente")
        # Sample vuelos
        if not db.query(Vuelo).first():
            v1 = Vuelo(origen="Bogotá", destino="Medellín", aerolinea="AeroMock", precio=120, duracion="00:45", asientos_disponibles=50)
            v2 = Vuelo(origen="Bogotá", destino="Cali", aerolinea="AeroMock", precio=140, duracion="01:05", asientos_disponibles=60)
            v3 = Vuelo(origen="Cartagena", destino="Bogotá", aerolinea="AeroMock", precio=160, duracion="01:10", asientos_disponibles=80)
            db.add_all([v1,v2,v3])
            db.commit()
            logger.info("✅ Vuelos de ejemplo creados exitosamente")
        logger.info("✅ Tablas y datos iniciales creados exitosamente")
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        # No relanzar para permitir que la app continúe
    finally:
        db.close()
