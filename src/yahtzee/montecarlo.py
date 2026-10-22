"""Marco de simulación Montecarlo.

El método repite el experimento aleatorio muchas veces y estudia la distribución
de los resultados. Aquí el experimento es una partida completa de Yahtzee entre
dos jugadores y la variable de interés es el puntaje final.

La Ley de los Grandes Números garantiza que la media muestral converge al valor
esperado al crecer el número de repeticiones, y el error estándar de la media
decrece como sigma/sqrt(n): cuadruplicar las iteraciones reduce a la mitad la
incertidumbre del estimador.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .dados import N_DADOS, lanzar
from .estrategia import NOMBRES_ESTRATEGIAS, Estrategia, por_nombre
from .juego import jugar_partida
from .puntuacion import es_cinco_iguales

NIVEL_CONFIANZA = 1.96  # aproximación normal para el 95 %
HITOS_POR_DEFECTO: tuple[int, ...] = (100, 1_000, 10_000, 100_000, 1_000_000)


@dataclass(frozen=True, slots=True)
class ResultadoMontecarlo:
    """Distribución de puntajes obtenida para una estrategia."""

    estrategia: str
    puntajes: np.ndarray

    @property
    def n_partidas(self) -> int:
        return int(self.puntajes.size)

    @property
    def media(self) -> float:
        return float(self.puntajes.mean())

    @property
    def desviacion(self) -> float:
        return float(self.puntajes.std(ddof=1))

    @property
    def error_estandar(self) -> float:
        """Error estándar de la media: sigma / sqrt(n)."""
        return self.desviacion / np.sqrt(self.n_partidas)

    @property
    def intervalo_confianza(self) -> tuple[float, float]:
        """Intervalo del 95 % para la media."""
        margen = NIVEL_CONFIANZA * self.error_estandar
        return (self.media - margen, self.media + margen)

    @property
    def minimo(self) -> int:
        return int(self.puntajes.min())

    @property
    def maximo(self) -> int:
        return int(self.puntajes.max())

    def percentil(self, valor: float) -> float:
        return float(np.percentile(self.puntajes, valor))

    def resumen(self) -> str:
        bajo, alto = self.intervalo_confianza
        return (
            f"{self.estrategia}: n={self.n_partidas:,} | media={self.media:.2f} | "
            f"sd={self.desviacion:.2f} | EE={self.error_estandar:.3f} | "
            f"IC95 %=({bajo:.2f}, {alto:.2f}) | min={self.minimo} max={self.maximo}"
        )


@dataclass(frozen=True, slots=True)
class Enfrentamiento:
    """Comparación pareada de dos estrategias jugando la misma tanda."""

    a: ResultadoMontecarlo
    b: ResultadoMontecarlo
    diferencia_media: float
    error_diferencia: float
    victorias_a: float
    victorias_b: float
    empates: float

    @property
    def diferencia_significativa(self) -> bool:
        """Verdadero si la diferencia supera dos errores estándar."""
        return abs(self.diferencia_media) > 2 * self.error_diferencia

    def resumen(self) -> str:
        return (
            f"{self.a.estrategia} {self.a.media:.2f} vs {self.b.estrategia} {self.b.media:.2f} | "
            f"diferencia={self.diferencia_media:+.2f} +/- {2 * self.error_diferencia:.2f} | "
            f"victorias={self.victorias_a:.1%} / {self.victorias_b:.1%} | empates={self.empates:.1%}"
        )


def _jugar_lote(n_partidas: int, estrategias: list, rng: np.random.Generator) -> np.ndarray:
    """Juega `n_partidas` con las estrategias dadas y devuelve (partidas x jugadores)."""
    if n_partidas <= 0:
        raise ValueError("El numero de partidas debe ser positivo")

    puntajes = np.empty((n_partidas, len(estrategias)), dtype=np.int64)
    for indice in range(n_partidas):
        puntajes[indice] = jugar_partida(estrategias, rng).puntajes
    return puntajes


def _correr(n_partidas: int, nombres: tuple[str, ...], semilla: int | None) -> np.ndarray:
    """Juega `n_partidas` construyendo las estrategias a partir de sus nombres."""
    rng = np.random.default_rng(semilla)
    return _jugar_lote(n_partidas, [por_nombre(nombre, rng) for nombre in nombres], rng)


def simular_con(
    estrategia: Estrategia,
    n_partidas: int,
    *,
    semilla: int | None = None,
) -> ResultadoMontecarlo:
    """Simula con una instancia de estrategia ya construida.

    Permite inyectar políticas de retención distintas y comparar configuraciones
    manteniendo todo lo demás constante.
    """
    rng = np.random.default_rng(semilla)
    matriz = _jugar_lote(n_partidas, [estrategia, estrategia], rng)
    return ResultadoMontecarlo(estrategia=estrategia.nombre, puntajes=matriz[:, 0])


def simular(
    n_partidas: int,
    estrategia: str = "bono",
    *,
    semilla: int | None = None,
) -> ResultadoMontecarlo:
    """Simula `n_partidas` partidas con la misma estrategia en ambos jugadores.

    Así la muestra recoge la variabilidad propia del juego y no la diferencia
    entre políticas.
    """
    matriz = _correr(n_partidas, (estrategia, estrategia), semilla)
    return ResultadoMontecarlo(estrategia=estrategia, puntajes=matriz[:, 0])


def simular_estrategias(
    n_partidas: int,
    *,
    semilla: int | None = None,
    estrategias: tuple[str, ...] = NOMBRES_ESTRATEGIAS,
) -> dict[str, ResultadoMontecarlo]:
    """Simula cada estrategia por separado con la misma semilla."""
    return {nombre: simular(n_partidas, nombre, semilla=semilla) for nombre in estrategias}


def simular_enfrentamiento(
    n_partidas: int,
    estrategia_a: str = "bono",
    estrategia_b: str = "codiciosa",
    *,
    semilla: int | None = None,
) -> Enfrentamiento:
    """Enfrenta dos estrategias en las mismas partidas (comparación pareada)."""
    matriz = _correr(n_partidas, (estrategia_a, estrategia_b), semilla)
    puntajes_a, puntajes_b = matriz[:, 0], matriz[:, 1]
    diferencias = puntajes_a - puntajes_b

    return Enfrentamiento(
        a=ResultadoMontecarlo(estrategia_a, puntajes_a),
        b=ResultadoMontecarlo(estrategia_b, puntajes_b),
        diferencia_media=float(diferencias.mean()),
        error_diferencia=float(diferencias.std(ddof=1) / np.sqrt(n_partidas)),
        victorias_a=float((puntajes_a > puntajes_b).mean()),
        victorias_b=float((puntajes_b > puntajes_a).mean()),
        empates=float((puntajes_a == puntajes_b).mean()),
    )


def curva_convergencia(puntajes: np.ndarray) -> np.ndarray:
    """Media acumulada tras cada partida: la traza de la Ley de los Grandes Números."""
    return np.cumsum(puntajes) / np.arange(1, puntajes.size + 1)


def banda_convergencia(puntajes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Banda de más/menos dos errores estándar alrededor de la media acumulada."""
    acumulada = curva_convergencia(puntajes)
    n = np.arange(1, puntajes.size + 1)
    margen = 2 * puntajes.std(ddof=1) / np.sqrt(n)
    return acumulada - margen, acumulada + margen


