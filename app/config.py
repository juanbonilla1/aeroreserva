import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "super_secret_dev_key")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "jwt_dev_secret")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "usuario_vuelos")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "123456")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "reserva_vuelos_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLIC_KEY: str = os.getenv("STRIPE_PUBLIC_KEY", "")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@aeroreserva.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()