from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .base import Base
from datetime import datetime
import bcrypt as bcrypt_module

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    telefono = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    es_admin = Column(Boolean, default=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        """Establece la contraseña hasheada usando bcrypt directamente"""
        # Convertir a bytes y truncar a 72 bytes (límite de bcrypt)
        password_bytes = password.encode('utf-8')[:72]
        
        # Hashear con bcrypt
        hashed = bcrypt_module.hashpw(password_bytes, bcrypt_module.gensalt())
        
        # Guardar como string
        self.password_hash = hashed.decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verifica la contraseña usando bcrypt directamente"""
        # Convertir a bytes y truncar a 72 bytes
        password_bytes = password.encode('utf-8')[:72]
        
        # Convertir hash guardado a bytes
        hash_bytes = self.password_hash.encode('utf-8')
        
        # Verificar
        return bcrypt_module.checkpw(password_bytes, hash_bytes)