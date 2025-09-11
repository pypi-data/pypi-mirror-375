"""
Módulo optimizado para Movimiento Rectilíneo Uniformemente Variado (MRUV).

Este módulo proporciona una implementación optimizada para cálculos de MRUV
con soporte para operaciones vectorizadas y caché de resultados.
"""

from typing import Union, Optional, Tuple, List, Dict, Any
import numpy as np
from functools import lru_cache
from numba import njit, float64, vectorize
import math

from ...units import ureg, Q_
from ..base_movimiento import Movimiento
from ...optimizacion import (
    vectorizar_funcion,
    optimizar_con_jit,
    cachear_resultados,
    optimizar_unidades,
)

# Constantes para cálculos
ePSILON = 1e-10  # Para comparaciones de punto flotante

# Funciones optimizadas con JIT
@njit(float64(float64, float64, float64, float64), cache=True)
def _calcular_posicion_jit(x0: float, v0: float, a: float, t: float) -> float:
    """Calcula la posición usando JIT para optimización."""
    return x0 + v0 * t + 0.5 * a * t**2

@njit(float64(float64, float64, float64), cache=True)
def _calcular_velocidad_jit(v0: float, a: float, t: float) -> float:
    """Calcula la velocidad usando JIT para optimización."""
    return v0 + a * t

@vectorize([float64(float64, float64, float64, float64)], cache=True)
def _calcular_posicion_vectorizada(x0: float, v0: float, a: float, t: float) -> float:
    """Versión vectorizada del cálculo de posición."""
    return x0 + v0 * t + 0.5 * a * t**2

