"""
Módulo de configuración centralizado para Cinetica.

Este módulo proporciona una configuración centralizada y validada para toda la aplicación,
cargando valores de múltiples fuentes en este orden de prioridad:
1. Variables de entorno
2. Archivo .env
3. Valores por defecto

Uso:
    from cinetica.config import settings
    print(settings.LOG_LEVEL)
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent


class LoggingSettings(BaseModel):
    """Configuración del sistema de logging."""

    level: str = Field(
        default="INFO",
        description="Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    file: Optional[Path] = Field(
        default=None,
        description="Ruta opcional para guardar logs en archivo",
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato de los mensajes de log",
    )
    date_format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Formato de fecha en los logs",
    )

    @field_validator("level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida que el nivel de log sea válido."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Nivel de log inválido. Debe ser uno de: {valid_levels}")
        return v.upper()


class PerformanceSettings(BaseModel):
    """Configuración de rendimiento."""

    max_workers: int = Field(
        default=4,
        ge=1,
        le=64,
        description="Número máximo de workers para operaciones paralelas",
    )
    cache_enabled: bool = Field(
        default=True,
        description="Habilitar caché para operaciones frecuentes",
    )
    cache_ttl: int = Field(
        default=300,
        ge=0,
        description="Tiempo de vida de la caché en segundos",
    )


class Settings(BaseSettings):
    """Configuración principal de la aplicación."""

    # Configuración de la aplicación
    debug: bool = Field(
        default=False,
        description="Modo de depuración (habilitar características adicionales)",
    )
    testing: bool = Field(
        default=False,
        description="Modo de pruebas (deshabilitar características que no se necesitan en pruebas)",
    )
    env: str = Field(
        default="production",
        description="Entorno de ejecución (development, testing, production)",
    )

    # Sub-configuraciones
    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Configuración del sistema de logging",
    )
    performance: PerformanceSettings = Field(
        default_factory=PerformanceSettings,
        description="Configuración de rendimiento",
    )

    # Configuración de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":
        """Validaciones adicionales de la configuración."""
        # Ajustar configuración basada en el entorno
        if self.env == "development":
            self.debug = True
            if self.logging.level == "INFO":
                self.logging.level = "DEBUG"
        elif self.env == "testing":
            self.testing = True
            self.debug = True
            self.performance.cache_enabled = False

        # Configurar ruta de logs por defecto si no está especificada
        if self.logging.file is None and not self.testing:
            logs_dir = BASE_DIR / "logs"
            logs_dir.mkdir(exist_ok=True)
            self.logging.file = logs_dir / f"cinetica_{self.env}.log"

        return self


# Cargar configuración
settings = Settings()

# Inicializar logger como None, se configurará cuando se necesite
logger = None

def get_logger():
    """Obtener el logger, inicializándolo si es necesario."""
    global logger
    if logger is None:
        from .logger import setup_logger
        logger = setup_logger(
            "cinetica.config",
            level=settings.logging.level,
            log_file=settings.logging.file,
            log_format=settings.logging.format,
            date_format=settings.logging.date_format,
        )
        
        # Log de la configuración cargada (solo en modo debug o development)
        if settings.debug:
            logger.debug("Configuración cargada: %s", settings.model_dump_json(indent=2))
    
    return logger
