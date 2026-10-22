"""Reglas de puntuación del Yahtzee.

Cada categoría se implementa como una función pura `valores -> puntos` y se
registra en `REGLAS`. Añadir una variante de reglas (por ejemplo, aceptar un
Yahtzee como full) consiste en sustituir una entrada del diccionario, sin tocar
el motor ni las estrategias.

Variante adoptada: la clásica. El full exige la combinación exacta 3+2; un
Yahtzee (cinco iguales) no puntúa como full.
"""

from __future__ import annotations

from collections import Counter
from functools import partial
from typing import Callable, Sequence

Valores = Sequence[int]
Regla = Callable[[Valores], int]

# --- Sección superior -------------------------------------------------------
UNOS = "Unos"
DOSES = "Doses"
TRESES = "Treses"
CUATROS = "Cuatros"
CINCOS = "Cincos"
SEISES = "Seises"

# --- Sección inferior -------------------------------------------------------
TRIO = "Trio"
POKER = "Poker"
FULL = "Full"
ESCALERA_CORTA = "Escalera corta"
ESCALERA_LARGA = "Escalera larga"
YAHTZEE = "Yahtzee"
CHANCE = "Chance"

SUPERIOR: tuple[str, ...] = (UNOS, DOSES, TRESES, CUATROS, CINCOS, SEISES)
INFERIOR: tuple[str, ...] = (TRIO, POKER, FULL, ESCALERA_CORTA, ESCALERA_LARGA, YAHTZEE, CHANCE)
CATEGORIAS: tuple[str, ...] = SUPERIOR + INFERIOR

CARA_OBJETIVO: dict[str, int] = {UNOS: 1, DOSES: 2, TRESES: 3, CUATROS: 4, CINCOS: 5, SEISES: 6}

BONO_SUPERIOR = 35
UMBRAL_BONO = 63
MAXIMO_POR_CATEGORIA_SUPERIOR = 5 * 6

# Puntaje máximo alcanzable en cada categoría. Se usa para decidir qué casilla
# conviene sacrificar cuando el turno no da puntos en ninguna.
PUNTAJE_MAXIMO: dict[str, int] = {
    UNOS: 5,
    DOSES: 10,
    TRESES: 15,
    CUATROS: 20,
    CINCOS: 25,
    SEISES: 30,
    TRIO: 30,
    POKER: 30,
    FULL: 25,
    ESCALERA_CORTA: 30,
    ESCALERA_LARGA: 40,
    YAHTZEE: 50,
    CHANCE: 30,
}

# Categorías de puntaje alto y baja probabilidad: gastarlas en cero cuesta caro.
ESCASAS: frozenset[str] = frozenset({POKER, FULL, ESCALERA_CORTA, ESCALERA_LARGA, YAHTZEE})


# --- Reglas -----------------------------------------------------------------
def _suma_de_cara(valores: Valores, *, cara: int) -> int:
    """Suma los dados que muestran la cara objetivo."""
    return sum(valor for valor in valores if valor == cara)


def _n_iguales(valores: Valores) -> int:
    """Cuántos dados muestra la cara más repetida."""
    return max(Counter(valores).values())


def _trio(valores: Valores) -> int:
    return sum(valores) if _n_iguales(valores) >= 3 else 0


def _poker(valores: Valores) -> int:
    return sum(valores) if _n_iguales(valores) >= 4 else 0


def _full(valores: Valores) -> int:
    return 25 if sorted(Counter(valores).values()) == [2, 3] else 0


def _contiene_consecutivos(valores: Valores, longitud: int) -> bool:
    """Verdadero si la tirada contiene `longitud` valores consecutivos distintos."""
    distintas = set(valores)
    return any(set(range(inicio, inicio + longitud)) <= distintas for inicio in range(1, 7 - longitud + 1))


def _escalera_corta(valores: Valores) -> int:
    return 30 if _contiene_consecutivos(valores, 4) else 0


def _escalera_larga(valores: Valores) -> int:
    return 40 if _contiene_consecutivos(valores, 5) else 0


def _yahtzee(valores: Valores) -> int:
    return 50 if _n_iguales(valores) == 5 else 0


def _chance(valores: Valores) -> int:
    return sum(valores)


REGLAS: dict[str, Regla] = {
    UNOS: partial(_suma_de_cara, cara=1),
    DOSES: partial(_suma_de_cara, cara=2),
    TRESES: partial(_suma_de_cara, cara=3),
    CUATROS: partial(_suma_de_cara, cara=4),
    CINCOS: partial(_suma_de_cara, cara=5),
    SEISES: partial(_suma_de_cara, cara=6),
    TRIO: _trio,
    POKER: _poker,
    FULL: _full,
    ESCALERA_CORTA: _escalera_corta,
    ESCALERA_LARGA: _escalera_larga,
    YAHTZEE: _yahtzee,
    CHANCE: _chance,
}


def puntuar(categoria: str, valores: Valores) -> int:
    """Puntaje de una tirada en una categoría.

    Raises:
        ValueError: si la categoría no existe.
    """
    try:
        regla = REGLAS[categoria]
    except KeyError as error:
        raise ValueError(f"Categoria desconocida: {categoria!r}") from error
    return regla(valores)


def es_cinco_iguales(valores: Valores) -> bool:
    """Verdadero si los cinco dados muestran la misma cara."""
    return _n_iguales(valores) == 5