def tabla_convergencia(
    puntajes: np.ndarray,
    hitos: tuple[int, ...] = HITOS_POR_DEFECTO,
) -> list[dict[str, float]]:
    """Media, desviación y error estándar para distintos tamaños de muestra.

    Muestra que el error estándar se reduce a la mitad cada vez que el número de
    iteraciones se multiplica por cuatro.
    """
    filas: list[dict[str, float]] = []
    for hito in hitos:
        if hito > puntajes.size:
            continue
        muestra = puntajes[:hito]
        desviacion = float(muestra.std(ddof=1))
        error = desviacion / np.sqrt(hito)
        media = float(muestra.mean())
        filas.append(
            {
                "iteraciones": hito,
                "media": media,
                "desviacion": desviacion,
                "error_estandar": error,
                "error_relativo_pct": 100 * error / media,
            }
        )
    return filas


def frecuencia_cinco_iguales(
    n_lanzamientos: int,
    *,
    semilla: int | None = None,
) -> dict[str, float]:
    """Estima por Montecarlo la probabilidad de cinco iguales en un lanzamiento.

    El contraste más limpio contra la teoría: el valor exacto es 6/6^5 = 1/1296.
    """
    rng = np.random.default_rng(semilla)
    aciertos = sum(1 for _ in range(n_lanzamientos) if es_cinco_iguales(lanzar(N_DADOS, rng=rng)))
    return {
        "lanzamientos": float(n_lanzamientos),
        "aciertos": float(aciertos),
        "frecuencia": aciertos / n_lanzamientos,
    }
