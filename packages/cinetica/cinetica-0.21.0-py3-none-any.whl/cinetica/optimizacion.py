"""
Módulo de optimización numérica para la biblioteca Cinetica.

Este módulo proporciona funciones y decoradores para optimizar el rendimiento
de los cálculos numéricos en la biblioteca.
"""

from functools import lru_cache, wraps
from typing import Callable, TypeVar, Any, Tuple, Union
import numpy as np
from numba import jit, njit, float64, vectorize
import numba
from .units import Q_, ureg

# Type variable para genéricos
T = TypeVar('T')

def vectorizar_funcion(func: Callable[..., T]) -> Callable[..., Union[np.ndarray, T]]:
    """
    Decora una función para que pueda manejar tanto escalares como arrays de NumPy.
    
    Args:
        func: Función a vectorizar. Debe aceptar y retornar valores escalares.
        
    Returns:
        Función que puede manejar arrays de entrada y devuelve arrays de salida.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Convertir entradas a arrays de NumPy si no lo son ya
        args_np = [np.asarray(arg) for arg in args]
        
        # Procesar kwargs
        kwargs_np = {k: np.asarray(v) if isinstance(v, (int, float, list, tuple)) else v 
                    for k, v in kwargs.items()}
        
        # Vectorizar la función
        vectorized_func = np.vectorize(func, otypes=[np.float64])
        return vectorized_func(*args_np, **kwargs_np)
    
    return wrapper

def optimizar_con_jit(func: Callable[..., T]) -> Callable[..., T]:
    """
    Aplica la compilación JIT de Numba a una función para mejorar el rendimiento.
    
    Args:
        func: Función a optimizar con JIT.
        
    Returns:
        Función compilada con Numba.
    """
    return njit(func, cache=True)

def cachear_resultados(maxsize: int = 128) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decora una función para cachear sus resultados y evitar cálculos repetidos.
    
    Args:
        maxsize: Número máximo de entradas en la caché.
        
    Returns:
        Decorador que aplica caché a la función.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cached_func = lru_cache(maxsize=maxsize)(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Convertir arrays de NumPy a tuplas para poder hacer hash
            args_hashable = tuple(tuple(arg) if isinstance(arg, np.ndarray) else arg 
                                for arg in args)
            kwargs_hashable = {k: tuple(v) if isinstance(v, np.ndarray) else v 
                             for k, v in kwargs.items()}
            return cached_func(*args_hashable, **kwargs_hashable)
            
        return wrapper
    return decorator

def optimizar_unidades(func: Callable[..., T]) -> Callable[..., T]:
    """
    Optimiza operaciones con unidades de Pint para mejorar el rendimiento.
    
    Args:
        func: Función que trabaja con cantidades de Pint.
        
    Returns:
        Función optimizada que minimiza la sobrecarga de Pint.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extraer magnitudes y unidades de los argumentos
        magnitudes = []
        unidades = []
        
        for arg in args:
            if hasattr(arg, 'magnitude') and hasattr(arg, 'units'):
                magnitudes.append(arg.magnitude)
                unidades.append(arg.units)
            else:
                magnitudes.append(arg)
                unidades.append(None)
                
        # Llamar a la función con las magnitudes
        resultado = func(*magnitudes, **kwargs)
        
        # Aplicar unidades al resultado si es necesario
        if unidades and any(u is not None for u in unidades):
            # Aquí se podría implementar lógica más sofisticada para determinar
            # las unidades del resultado basado en las unidades de entrada
            return resultado * unidades[0] if unidades[0] else resultado
        return resultado
        
    return wrapper

def optimizar_operaciones_vectoriales():
    """
    Registra funciones vectoriales optimizadas para operaciones comunes.
    """
    # Suma vectorial optimizada
    @vectorize([float64(float64, float64)])
    def suma_vectorial(a, b):
        return a + b
    
    # Producto punto optimizado
    @njit
    def producto_punto(a, b):
        return np.dot(a, b)
    
    # Norma de vector optimizada
    @njit
    def norma_vectorial(v):
        return np.sqrt(np.sum(v**2))
    
    return {
        'suma_vectorial': suma_vectorial,
        'producto_punto': producto_punto,
        'norma_vectorial': norma_vectorial
    }

# Exportar las funciones optimizadas
operaciones_vectoriales = optimizar_operaciones_vectoriales()
suma_vectorial = operaciones_vectoriales['suma_vectorial']
producto_punto = operaciones_vectoriales['producto_punto']
norma_vectorial = operaciones_vectoriales['norma_vectorial']
