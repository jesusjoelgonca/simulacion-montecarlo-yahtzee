"""Simulación Montecarlo del juego de Yahtzee.

API pública del paquete:

    >>> from yahtzee import simular
    >>> resultado = simular(10_000, semilla=2026)
    >>> print(resultado.resumen())

Módulos:
    dados           generación de tiradas
    puntuacion      reglas de las trece categorías
    tarjeta         estado de la tarjeta de un jugador
    retencion       políticas de conservación de dados
    estrategia      políticas de decisión
    juego           motor de turnos y partidas
    montecarlo      simulación y estadística
    probabilidades  valores exactos de contraste
"""

from .dados import CARAS, N_DADOS, lanzar
from .estrategia import (
    NOMBRES_ESTRATEGIAS,
    Estrategia,
    EstrategiaAleatoria,
    EstrategiaBono,
    EstrategiaCodiciosa,
    por_nombre,
)
from .juego import JUGADORES, LANZAMIENTOS_POR_TURNO, ResultadoPartida, Turno, jugar_partida, jugar_turno
from .montecarlo import (
    Enfrentamiento,
    ResultadoMontecarlo,
    banda_convergencia,
    curva_convergencia,
    frecuencia_cinco_iguales,
    simular,
    simular_con,
    simular_enfrentamiento,
    simular_estrategias,
    tabla_convergencia,
)
from .probabilidades import (
    distribucion_suma,
    probabilidad_categoria_un_lanzamiento,
    probabilidad_cinco_iguales,
    probabilidad_full_estricto,
    tabla_probabilidades,
)
from .puntuacion import CATEGORIAS, INFERIOR, SUPERIOR, puntuar
from .retencion import PoliticaRetencion, RetencionNula, RetencionPorObjetivo
from .tarjeta import Tarjeta

__version__ = "1.0.0"

__all__ = [
    "CARAS",
    "N_DADOS",
    "lanzar",
    "NOMBRES_ESTRATEGIAS",
    "Estrategia",
    "EstrategiaAleatoria",
    "EstrategiaBono",
    "EstrategiaCodiciosa",
    "por_nombre",
    "JUGADORES",
    "LANZAMIENTOS_POR_TURNO",
    "ResultadoPartida",
    "Turno",
    "jugar_partida",
    "jugar_turno",
    "Enfrentamiento",
    "ResultadoMontecarlo",
    "banda_convergencia",
    "curva_convergencia",
    "frecuencia_cinco_iguales",
    "simular",
    "simular_con",
    "simular_enfrentamiento",
    "simular_estrategias",
    "tabla_convergencia",
    "distribucion_suma",
    "probabilidad_categoria_un_lanzamiento",
    "probabilidad_cinco_iguales",
    "probabilidad_full_estricto",
    "tabla_probabilidades",
    "CATEGORIAS",
    "INFERIOR",
    "SUPERIOR",
    "puntuar",
    "PoliticaRetencion",
    "RetencionNula",
    "RetencionPorObjetivo",
    "Tarjeta",
]
