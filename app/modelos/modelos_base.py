from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from .base import Base
from app.config import settings
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
                logger.warning(f"⚠️ Intento {attempt + 1}/{max_retries} falló. Reintentando en {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"❌ No se pudo conectar a BD después de {max_retries} intentos: {e}")
                raise

ENGINE = create_engine_with_retry()
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

def crear_tablas():
    """Crea las tablas y datos iniciales"""
    from .usuario import Usuario
    from .vuelo import Vuelo
    from .reserva import Reserva
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=ENGINE)
    
    db = SessionLocal()
    try:
        # Crear usuario admin si no existe
        admin = db.query(Usuario).filter(Usuario.email == settings.ADMIN_EMAIL).first()
        if not admin:
            # Truncar la contraseña del admin a 72 caracteres
            admin_password = settings.ADMIN_PASSWORD[:72]
            
            admin_user = Usuario(
                nombre="Administrador",
                email=settings.ADMIN_EMAIL,
                telefono="",
                es_admin=True
            )
            admin_user.set_password(admin_password)
            db.add(admin_user)
            db.commit()
            logger.info("✅ Usuario admin creado exitosamente")
        
        # Crear vuelos de ejemplo si no existen
        if db.query(Vuelo).count() == 0:
            vuelos_ejemplo = [
                Vuelo(
                    origen="Bogotá",
                    destino="Medellín",
                    aerolinea="AeroReserva",
                    precio=120,
                    duracion="00:45",
                    asientos_disponibles=50,
                    activo=True
                ),
                Vuelo(
                    origen="Bogotá",
                    destino="Cali",
                    aerolinea="AeroReserva",
                    precio=140,
                    duracion="01:05",
                    asientos_disponibles=60,
                    activo=True
                ),
                Vuelo(
                    origen="Cartagena",
                    destino="Bogotá",
                    aerolinea="AeroReserva",
                    precio=160,
                    duracion="01:10",
                    asientos_disponibles=80,
                    activo=True
                ),
                Vuelo(
                    origen="Medellín",
                    destino="Cartagena",
                    aerolinea="AeroReserva",
                    precio=180,
                    duracion="01:20",
                    asientos_disponibles=70,
                    activo=True
                ),
                Vuelo(
                    origen="Cali",
                    destino="San Andrés",
                    aerolinea="AeroReserva",
                    precio=250,
                    duracion="02:00",
                    asientos_disponibles=90,
                    activo=True
                )
            ]
            db.add_all(vuelos_ejemplo)
            db.commit()
            logger.info("✅ Vuelos de ejemplo creados exitosamente")
        
        logger.info("✅ Tablas y datos iniciales creados exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        db.rollback()
    finally:
        db.close()