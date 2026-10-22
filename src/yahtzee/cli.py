"""Interfaz de línea de comandos.

Solo interpreta argumentos, llama a la API del paquete y formatea la salida. La
lógica del juego y de la simulación vive en los módulos, no aquí.

Ejemplos:
    python -m yahtzee simular --partidas 100000 --semilla 2026
    python -m yahtzee comparar --partidas 20000
    python -m yahtzee demo --semilla 7
    python -m yahtzee probabilidades
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

from . import __version__
from .estrategia import NOMBRES_ESTRATEGIAS, por_nombre
from .juego import jugar_partida
from .montecarlo import simular, simular_enfrentamiento, simular_estrategias
from .probabilidades import tabla_probabilidades
from .puntuacion import BONO_SUPERIOR, UMBRAL_BONO


def _cmd_simular(args: argparse.Namespace) -> int:
    resultado = simular(args.partidas, args.estrategia, semilla=args.semilla)
    print(resultado.resumen())
    print(f"  percentiles: p5={resultado.percentil(5):.0f}  p50={resultado.percentil(50):.0f}  p95={resultado.percentil(95):.0f}")

    if args.csv:
        destino = Path(args.csv)
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["partida", "puntaje"])
            escritor.writerows(enumerate(resultado.puntajes.tolist(), start=1))
        print(f"  puntajes escritos en {destino}")
    return 0


def _cmd_comparar(args: argparse.Namespace) -> int:
    resultados = simular_estrategias(args.partidas, semilla=args.semilla)
    print(f"Comparación con {args.partidas:,} partidas por estrategia\n")
    print(f"{'estrategia':<12}{'media':>9}{'sd':>9}{'EE':>9}{'IC95 %':>22}")
    for resultado in resultados.values():
        bajo, alto = resultado.intervalo_confianza
        print(
            f"{resultado.estrategia:<12}{resultado.media:>9.2f}{resultado.desviacion:>9.2f}"
            f"{resultado.error_estandar:>9.3f}   ({bajo:>7.2f}, {alto:>7.2f})"
        )

    print()
    enfrentamiento = simular_enfrentamiento(
        args.partidas, "bono", "codiciosa", semilla=args.semilla
    )
    print("Enfrentamiento pareado")
    print(f"  {enfrentamiento.resumen()}")
    print(f"  diferencia significativa: {'sí' if enfrentamiento.diferencia_significativa else 'no'}")
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    rng = np.random.default_rng(args.semilla)
    estrategias = [por_nombre(args.estrategia, rng), por_nombre("aleatoria", rng)]
    registro: list = []
    partida = jugar_partida(estrategias, rng, registro=registro)

    print(f"Demostración: jugador 1 = {args.estrategia}, jugador 2 = aleatoria\n")
    for turno in registro[:6]:
        lanzamientos = " -> ".join("".join(str(cara) for cara in tirada) for tirada in turno.lanzamientos)
        print(f"  J{turno.jugador + 1} {turno.categoria:<16} {turno.puntaje:>3} pts   [{lanzamientos}]")

    print()
    for indice, tarjeta in enumerate(partida.tarjetas):
        print(f"  J{indice + 1}: total {tarjeta.total():>3} | superior {tarjeta.total_superior():>2} | bono {tarjeta.bono():>2}")
    ganador = partida.ganador
    print(f"  Resultado: {'empate' if ganador is None else f'gana el jugador {ganador + 1}'}")
    return 0


def _cmd_probabilidades(args: argparse.Namespace) -> int:
    print("Probabilidad exacta de puntuar con un solo lanzamiento de cinco dados\n")
    tabla = tabla_probabilidades()
    for categoria, probabilidad in tabla.items():
        print(f"  {categoria:<16}{probabilidad:>10.6f}   {probabilidad:>8.4%}")
    print(f"\n  Bono superior: {BONO_SUPERIOR} puntos con {UMBRAL_BONO} o más en la sección superior")
    return 0


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yahtzee",
        description="Simulación Montecarlo del juego de Yahtzee para dos jugadores",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    simular_parser = subparsers.add_parser("simular", help="simula N partidas con una estrategia")
    simular_parser.add_argument("--partidas", type=int, default=10_000)
    simular_parser.add_argument("--estrategia", choices=NOMBRES_ESTRATEGIAS, default="bono")
    simular_parser.add_argument("--semilla", type=int, default=None)
    simular_parser.add_argument("--csv", type=str, default=None, help="ruta del CSV de salida")
    simular_parser.set_defaults(func=_cmd_simular)

    comparar_parser = subparsers.add_parser("comparar", help="compara las tres estrategias")
    comparar_parser.add_argument("--partidas", type=int, default=10_000)
    comparar_parser.add_argument("--semilla", type=int, default=None)
    comparar_parser.set_defaults(func=_cmd_comparar)

    demo_parser = subparsers.add_parser("demo", help="muestra una partida turno a turno")
    demo_parser.add_argument("--estrategia", choices=NOMBRES_ESTRATEGIAS, default="bono")
    demo_parser.add_argument("--semilla", type=int, default=7)
    demo_parser.set_defaults(func=_cmd_demo)

    probabilidades_parser = subparsers.add_parser("probabilidades", help="tabla exacta de probabilidades")
    probabilidades_parser.set_defaults(func=_cmd_probabilidades)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
