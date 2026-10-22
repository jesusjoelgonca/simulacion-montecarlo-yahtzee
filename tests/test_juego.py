"""Pruebas del motor, del marco Montecarlo y de las probabilidades exactas."""

from __future__ import annotations

import unittest

import numpy as np

from yahtzee.estrategia import EstrategiaCodiciosa
from yahtzee.juego import jugar_partida, jugar_turno
from yahtzee.montecarlo import (
    curva_convergencia,
    frecuencia_cinco_iguales,
    simular,
    simular_enfrentamiento,
    tabla_convergencia,
)
from yahtzee.probabilidades import (
    probabilidad_categoria_un_lanzamiento,
    probabilidad_cinco_iguales,
    probabilidad_full_estricto,
    tabla_probabilidades,
)
from yahtzee.puntuacion import CATEGORIAS, YAHTZEE
from yahtzee.tarjeta import Tarjeta


class TestJuego(unittest.TestCase):
    def test_un_turno_ocupa_una_casilla(self):
        tarjeta = Tarjeta()
        rng = np.random.default_rng(1)
        jugar_turno(tarjeta, EstrategiaCodiciosa(), rng)
        self.assertEqual(len(tarjeta.disponibles()), len(CATEGORIAS) - 1)

    def test_un_turno_no_supera_tres_lanzamientos(self):
        rng = np.random.default_rng(2)
        turno = jugar_turno(Tarjeta(), EstrategiaCodiciosa(), rng)
        self.assertLessEqual(len(turno.lanzamientos), 3)
        self.assertGreaterEqual(len(turno.lanzamientos), 1)

    def test_la_partida_completa_las_trece_casillas(self):
        rng = np.random.default_rng(3)
        partida = jugar_partida([EstrategiaCodiciosa(), EstrategiaCodiciosa()], rng)
        for tarjeta in partida.tarjetas:
            self.assertTrue(tarjeta.completa())

    def test_la_misma_semilla_reproduce_la_partida(self):
        def jugar(semilla):
            rng = np.random.default_rng(semilla)
            return jugar_partida([EstrategiaCodiciosa(), EstrategiaCodiciosa()], rng).puntajes

        self.assertEqual(jugar(42), jugar(42))
        self.assertNotEqual(jugar(42), jugar(43))

    def test_rechaza_numero_de_estrategias_incorrecto(self):
        with self.assertRaises(ValueError):
            jugar_partida([EstrategiaCodiciosa()], np.random.default_rng(1))


class TestMontecarlo(unittest.TestCase):
    def test_la_media_cae_dentro_del_intervalo(self):
        resultado = simular(200, "codiciosa", semilla=7)
        bajo, alto = resultado.intervalo_confianza
        self.assertLessEqual(bajo, resultado.media)
        self.assertGreaterEqual(alto, resultado.media)

    def test_el_error_estandar_decrece_con_n(self):
        resultado = simular(2_000, "codiciosa", semilla=7)
        filas = tabla_convergencia(resultado.puntajes, hitos=(100, 1_000))
        self.assertLess(filas[1]["error_estandar"], filas[0]["error_estandar"])

    def test_la_curva_convergencia_termina_en_la_media(self):
        resultado = simular(500, "codiciosa", semilla=7)
        curva = curva_convergencia(resultado.puntajes)
        self.assertAlmostEqual(curva[-1], resultado.media, places=6)

    def test_la_media_es_estable_entre_semillas(self):
        medias = [simular(1_000, "codiciosa", semilla=semilla).media for semilla in (1, 2, 3)]
        self.assertLess(max(medias) - min(medias), 10)

    def test_el_enfrentamiento_reporta_proporciones_validas(self):
        resultado = simular_enfrentamiento(300, "bono", "aleatoria", semilla=11)
        total = resultado.victorias_a + resultado.victorias_b + resultado.empates
        self.assertAlmostEqual(total, 1.0, places=6)
        self.assertGreater(resultado.victorias_a, resultado.victorias_b)

    def test_rechaza_numero_de_partidas_invalido(self):
        with self.assertRaises(ValueError):
            simular(0, "codiciosa")


class TestProbabilidades(unittest.TestCase):
    def test_la_tabla_cubre_todas_las_categorias(self):
        self.assertEqual(set(tabla_probabilidades()), set(CATEGORIAS))

    def test_cinco_iguales_coincide_con_la_formula(self):
        self.assertAlmostEqual(probabilidad_cinco_iguales(), 6 / 6**5)
        self.assertAlmostEqual(probabilidad_cinco_iguales(), 1 / 1296)

    def test_probabilidades_entre_cero_y_uno(self):
        for probabilidad in tabla_probabilidades().values():
            self.assertGreaterEqual(probabilidad, 0.0)
            self.assertLessEqual(probabilidad, 1.0)

    def test_chance_siempre_puntua(self):
        self.assertAlmostEqual(tabla_probabilidades()["Chance"], 1.0)

    def test_yahtzee_coincide_con_cinco_iguales(self):
        self.assertAlmostEqual(
            probabilidad_categoria_un_lanzamiento(YAHTZEE),
            probabilidad_cinco_iguales(),
        )

    def test_full_estricto_coincide_con_la_enumeracion(self):
        self.assertAlmostEqual(
            probabilidad_full_estricto(),
            probabilidad_categoria_un_lanzamiento("Full"),
        )

    def test_frecuencia_simulada_se_acerca_a_la_teoria(self):
        teorica = probabilidad_cinco_iguales()
        observada = frecuencia_cinco_iguales(200_000, semilla=5)["frecuencia"]
        self.assertLess(abs(observada - teorica), 5 * (teorica * (1 - teorica) / 200_000) ** 0.5)


if __name__ == "__main__":
    unittest.main()
