"""Ejecuta los experimentos Montecarlo y guarda los resultados en disco.

Solo calcula y escribe CSV/JSON. Las figuras se generan aparte, en
`scripts/figuras.py`, a partir de estos archivos: así se puede cambiar la
presentación sin repetir la simulación.

Uso:
    python scripts/experimentos.py --rapido      # ~1 minuto
    python scripts/experimentos.py               # configuración del informe
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from yahtzee import (  # noqa: E402  (la ruta se ajusta arriba)
    EstrategiaAleatoria,
    EstrategiaBono,
    EstrategiaCodiciosa,
    RetencionNula,
    RetencionPorObjetivo,
    banda_convergencia,
    curva_convergencia,
    probabilidad_cinco_iguales,
    simular,
    simular_con,
    tabla_convergencia,
    tabla_probabilidades,
)

SALIDA = RAIZ / "resultados"
SEMILLA = 2026


def _guardar_csv(ruta: Path, filas: list[dict[str, object]], campos: list[str]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def experimento_probabilidades(n_lanzamientos: int) -> dict[str, object]:
    """Contrasta la frecuencia simulada de cinco iguales con el valor exacto."""
    rng = np.random.default_rng(SEMILLA)
    teorica = probabilidad_cinco_iguales()
    hitos = [n for n in (100, 1_000, 10_000, 100_000, 1_000_000) if n <= n_lanzamientos]

    filas: list[dict[str, object]] = []
    aciertos = 0
    lanzados = 0
    for hito in hitos:
        while lanzados < hito:
            if len(set(int(v) for v in rng.integers(1, 7, size=5))) == 1:
                aciertos += 1
            lanzados += 1
        frecuencia = aciertos / lanzados
        filas.append(
            {
                "lanzamientos": lanzados,
                "aciertos": aciertos,
                "frecuencia_simulada": frecuencia,
                "probabilidad_exacta": teorica,
                "error_absoluto": abs(frecuencia - teorica),
                "error_relativo_pct": 100 * abs(frecuencia - teorica) / teorica,
            }
        )

    _guardar_csv(
        SALIDA / "contraste_cinco_iguales.csv",
        filas,
        ["lanzamientos", "aciertos", "frecuencia_simulada", "probabilidad_exacta", "error_absoluto", "error_relativo_pct"],
    )
    return {"filas": filas, "teorica": teorica}


def experimento_estrategias(n_partidas: int) -> dict[str, object]:
    """Diseño factorial 2x2: estrategia x política de retención, más la base aleatoria.

    Mantener fija la política de retención mientras cambia la estrategia (y al
    revés) permite atribuir la diferencia a un solo factor.
    """
    configuraciones = [
        ("aleatoria", "sin retencion", lambda rng: EstrategiaAleatoria(rng)),
        ("codiciosa", "sin retencion", lambda rng: EstrategiaCodiciosa(retencion=RetencionNula())),
        ("codiciosa", "por objetivo", lambda rng: EstrategiaCodiciosa(retencion=RetencionPorObjetivo())),
        ("bono", "sin retencion", lambda rng: EstrategiaBono(retencion=RetencionNula())),
        ("bono", "por objetivo", lambda rng: EstrategiaBono(retencion=RetencionPorObjetivo())),
    ]

    filas: list[dict[str, object]] = []
    for estrategia, retencion, fabrica in configuraciones:
        rng = np.random.default_rng(SEMILLA)
        resultado = simular_con(fabrica(rng), n_partidas, semilla=SEMILLA)
        bajo, alto = resultado.intervalo_confianza
        filas.append(
            {
                "estrategia": estrategia,
                "retencion": retencion,
                "partidas": resultado.n_partidas,
                "media": resultado.media,
                "desviacion": resultado.desviacion,
                "error_estandar": resultado.error_estandar,
                "ic95_inferior": bajo,
                "ic95_superior": alto,
                "minimo": resultado.minimo,
                "maximo": resultado.maximo,
                "p50": resultado.percentil(50),
            }
        )
        print(f"  {estrategia:<10} {retencion:<14} media={resultado.media:7.2f}  EE={resultado.error_estandar:.3f}")

    _guardar_csv(
        SALIDA / "comparacion_configuraciones.csv",
        filas,
        ["estrategia", "retencion", "partidas", "media", "desviacion", "error_estandar",
         "ic95_inferior", "ic95_superior", "minimo", "maximo", "p50"],
    )
    return {"filas": filas}


def experimento_convergencia(n_partidas: int) -> dict[str, object]:
    """Simulación larga con la mejor configuración, para la Ley de los Grandes Números."""
    resultado = simular(n_partidas, "bono", semilla=SEMILLA)

    curva = curva_convergencia(resultado.puntajes)
    inferior, superior = banda_convergencia(resultado.puntajes)

    # Se guarda una traza reducida para que la figura sea ligera y legible.
    indices = np.unique(np.round(np.logspace(0, np.log10(n_partidas), 600)).astype(int)) - 1
    indices = indices[(indices >= 0) & (indices < n_partidas)]
    _guardar_csv(
        SALIDA / "convergencia.csv",
        [
            {
                "partidas": int(i + 1),
                "media_acumulada": float(curva[i]),
                "banda_inferior": float(inferior[i]),
                "banda_superior": float(superior[i]),
            }
            for i in indices
        ],
        ["partidas", "media_acumulada", "banda_inferior", "banda_superior"],
    )

    tabla = tabla_convergencia(resultado.puntajes)
    _guardar_csv(
        SALIDA / "tabla_convergencia.csv",
        tabla,
        ["iteraciones", "media", "desviacion", "error_estandar", "error_relativo_pct"],
    )

    with (SALIDA / "puntajes_bono.csv").open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["partida", "puntaje"])
        escritor.writerows(enumerate(resultado.puntajes.tolist(), start=1))

    print(f"  convergencia: {resultado.resumen()}")
    return {
        "resumen": resultado.resumen(),
        "media": resultado.media,
        "desviacion": resultado.desviacion,
        "error_estandar": resultado.error_estandar,
        "ic95": resultado.intervalo_confianza,
        "tabla": tabla,
        "n": n_partidas,
    }


def main() -> int:
    analizador = argparse.ArgumentParser(description="Experimentos Montecarlo del Yahtzee")
    analizador.add_argument("--rapido", action="store_true", help="muestra reducida, para probar")
    args = analizador.parse_args()

    n_estrategias = 3_000 if args.rapido else 10_000
    n_convergencia = 10_000 if args.rapido else 50_000
    n_lanzamientos = 100_000 if args.rapido else 1_000_000

    SALIDA.mkdir(parents=True, exist_ok=True)
    inicio = time.perf_counter()
    resumen: dict[str, object] = {"semilla": SEMILLA}

    print("[1/4] Tabla exacta de probabilidades")
    tabla = tabla_probabilidades()
    _guardar_csv(
        SALIDA / "probabilidades_exactas.csv",
        [{"categoria": c, "probabilidad": p} for c, p in tabla.items()],
        ["categoria", "probabilidad"],
    )
    resumen["probabilidades_exactas"] = tabla

    print(f"[2/4] Contraste de la Ley de los Grandes Números ({n_lanzamientos:,} lanzamientos)")
    resumen["contraste"] = experimento_probabilidades(n_lanzamientos)

    print(f"[3/4] Comparación de configuraciones ({n_estrategias:,} partidas cada una)")
    resumen["configuraciones"] = experimento_estrategias(n_estrategias)

    print(f"[4/4] Convergencia ({n_convergencia:,} partidas)")
    resumen["convergencia"] = experimento_convergencia(n_convergencia)

    resumen["duracion_s"] = round(time.perf_counter() - inicio, 1)
    with (SALIDA / "resumen.json").open("w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, ensure_ascii=False, indent=2)

    print(f"\nResultados en {SALIDA} ({resumen['duracion_s']} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