class MovimientoRectilineoUniformementeVariadoOptimizado(Movimiento):
    """
    Implementación optimizada de Movimiento Rectilíneo Uniformemente Variado (MRUV).
    
    Esta versión incluye optimizaciones como:
    - Operaciones vectorizadas con NumPy
    - Caché de resultados frecuentes
    - Compilación JIT para funciones críticas
    - Manejo eficiente de unidades
    """
    
    def __init__(
        self,
        posicion_inicial: Union[float, Q_] = 0.0,
        velocidad_inicial: Union[float, Q_] = 0.0,
        aceleracion_inicial: Union[float, Q_] = 0.0,
    ) -> None:
        """
        Inicializa el objeto MRUV optimizado.
        
        Args:
            posicion_inicial: Posición inicial (m o Q_)
            velocidad_inicial: Velocidad inicial (m/s o Q_)
            aceleracion_inicial: Aceleración constante (m/s² o Q_)
        """
        # Convertir a cantidades de Pint si es necesario
        if not isinstance(posicion_inicial, Q_):
            posicion_inicial = Q_(posicion_inicial, 'm')
        if not isinstance(velocidad_inicial, Q_):
            velocidad_inicial = Q_(velocidad_inicial, 'm/s')
        if not isinstance(aceleracion_inicial, Q_):
            aceleracion_inicial = Q_(aceleracion_inicial, 'm/s^2')
            
        # Almacenar las cantidades con unidades
        self._posicion_inicial = posicion_inicial
        self._velocidad_inicial = velocidad_inicial
        self._aceleracion_inicial = aceleracion_inicial
        
        # Almacenar valores numéricos para cálculos rápidos
        self._x0 = float(self._posicion_inicial.magnitude)
        self._v0 = float(self._velocidad_inicial.magnitude)
        self._a = float(self._aceleracion_inicial.magnitude)
        
        # Cache para resultados frecuentes
        self._cache: Dict[str, Any] = {}
    
    @property
    def posicion_inicial(self) -> Q_:
        return self._posicion_inicial
    
    @property
    def velocidad_inicial(self) -> Q_:
        return self._velocidad_inicial
    
    @property
    def aceleracion_inicial(self) -> Q_:
        return self._aceleracion_inicial
    
    @vectorizar_funcion
    @cachear_resultados(maxsize=1024)
    def _calcular_posicion(self, tiempo: float) -> float:
        """Función interna optimizada para calcular posición."""
        return _calcular_posicion_jit(self._x0, self._v0, self._a, tiempo)
    
    def posicion(self, tiempo: Union[float, np.ndarray, Q_]) -> Q_:
        """
        Calcula la posición en un tiempo dado.
        
        Args:
            tiempo: Tiempo transcurrido (s, Q_ o array de tiempos)
            
        Returns:
            Posición como Quantity con unidades de longitud
            
        Raises:
            ValueError: Si algún tiempo es negativo
        """
        import numpy as np
        
        if isinstance(tiempo, Q_):
            t = tiempo.to('s').magnitude
        else:
            t = np.asarray(tiempo)
            tiempo = Q_(tiempo, 's')
        
        # Validar que no haya tiempos negativos
        if np.any(t < 0):
            raise ValueError("El tiempo no puede ser negativo.")
            
        # Calcular posición
        resultado = self._calcular_posicion(t)
        
        # Devolver con las unidades apropiadas
        return Q_(resultado, self._posicion_inicial.units)
    
    @vectorizar_funcion
    @cachear_resultados(maxsize=1024)
    def _calcular_velocidad(self, tiempo: float) -> float:
        """Función interna optimizada para calcular velocidad."""
        return _calcular_velocidad_jit(self._v0, self._a, tiempo)
    
    def velocidad(self, tiempo: Union[float, np.ndarray, Q_]) -> Q_:
        """
        Calcula la velocidad en un tiempo dado.
        
        Args:
            tiempo: Tiempo transcurrido (s, Q_ o array de tiempos)
            
        Returns:
            Velocidad como Quantity con unidades de velocidad
            
        Raises:
            ValueError: Si algún tiempo es negativo
        """
        import numpy as np
        
        if isinstance(tiempo, Q_):
            t = tiempo.to('s').magnitude
        else:
            t = np.asarray(tiempo)
            tiempo = Q_(tiempo, 's')
            
        # Validar que no haya tiempos negativos
        if np.any(t < 0):
            raise ValueError("El tiempo no puede ser negativo.")
            
        # Calcular velocidad
        resultado = self._calcular_velocidad(t)
        
        # Devolver con las unidades apropiadas
        return Q_(resultado, self._velocidad_inicial.units)
    
    def velocidad_sin_tiempo(self, posicion_final: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad final sin conocer el tiempo.
        
        Args:
            posicion_final: Posición final (m o Q_)
            
        Returns:
            Velocidad final en m/s
        """
        # Convertir a magnitud si es necesario
        if isinstance(posicion_final, Q_):
            xf = posicion_final.to('m').magnitude
        else:
            xf = posicion_final
        
        # Calcular usando la ecuación v² = v₀² + 2aΔx
        delta_x = xf - self._x0
        v_squared = self._v0**2 + 2 * self._a * delta_x
        
        # Manejar casos especiales
        if abs(self._a) < ePSILON:  # MRU
            return abs(self._v0) * (self._velocidad_inicial.units)
            
        if v_squared < 0:
            raise ValueError("No existe solución real para los parámetros dados.")
            
        # Determinar el signo de la velocidad
        v = math.sqrt(v_squared)
        if abs(self._a) > ePSILON:
            tiempo_cruce = -self._v0 / self._a
            if tiempo_cruce > 0:  # Hay cambio de dirección
                if self._a > 0:
                    v = -v if tiempo_cruce > 0 else v
                else:
                    v = v if tiempo_cruce > 0 else -v
        
        return v * (self._velocidad_inicial.units)
    
    def tiempo_por_posicion(self, posicion_final: Union[float, Q_]) -> List[Q_]:
        """
        Calcula los tiempos en los que se alcanza una posición dada.
        
        Args:
            posicion_final: Posición objetivo (m o Q_)
            
        Returns:
            Lista de tiempos en segundos donde se alcanza la posición
        """
        # Convertir a magnitud si es necesario
        if isinstance(posicion_final, Q_):
            xf = posicion_final.to('m').magnitude
        else:
            xf = posicion_final
        
        # Caso MRU (aceleración cero)
        if abs(self._a) < ePSILON:
            if abs(self._v0) < ePSILON:  # Velocidad cero
                if abs(self._x0 - xf) < ePSILON:  # Siempre en la posición
                    return [0.0 * ureg.second]
                else:  # Nunca alcanza la posición
                    return []
            else:  # MRU simple
                t = (xf - self._x0) / self._v0
                return [t * ureg.second] if t >= 0 else []
        
        # Caso MRUV (aceleración no nula)
        # Resolver la ecuación cuadrática: 0.5*a*t² + v0*t + (x0 - xf) = 0
        a = 0.5 * self._a
        b = self._v0
        c = self._x0 - xf
        
        discriminante = b**2 - 4*a*c
        
        if discriminante < 0:
            return []  # No hay soluciones reales
            
        sqrt_disc = math.sqrt(discriminante)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        
        # Filtrar tiempos negativos y ordenar
        tiempos = [t for t in [t1, t2] if t >= 0]
        tiempos = sorted(list(set(tiempos)))  # Eliminar duplicados
        
        return [t * ureg.second for t in tiempos]
    
    def aceleracion(self, tiempo: Union[float, Q_, None] = None) -> Q_:
        """
        Devuelve la aceleración constante del movimiento.
        
        En MRUV, la aceleración es constante, por lo que este método ignora el parámetro tiempo.
        
        Args:
            tiempo: Parámetro opcional ignorado, presente por compatibilidad con la clase base.
            
        Returns:
            La aceleración constante del movimiento.
        """
        return self._aceleracion_inicial
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"posicion_inicial={self._posicion_inicial}, "
            f"velocidad_inicial={self._velocidad_inicial}, "
            f"aceleracion_inicial={self._aceleracion_inicial}"
            ")"
        )

# Alias para compatibilidad
MRUVOptimizado = MovimientoRectilineoUniformementeVariadoOptimizado
