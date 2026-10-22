"""Motor del juego para dos jugadores.

Cada turno admite hasta tres lanzamientos de cinco dados. Entre lanzamiento y
lanzamiento el jugador conserva los dados que quiera y vuelve a lanzar el resto.
Al cerrar el turno anota el resultado en una casilla libre. La partida dura
trece turnos por jugador, uno por categoría.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from .dados import N_DADOS, lanzar
from .estrategia import Estrategia
from .puntuacion import CATEGORIAS, puntuar
from .tarjeta import Tarjeta

LANZAMIENTOS_POR_TURNO = 3
JUGADORES = 2


@dataclass(slots=True)
class Turno:
    """Detalle de un turno, para la demostración y la depuración."""

    jugador: int
    categoria: str
    puntaje: int
    lanzamientos: list[tuple[int, ...]] = field(default_factory=list)


@dataclass(slots=True)
class ResultadoPartida:
    """Puntajes finales de una partida."""

    puntajes: tuple[int, int]
    tarjetas: tuple[Tarjeta, Tarjeta]

    @property
    def ganador(self) -> int | None:
        """Índice del ganador, o None si hay empate."""
        if self.puntajes[0] == self.puntajes[1]:
            return None
        return 0 if self.puntajes[0] > self.puntajes[1] else 1


def jugar_turno(
    tarjeta: Tarjeta,
    estrategia: Estrategia,
    rng: np.random.Generator,
    jugador: int = 0,
) -> Turno:
    """Juega un turno completo y lo anota en la tarjeta."""
    valores = list(lanzar(N_DADOS, rng=rng))
    lanzamientos: list[tuple[int, ...]] = [tuple(valores)]

    for _ in range(LANZAMIENTOS_POR_TURNO - 1):
        categoria = estrategia.elegir(tarjeta, valores)
        conservar = list(estrategia.retener(categoria, valores))[:N_DADOS]
        if len(conservar) == N_DADOS:
            break  # No hay nada que relanzar: la tirada queda como está.
        valores = conservar + list(lanzar(N_DADOS - len(conservar), rng=rng))
        lanzamientos.append(tuple(valores))

    categoria = estrategia.elegir(tarjeta, valores)
    puntaje = puntuar(categoria, valores)
    tarjeta.registrar(categoria, puntaje)
    return Turno(jugador=jugador, categoria=categoria, puntaje=puntaje, lanzamientos=lanzamientos)


def jugar_partida(
    estrategias: Sequence[Estrategia],
    rng: np.random.Generator,
    registro: list[Turno] | None = None,
) -> ResultadoPartida:
    """Juega una partida completa de dos jugadores.

    Args:
        estrategias: una estrategia por jugador.
        rng: generador compartido de dados y decisiones.
        registro: si se pasa una lista, se le añaden los turnos jugados.

    Raises:
        ValueError: si no se pasan exactamente dos estrategias.
    """
    if len(estrategias) != JUGADORES:
        raise ValueError(f"Se requieren {JUGADORES} estrategias, se recibieron {len(estrategias)}")

    tarjetas = (Tarjeta(), Tarjeta())

    for _ in range(len(CATEGORIAS)):
        for indice, estrategia in enumerate(estrategias):
            turno = jugar_turno(tarjetas[indice], estrategia, rng, jugador=indice)
            if registro is not None:
                registro.append(turno)

    return ResultadoPartida(
        puntajes=(tarjetas[0].total(), tarjetas[1].total()),
        tarjetas=tarjetas,
    )
