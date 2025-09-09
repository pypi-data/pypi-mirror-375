"""
Cinetica - Una librería para cálculos de cinemática

Esta biblioteca proporciona herramientas para cálculos de física, incluyendo:
- Cinemática (movimiento rectilíneo, parabólico, circular, etc.)
- Dinámica (leyes de Newton, fuerzas, trabajo y energía)
- Herramientas de visualización gráfica

La configuración se puede personalizar a través de variables de entorno o un archivo .env.
"""

__version__ = "0.20.0"  # Versión actualizada por la nueva funcionalidad

# Importaciones principales
from .units import ureg, Q_
from .logger import setup_logger, get_logger
from .config import settings as config

# Importar submódulos
from .cinematica import (
    circular,
    espacial,
    oscilatorio,
    parabolico,
    rectilineo,
    relativo,
)
from . import graficos
from . import dinamica

# Configurar logger raíz por defecto
logger = get_logger('cinetica')

__all__ = [
    # Módulos principales
    "circular",
    "espacial",
    "oscilatorio",
    "parabolico",
    "rectilineo",
    "relativo",
    "graficos",
    "dinamica",
    
    # Utilidades
    "setup_logger",
    "get_logger",
    "config",
    "logger",
    "__version__",
]
