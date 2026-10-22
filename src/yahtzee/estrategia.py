"""Estrategias de juego.

Una estrategia decide únicamente en qué categoría se anota el turno. Qué dados
se conservan lo resuelve una política de retención inyectada (ver `retencion`).
Esa separación permite comparar políticas de retención sin tocar las estrategias
y evita duplicar la lógica de decisión.

    aleatoria   elige una casilla libre al azar y no conserva dados
    codiciosa   maximiza el puntaje inmediato
    bono        asegura primero el bono de la sección superior y solo después
                busca el mejor puntaje de la sección inferior
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Sequence

import numpy as np

from .puntuacion import CARA_OBJETIVO, PUNTAJE_MAXIMO, puntuar
from .retencion import PoliticaRetencion, RetencionNula, RetencionPorObjetivo
from .tarjeta import Tarjeta

NOMBRES_ESTRATEGIAS: tuple[str, ...] = ("aleatoria", "codiciosa", "bono")


class Estrategia(ABC):
    """Contrato de una política de decisión."""

    nombre: ClassVar[str] = "base"

    def __init__(self, retencion: PoliticaRetencion | None = None) -> None:
        self.retencion: PoliticaRetencion = retencion or RetencionPorObjetivo()

    @abstractmethod
    def elegir(self, tarjeta: Tarjeta, valores: Sequence[int]) -> str:
        """Categoría en la que se anotará el turno."""

    def retener(self, categoria: str, valores: Sequence[int]) -> tuple[int, ...]:
        """Dados que se conservan antes del siguiente lanzamiento."""
        return self.retencion.dados_a_conservar(categoria, valores)

    def __repr__(self) -> str:
        return f"<{self.nombre}>"


class EstrategiaAleatoria(Estrategia):
    """Elige una casilla libre al azar. Sin retención de dados."""

    nombre = "aleatoria"

    def __init__(self, rng: np.random.Generator | None = None) -> None:
        super().__init__(retencion=RetencionNula())
        self.rng = rng if rng is not None else np.random.default_rng()

    def elegir(self, tarjeta: Tarjeta, valores: Sequence[int]) -> str:
        disponibles = tarjeta.disponibles()
        return disponibles[int(self.rng.integers(len(disponibles)))]


class EstrategiaCodiciosa(Estrategia):
    """Maximiza el puntaje del turno, sin mirar el resto de la partida."""

    nombre = "codiciosa"

    def elegir(self, tarjeta: Tarjeta, valores: Sequence[int]) -> str:
        return max(tarjeta.disponibles(), key=lambda categoria: puntuar(categoria, valores))


class EstrategiaBono(Estrategia):
    """Pondera el avance del bono superior y protege las categorías escasas.

    El atractivo de cada casilla libre se calcula así:

    * se parte del puntaje que daría el turno en esa categoría;
    * si la casilla es de la sección superior y el bono sigue siendo alcanzable,
      el puntaje se multiplica por `factor_bono`, porque cada punto de arriba
      vale también como avance hacia los 35 del bono;
    * si el turno no puntúa, se resta una fracción del puntaje máximo de la
      categoría (`castigo_escaso`), de modo que se sacrifica antes un chance o
      unos doses que un Yahtzee.

    Los valores por defecto salen de una calibración sobre 3000 partidas por
    configuración, descrita en el documento técnico. No son la política óptima:
    la política óptima exige programación dinámica sobre los 252 multiconjuntos
    de cinco dados y queda fuera del alcance de esta actividad.
    """

    nombre = "bono"

    def __init__(
        self,
        factor_bono: float = 2.0,
        castigo_escaso: float = 0.30,
        retencion: PoliticaRetencion | None = None,
    ) -> None:
        super().__init__(retencion=retencion)
        self.factor_bono = factor_bono
        self.castigo_escaso = castigo_escaso

    def elegir(self, tarjeta: Tarjeta, valores: Sequence[int]) -> str:
        falta_bono = tarjeta.falta_bono()
        return max(
            tarjeta.disponibles(),
            key=lambda categoria: self._atractivo(categoria, valores, falta_bono),
        )

    def _atractivo(self, categoria: str, valores: Sequence[int], falta_bono: bool) -> float:
        valor = float(puntuar(categoria, valores))
        if falta_bono and categoria in CARA_OBJETIVO:
            valor *= self.factor_bono
        if valor == 0.0:
            valor -= PUNTAJE_MAXIMO[categoria] * self.castigo_escaso
        return valor


def por_nombre(nombre: str, rng: np.random.Generator | None = None) -> Estrategia:
    """Construye una estrategia a partir de su nombre.

    Raises:
        ValueError: si el nombre no corresponde a ninguna estrategia.
    """
    clave = nombre.strip().lower()
    if clave in {"aleatoria", "random"}:
        return EstrategiaAleatoria(rng)
    if clave in {"codiciosa", "greedy"}:
        return EstrategiaCodiciosa()
    if clave in {"bono", "esperada", "ev"}:
        return EstrategiaBono()
    raise ValueError(f"Estrategia desconocida: {nombre!r}. Opciones: {', '.join(NOMBRES_ESTRATEGIAS)}")
