"""Políticas de retención de dados.

Decidir qué dados se conservan es un problema distinto de decidir en qué
categoría se anota el turno. Se separan a propósito: una estrategia compone una
política de retención, de modo que se pueden comparar políticas sin duplicar
código ni reescribir las estrategias.
"""

from __future__ import annotations

from typing import Protocol, Sequence

from .puntuacion import (
    CARA_OBJETIVO,
    CHANCE,
    ESCALERA_CORTA,
    ESCALERA_LARGA,
    FULL,
    POKER,
    TRIO,
    YAHTZEE,
)

# En la categoría chance conviene volver a lanzar los dados bajos.
UMBRAL_CHANCE = 4


class PoliticaRetencion(Protocol):
    """Contrato de una política de retención."""

    def dados_a_conservar(self, categoria: str, valores: Sequence[int]) -> tuple[int, ...]:
        """Devuelve los valores que se mantienen antes del siguiente lanzamiento."""
        ...


class RetencionNula:
    """No conserva nada: vuelve a lanzar los cinco dados."""

    def dados_a_conservar(self, categoria: str, valores: Sequence[int]) -> tuple[int, ...]:
        return ()


class RetencionPorObjetivo:
    """Conserva los dados que aportan a la categoría que se está persiguiendo."""

    def dados_a_conservar(self, categoria: str, valores: Sequence[int]) -> tuple[int, ...]:
        if categoria in CARA_OBJETIVO:
            cara = CARA_OBJETIVO[categoria]
            return tuple(valor for valor in valores if valor == cara)

        if categoria in (TRIO, POKER, YAHTZEE):
            return _dados_de_la_cara_mas_repetida(valores)

        if categoria == FULL:
            return _retencion_full(valores)

        if categoria in (ESCALERA_CORTA, ESCALERA_LARGA):
            return _racha_mas_larga(valores)

        if categoria == CHANCE:
            return tuple(valor for valor in valores if valor >= UMBRAL_CHANCE)

        return ()


def _grupos_ordenados(valores: Sequence[int]) -> list[tuple[int, int]]:
    """Pares (cara, veces) ordenados de más a menos repetidos y de mayor a menor cara."""
    conteos = {cara: valores.count(cara) for cara in set(valores)}
    return sorted(conteos.items(), key=lambda par: (-par[1], -par[0]))


def _dados_de_la_cara_mas_repetida(valores: Sequence[int]) -> tuple[int, ...]:
    cara, _ = _grupos_ordenados(valores)[0]
    return tuple(valor for valor in valores if valor == cara)


def _retencion_full(valores: Sequence[int]) -> tuple[int, ...]:
    """Conserva el grupo mayor y, si tiene al menos dos dados, el segundo grupo."""
    grupos = _grupos_ordenados(valores)
    conservar = [valor for valor in valores if valor == grupos[0][0]]
    for cara, veces in grupos[1:]:
        if veces >= 2:
            conservar += [valor for valor in valores if valor == cara]
            break
    return tuple(conservar)


def _racha_mas_larga(valores: Sequence[int]) -> tuple[int, ...]:
    """Secuencia de valores consecutivos más larga que contiene la tirada."""
    mejor: tuple[int, ...] = ()
    actual: tuple[int, ...] = ()
    for valor in sorted(set(valores)):
        actual = actual + (valor,) if actual and valor == actual[-1] + 1 else (valor,)
        if len(actual) > len(mejor):
            mejor = actual
    return mejor
