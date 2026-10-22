"""Version base del juego de Yahtzee (fase USA).

Este archivo reproduce la guia minima de partida que se toma como punto de
referencia: un solo jugador, cinco dados, tres lanzamientos por turno y
unicamente dos formas de puntuar (suma total y "yahtzee"). No conserva dados
entre lanzamientos y no lleva una tarjeta con las trece categorias.

Se conserva sin cambios para poder comparar, en el documento tecnico, que se
modifico y por que. La version ampliada vive en el paquete `yahtzee`.

Ejecucion:
    python src/v0_base/yahtzee_base.py --turnos 13 --semilla 7
"""

from __future__ import annotations

import argparse
import random


def lanzar_dados(cantidad: int = 5, caras: int = 6, azar: random.Random | None = None) -> list[int]:
    """Lanza `cantidad` dados de `caras` caras y devuelve la lista de valores."""
    generador = azar or random.Random()
    return [generador.randint(1, caras) for _ in range(cantidad)]


def puntuar_suma(dados: list[int]) -> int:
    """Categoria unica de la version base: la suma de los cinco dados."""
    return sum(dados)


def es_yahtzee(dados: list[int]) -> bool:
    """Verdadero si los cinco dados muestran la misma cara."""
    return len(set(dados)) == 1


def jugar_turno(azar: random.Random) -> int:
    """Juega un turno de tres lanzamientos sin conservar dados.

    La version base vuelve a lanzar los cinco dados en cada oportunidad y se
    queda con el ultimo resultado. Es deliberadamente simple: no hay decision
    que tomar, de modo que el turno no depende de ninguna estrategia.
    """
    dados: list[int] = []
    for _ in range(3):
        dados = lanzar_dados(azar=azar)
    return puntuar_suma(dados)


def jugar_partida(turnos: int, azar: random.Random) -> int:
    """Juega `turnos` turnos y devuelve el puntaje acumulado."""
    total = 0
    for _ in range(turnos):
        total += jugar_turno(azar)
    return total


def main() -> int:
    analizador = argparse.ArgumentParser(description="Yahtzee, version base (fase USA)")
    analizador.add_argument("--turnos", type=int, default=13, help="turnos por partida")
    analizador.add_argument("--partidas", type=int, default=1, help="partidas a simular")
    analizador.add_argument("--semilla", type=int, default=None, help="semilla del generador")
    args = analizador.parse_args()

    azar = random.Random(args.semilla)
    puntajes = [jugar_partida(args.turnos, azar) for _ in range(args.partidas)]

    if args.partidas == 1:
        print(f"Puntaje de la partida: {puntajes[0]}")
    else:
        media = sum(puntajes) / len(puntajes)
        print(f"Partidas: {args.partidas}")
        print(f"Media: {media:.2f}")
        print(f"Minimo: {min(puntajes)}  Maximo: {max(puntajes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
