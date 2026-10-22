"""Genera las figuras del informe a partir de los CSV de `resultados/`.

Separado de `experimentos.py` a propósito: cambiar la presentación no debe
obligar a repetir ocho minutos de simulación.

Uso:
    python scripts/figuras.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
RESULTADOS = RAIZ / "resultados"
FIGURAS = RESULTADOS / "figuras"

# Paleta en grises: las figuras se leen igual en pantalla y en impresión.
TINTA = "#1f2933"
GRIS = "#8b98a5"
GRIS_CLARO = "#d5dbe1"
FONDO_BANDA = "#eef1f4"

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 9,
        "axes.edgecolor": GRIS,
        "axes.labelcolor": TINTA,
        "axes.titlesize": 10,
        "xtick.color": TINTA,
        "ytick.color": TINTA,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 200,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
    }
)

ANCHO = 6.3


def _leer(nombre: str) -> list[dict[str, str]]:
    with (RESULTADOS / nombre).open(encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def _columna(filas: list[dict[str, str]], campo: str) -> np.ndarray:
    return np.array([float(fila[campo]) for fila in filas])


def _puntajes() -> np.ndarray:
    with (RESULTADOS / "puntajes_bono.csv").open(encoding="utf-8") as archivo:
        return np.array([int(fila["puntaje"]) for fila in csv.DictReader(archivo)])


def _guardar(fig, nombre: str) -> None:
    FIGURAS.mkdir(parents=True, exist_ok=True)
    ruta = FIGURAS / nombre
    fig.savefig(ruta)
    plt.close(fig)
    print(f"  {ruta.name}")


def _estilo_ejes(eje, *, grilla: str = "y") -> None:
    eje.grid(axis=grilla, color=GRIS_CLARO, linewidth=0.6)
    eje.set_axisbelow(True)


def figura_convergencia() -> None:
    """Media acumulada del puntaje: la traza visual de la Ley de los Grandes Números."""
    filas = _leer("convergencia.csv")
    n = _columna(filas, "partidas")
    media = _columna(filas, "media_acumulada")
    inferior = _columna(filas, "banda_inferior")
    superior = _columna(filas, "banda_superior")
    final = media[-1]

    fig, eje = plt.subplots(figsize=(ANCHO, 3.4))
    eje.fill_between(n, inferior, superior, color=FONDO_BANDA, label="Banda de ± 2 errores estándar")
    eje.plot(n, media, color=TINTA, linewidth=1.2, label="Media acumulada")
    eje.axhline(final, color=GRIS, linewidth=1.0, linestyle=(0, (4, 3)), label=f"Media final = {final:.1f}")

    eje.set_xscale("log")
    eje.set_xlabel("Número de partidas simuladas (escala logarítmica)")
    eje.set_ylabel("Puntaje medio acumulado")
    eje.set_title("Convergencia de la media muestral con la estrategia de bono")
    eje.legend(frameon=False, loc="lower right", fontsize=8)
    _estilo_ejes(eje)
    _guardar(fig, "fig1_convergencia.png")


def figura_error_estandar() -> None:
    """Contrasta el error estándar empírico con la ley sigma/sqrt(n)."""
    puntajes = _puntajes()
    desviacion = puntajes.std(ddof=1)

    tamanos = np.unique(np.round(np.logspace(np.log10(100), np.log10(puntajes.size // 4), 14)).astype(int))
    empirico = []
    for tamano in tamanos:
        bloques = puntajes.size // tamano
        medias = puntajes[: bloques * tamano].reshape(bloques, tamano).mean(axis=1)
        empirico.append(medias.std(ddof=1))
    empirico = np.array(empirico)

    curva_n = np.logspace(np.log10(tamanos[0]), np.log10(tamanos[-1]), 200)

    fig, eje = plt.subplots(figsize=(ANCHO, 3.4))
    eje.plot(curva_n, desviacion / np.sqrt(curva_n), color=GRIS, linewidth=1.1,
             linestyle=(0, (4, 3)), label="Ley teórica σ/√n")
    eje.plot(tamanos, empirico, color=TINTA, linewidth=1.0, marker="o", markersize=4.5,
             label="Error estándar estimado por bloques")

    eje.set_xscale("log")
    eje.set_yscale("log")
    eje.set_xlabel("Tamaño de muestra n (escala logarítmica)")
    eje.set_ylabel("Error estándar de la media")
    eje.set_title("El error estándar cae a la mitad al cuadruplicar las iteraciones")
    eje.set_yticks([0.3, 0.4, 0.5, 0.7, 1, 1.5, 2, 3, 4])
    eje.set_yticklabels(["0.3", "0.4", "0.5", "0.7", "1", "1.5", "2", "3", "4"])
    eje.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    eje.legend(frameon=False, loc="lower left", fontsize=8)
    _estilo_ejes(eje, grilla="both")
    _guardar(fig, "fig2_error_estandar.png")


def figura_configuraciones() -> None:
    """Dos vistas: la escala completa y el detalle de las dos mejores configuraciones.

    En el panel izquierdo las barras parten de cero, que es lo correcto cuando la
    magnitud importa. En el derecho se comparan solo las dos mejores con un
    gráfico de puntos y eje recortado, donde el intervalo de confianza sí se
    distingue; recortar el eje de unas barras exageraría la diferencia.
    """
    filas = _leer("comparacion_configuraciones.csv")
    etiquetas = [f"{fila['estrategia']}\n{fila['retencion']}" for fila in filas]
    medias = _columna(filas, "media")
    inferior = _columna(filas, "ic95_inferior")
    superior = _columna(filas, "ic95_superior")

    fig, (izquierda, derecha) = plt.subplots(
        1, 2, figsize=(ANCHO, 3.6), gridspec_kw={"width_ratios": [2.1, 1]}
    )

    posiciones = np.arange(len(filas))
    izquierda.bar(posiciones, medias, color=GRIS_CLARO, edgecolor=TINTA, linewidth=0.8, width=0.62)
    for posicion, media in zip(posiciones, medias):
        izquierda.annotate(f"{media:.1f}", (posicion, media), textcoords="offset points",
                           xytext=(0, 5), ha="center", fontsize=7.5)
    izquierda.set_xticks(posiciones)
    izquierda.set_xticklabels(etiquetas, fontsize=7)
    izquierda.set_ylabel("Puntaje medio por partida")
    izquierda.set_ylim(0, medias.max() * 1.18)
    izquierda.set_title("Escala completa", fontsize=9)
    _estilo_ejes(izquierda)

    detalle = [i for i, fila in enumerate(filas) if fila["retencion"] == "por objetivo"]
    x_detalle = np.arange(len(detalle))
    for posicion, indice in enumerate(detalle):
        derecha.errorbar(
            posicion,
            medias[indice],
            yerr=[[medias[indice] - inferior[indice]], [superior[indice] - medias[indice]]],
            fmt="o",
            color=TINTA,
            markersize=7,
            capsize=6,
            linewidth=1.4,
        )
        derecha.annotate(f"{medias[indice]:.2f}", (posicion, medias[indice]),
                         textcoords="offset points", xytext=(9, 0), ha="left", va="center", fontsize=7.5)
    derecha.set_xticks(x_detalle)
    derecha.set_xticklabels([filas[i]["estrategia"] for i in detalle], fontsize=8)
    derecha.set_ylim(204.0, 209.0)
    derecha.set_title("Detalle de las dos mejores\n(IC 95 %)", fontsize=9)
    _estilo_ejes(derecha)

    fig.suptitle("Aporte de la estrategia y de la política de retención", fontsize=10, y=1.02)
    _guardar(fig, "fig3_configuraciones.png")


def figura_distribucion() -> None:
    """Distribución del puntaje final: asimétrica a la derecha, con dos modas."""
    puntajes = _puntajes()

    fig, eje = plt.subplots(figsize=(ANCHO, 3.2))
    eje.hist(puntajes, bins=45, color=GRIS_CLARO, edgecolor=TINTA, linewidth=0.5)
    eje.axvline(puntajes.mean(), color=TINTA, linewidth=1.2, label=f"Media = {puntajes.mean():.1f}")
    eje.axvline(np.median(puntajes), color=GRIS, linewidth=1.0, linestyle=(0, (4, 3)),
                label=f"Mediana = {np.median(puntajes):.0f}")

    eje.set_xlabel("Puntaje final de la partida")
    eje.set_ylabel("Número de partidas")
    eje.set_title(f"Distribución del puntaje con la estrategia de bono (n = {puntajes.size:,})")
    eje.legend(frameon=False, fontsize=8)
    _estilo_ejes(eje)
    _guardar(fig, "fig4_distribucion.png")


def figura_cinco_iguales() -> None:
    """El error absoluto de la frecuencia simulada tiende a cero al crecer n."""
    filas = _leer("contraste_cinco_iguales.csv")
    n = _columna(filas, "lanzamientos")
    error = _columna(filas, "error_absoluto")
    teorica = float(filas[0]["probabilidad_exacta"])

    fig, eje = plt.subplots(figsize=(ANCHO, 3.4))
    eje.plot(n, error, color=TINTA, linewidth=1.1, marker="o", markersize=4.5,
             label="Error absoluto observado")
    referencia = error[0] * np.sqrt(n[0]) / np.sqrt(n)
    eje.plot(n, referencia, color=GRIS, linewidth=1.0, linestyle=(0, (4, 3)),
             label="Referencia 1/√n")

    eje.set_xscale("log")
    eje.set_yscale("log")
    eje.set_xlabel("Número de lanzamientos simulados (escala logarítmica)")
    eje.set_ylabel("Error absoluto")
    eje.set_yticks([1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4])
    eje.set_yticklabels(["1e-5", "2e-5", "5e-5", "1e-4", "2e-4", "5e-4"])
    eje.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    eje.set_title(f"Contraste contra el valor exacto de cinco iguales (1/1296 = {teorica:.6f})")
    eje.legend(frameon=False, fontsize=8)
    _estilo_ejes(eje, grilla="both")
    _guardar(fig, "fig5_cinco_iguales.png")


def figura_probabilidades() -> None:
    """Probabilidad exacta de puntuar en cada categoría con un solo lanzamiento."""
    filas = _leer("probabilidades_exactas.csv")
    etiquetas = [fila["categoria"] for fila in filas]
    valores = _columna(filas, "probabilidad")

    fig, eje = plt.subplots(figsize=(ANCHO, 3.4))
    posiciones = np.arange(len(filas))
    eje.barh(posiciones, valores, color=GRIS_CLARO, edgecolor=TINTA, linewidth=0.7)
    eje.set_yticks(posiciones)
    eje.set_yticklabels(etiquetas, fontsize=8)
    eje.invert_yaxis()
    for posicion, valor in zip(posiciones, valores):
        eje.annotate(f"{valor:.4f}", (valor, posicion), textcoords="offset points",
                     xytext=(4, 0), va="center", fontsize=7)
    eje.set_xlabel("Probabilidad exacta en un lanzamiento")
    eje.set_xlim(0, 1.12)
    eje.set_title("Distribución de probabilidad por categoría (6⁵ = 7776 casos)")
    _estilo_ejes(eje, grilla="x")
    _guardar(fig, "fig6_probabilidades.png")


def main() -> int:
    print("Generando figuras")
    figura_convergencia()
    figura_error_estandar()
    figura_configuraciones()
    figura_distribucion()
    figura_cinco_iguales()
    figura_probabilidades()
    print(f"Listo: {FIGURAS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
