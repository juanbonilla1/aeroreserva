from sqlalchemy import Column, Integer, String, Float, JSON, Boolean
from .base import Base

class Vuelo(Base):
    __tablename__ = "vuelos"
    id = Column(Integer, primary_key=True, index=True)
    origen = Column(String(100), nullable=False)
    destino = Column(String(100), nullable=False)
    aerolinea = Column(String(100), nullable=True)
    precio = Column(Integer, nullable=False)
    duracion = Column(String(50), nullable=True)
    horarios = Column(JSON, nullable=True)
    asientos_disponibles = Column(Integer, default=100)
    activo = Column(Boolean, default=True)
