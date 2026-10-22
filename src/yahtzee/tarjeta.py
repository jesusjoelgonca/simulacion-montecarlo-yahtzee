"""Tarjeta de puntuación de un jugador.

Es la estructura de manejo de la información: trece casillas, cada una se usa
una sola vez, y el total incorpora el bono de la sección superior. Se usa un
diccionario indexado por nombre porque permite distinguir una casilla libre de
una casilla con cero puntos, algo que una lista de enteros no expresa.
"""

from __future__ import annotations

from .puntuacion import (
    BONO_SUPERIOR,
    CATEGORIAS,
    MAXIMO_POR_CATEGORIA_SUPERIOR,
    SUPERIOR,
    UMBRAL_BONO,
)


class Tarjeta:
    """Estado de las trece categorías de un jugador."""

    __slots__ = ("puntajes",)

    def __init__(self) -> None:
        # None = casilla libre; 0 = casilla usada que no sumó.
        self.puntajes: dict[str, int | None] = {categoria: None for categoria in CATEGORIAS}

    def disponibles(self) -> tuple[str, ...]:
        """Categorías libres, en el orden canónico del juego."""
        return tuple(categoria for categoria in CATEGORIAS if self.puntajes[categoria] is None)

    def registrar(self, categoria: str, valor: int) -> None:
        """Anota un puntaje en una casilla libre.

        Raises:
            ValueError: si la categoría no existe o ya fue usada.
        """
        if categoria not in self.puntajes:
            raise ValueError(f"Categoria desconocida: {categoria!r}")
        if self.puntajes[categoria] is not None:
            raise ValueError(f"La categoria {categoria!r} ya fue usada")
        self.puntajes[categoria] = int(valor)

    def total_superior(self) -> int:
        """Puntos acumulados en la sección superior."""
        return sum(self.puntajes[categoria] or 0 for categoria in SUPERIOR)

    def bono(self) -> int:
        """Bono de la sección superior, si se alcanzó el umbral."""
        return BONO_SUPERIOR if self.total_superior() >= UMBRAL_BONO else 0

    def falta_bono(self) -> bool:
        """Verdadero si el bono aún no se alcanzó pero sigue siendo alcanzable."""
        if self.total_superior() >= UMBRAL_BONO:
            return False
        libres = sum(1 for categoria in SUPERIOR if self.puntajes[categoria] is None)
        return self.total_superior() + libres * MAXIMO_POR_CATEGORIA_SUPERIOR >= UMBRAL_BONO

    def total(self) -> int:
        """Puntaje final de la partida."""
        return sum(valor or 0 for valor in self.puntajes.values()) + self.bono()

    def completa(self) -> bool:
        """Verdadero si las trece casillas están usadas."""
        return all(valor is not None for valor in self.puntajes.values())

    def copia(self) -> "Tarjeta":
        """Copia independiente, útil para explorar escenarios sin alterar el original."""
        clon = Tarjeta()
        clon.puntajes = dict(self.puntajes)
        return clon

    def __repr__(self) -> str:
        usadas = len(CATEGORIAS) - len(self.disponibles())
        return f"Tarjeta({usadas}/{len(CATEGORIAS)}, total={self.total()})"
