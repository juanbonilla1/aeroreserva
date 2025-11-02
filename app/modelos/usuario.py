from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .base import Base
from datetime import datetime
from passlib.hash import bcrypt

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    telefono = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    es_admin = Column(Boolean, default=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Establece la contraseña hasheada, truncando a 72 bytes si es necesario"""
        if isinstance(password, str):
            # Convertir a bytes
            password_bytes = password.encode('utf-8')
            # Truncar a 72 bytes (límite de bcrypt)
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            # Convertir de vuelta a string
            password = password_bytes.decode('utf-8', errors='ignore')
        
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        """Verifica la contraseña, truncando a 72 bytes si es necesario"""
        if isinstance(password, str):
            # Convertir a bytes
            password_bytes = password.encode('utf-8')
            # Truncar a 72 bytes (límite de bcrypt)
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            # Convertir de vuelta a string
            password = password_bytes.decode('utf-8', errors='ignore')
        
        return bcrypt.verify(password, self.password_hash)