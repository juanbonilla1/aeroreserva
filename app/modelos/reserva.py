from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, String
from datetime import datetime
from .base import Base
from datetime import datetime

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    vuelo_id = Column(Integer, ForeignKey("vuelos.id"))
    num_pasajeros = Column(Integer, default=1)
    precio_total = Column(Integer, default=0)
    pagado = Column(Boolean, default=False)
    estado = Column(String(40), default="Activa")
    codigo_reserva = Column(String(50), unique=True, nullable=False)
    fecha_reserva = Column(DateTime, default=datetime.utcnow)

    # Estas relaciones se configuran después en modelos_base si es necesario
    # usuario = relationship("Usuario", back_populates="reservas")
    # vuelo = relationship("Vuelo")
