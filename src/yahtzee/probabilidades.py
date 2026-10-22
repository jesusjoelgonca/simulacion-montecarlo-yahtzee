"""Probabilidades exactas del juego, para contrastar la simulación.

Montecarlo sirve para estimar cantidades sin forma cerrada cómoda. Cuando el
espacio muestral es pequeño (un lanzamiento de cinco dados son 6^5 = 7776 casos),
la probabilidad se calcula por enumeración exacta. Comparar ese valor con la
frecuencia observada es la comprobación empírica de la Ley de los Grandes
Números.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product
from math import comb
from types import MappingProxyType
from typing import Mapping

from .dados import CARAS, N_DADOS
from .puntuacion import CATEGORIAS, puntuar


@lru_cache(maxsize=None)
def _conteo_por_categoria(caras: int = CARAS, n_dados: int = N_DADOS) -> Mapping[str, int]:
    """Cuenta en cuántos resultados posibles se puntúa en cada categoría.

    El resultado se memoriza porque recorrer los 7776 casos es la parte cara del
    cálculo y no depende de la categoría consultada.
    """
    conteo = dict.fromkeys(CATEGORIAS, 0)
    for resultado in product(range(1, caras + 1), repeat=n_dados):
        for categoria in CATEGORIAS:
            if puntuar(categoria, resultado) > 0:
                conteo[categoria] += 1
    return MappingProxyType(conteo)


def tabla_probabilidades(caras: int = CARAS, n_dados: int = N_DADOS) -> dict[str, float]:
    """Probabilidad exacta de puntuar en cada categoría con un lanzamiento."""
    conteo = _conteo_por_categoria(caras, n_dados)
    total = caras**n_dados
    return {categoria: conteo[categoria] / total for categoria in CATEGORIAS}


def probabilidad_categoria_un_lanzamiento(
    categoria: str,
    caras: int = CARAS,
    n_dados: int = N_DADOS,
) -> float:
    """Probabilidad exacta de puntuar en una categoría con un lanzamiento.

    Raises:
        ValueError: si la categoría no existe.
    """
    if categoria not in CATEGORIAS:
        raise ValueError(f"Categoria desconocida: {categoria!r}")
    return _conteo_por_categoria(caras, n_dados)[categoria] / caras**n_dados


def probabilidad_cinco_iguales(caras: int = CARAS, n_dados: int = N_DADOS) -> float:
    """Probabilidad de que todos los dados salgan iguales en un lanzamiento.

    Son `caras` casos favorables de `caras ** n_dados` posibles.
    """
    return caras / caras**n_dados


def probabilidad_full_estricto(caras: int = CARAS) -> float:
    """Probabilidad exacta de un full 3+2 en un lanzamiento.

    Se elige la cara del trío (6 opciones), la de la pareja (5 opciones) y las
    posiciones de los tres dados iguales (C(5,3) = 10), sobre 6^5 resultados.
    """
    return caras * (caras - 1) * comb(5, 3) / caras**N_DADOS


def distribucion_suma(n_dados: int = N_DADOS, caras: int = CARAS) -> dict[int, float]:
    """Distribución exacta de la suma de los dados, por convolución."""
    distribucion: dict[int, float] = {0: 1.0}
    for _ in range(n_dados):
        siguiente: dict[int, float] = {}
        for suma, probabilidad in distribucion.items():
            for cara in range(1, caras + 1):
                siguiente[suma + cara] = siguiente.get(suma + cara, 0.0) + probabilidad / caras
        distribucion = siguiente
    return dict(sorted(distribucion.items()))
