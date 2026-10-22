"""Generación de tiradas.

La distribución del problema es uniforme discreta: cada dado de seis caras tiene
probabilidad 1/6 de mostrar cualquier cara y los cinco dados son independientes.
El generador de NumPy reproduce esa distribución.
"""

from __future__ import annotations

import numpy as np

CARAS = 6
N_DADOS = 5


def lanzar(
    cantidad: int = N_DADOS,
    caras: int = CARAS,
    rng: np.random.Generator | None = None,
) -> tuple[int, ...]:
    """Lanza `cantidad` dados y devuelve los valores en el orden en que salieron.

    Args:
        cantidad: número de dados a lanzar.
        caras: número de caras de cada dado.
        rng: generador de NumPy. Si es None se crea uno nuevo sin semilla.
    """
    if cantidad <= 0:
        raise ValueError("La cantidad de dados debe ser positiva")
    if caras <= 1:
        raise ValueError("Un dado necesita al menos dos caras")

    generador = rng if rng is not None else np.random.default_rng()
    # tolist() evita recorrer el arreglo con un generador: es la ruta caliente
    # de la simulacion, se llama decenas de veces por partida.
    return tuple(generador.integers(1, caras + 1, size=cantidad).tolist())
