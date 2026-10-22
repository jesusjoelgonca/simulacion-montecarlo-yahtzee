"""Pruebas de las políticas de retención y de las estrategias."""

from __future__ import annotations

import unittest

import numpy as np

from yahtzee.estrategia import (
    EstrategiaAleatoria,
    EstrategiaBono,
    EstrategiaCodiciosa,
    por_nombre,
)
from yahtzee.puntuacion import SEISES, TRIO, YAHTZEE
from yahtzee.retencion import RetencionNula, RetencionPorObjetivo
from yahtzee.tarjeta import Tarjeta


class TestRetencion(unittest.TestCase):
    def setUp(self):
        self.politica = RetencionPorObjetivo()

    def test_retencion_nula_no_conserva_nada(self):
        self.assertEqual(RetencionNula().dados_a_conservar(SEISES, (6, 6, 1, 2, 3)), ())

    def test_superior_conserva_solo_su_cara(self):
        self.assertEqual(self.politica.dados_a_conservar(SEISES, (6, 6, 1, 2, 3)), (6, 6))

    def test_trio_conserva_la_cara_mas_repetida(self):
        self.assertEqual(self.politica.dados_a_conservar(TRIO, (2, 2, 2, 5, 6)), (2, 2, 2))

    def test_yahtzee_conserva_la_mayoria(self):
        self.assertEqual(self.politica.dados_a_conservar(YAHTZEE, (4, 4, 4, 1, 2)), (4, 4, 4))

    def test_escalera_conserva_la_racha_mas_larga(self):
        self.assertEqual(self.politica.dados_a_conservar("Escalera corta", (1, 2, 3, 5, 5)), (1, 2, 3))

    def test_full_conserva_dos_grupos(self):
        conservar = self.politica.dados_a_conservar("Full", (3, 3, 5, 5, 1))
        self.assertEqual(sorted(conservar), [3, 3, 5, 5])

    def test_la_retencion_nunca_excede_cinco_dados(self):
        for valores in [(1, 1, 1, 1, 1), (1, 2, 3, 4, 5), (6, 6, 5, 5, 4)]:
            for categoria in (SEISES, TRIO, YAHTZEE, "Full", "Chance", "Escalera larga"):
                self.assertLessEqual(len(self.politica.dados_a_conservar(categoria, valores)), 5)


class TestEstrategias(unittest.TestCase):
    def test_codiciosa_elige_el_mayor_puntaje(self):
        tarjeta = Tarjeta()
        categoria = EstrategiaCodiciosa().elegir(tarjeta, (6, 6, 6, 6, 6))
        self.assertEqual(categoria, YAHTZEE)

    def test_codiciosa_respeta_casillas_ocupadas(self):
        tarjeta = Tarjeta()
        tarjeta.registrar(YAHTZEE, 50)
        categoria = EstrategiaCodiciosa().elegir(tarjeta, (6, 6, 6, 6, 6))
        self.assertNotEqual(categoria, YAHTZEE)

    def test_siempre_elige_una_casilla_libre(self):
        rng = np.random.default_rng(1)
        fabricas = (
            lambda: EstrategiaCodiciosa(),
            lambda: EstrategiaBono(),
            lambda: EstrategiaAleatoria(rng),
        )
        for fabrica in fabricas:
            tarjeta = Tarjeta()
            estrategia = fabrica()
            for _ in range(13):
                categoria = estrategia.elegir(tarjeta, (1, 2, 3, 4, 5))
                self.assertIn(categoria, tarjeta.disponibles())
                tarjeta.registrar(categoria, 0)
            self.assertTrue(tarjeta.completa())

    def test_por_nombre(self):
        self.assertIsInstance(por_nombre("aleatoria"), EstrategiaAleatoria)
        self.assertIsInstance(por_nombre("codiciosa"), EstrategiaCodiciosa)
        self.assertIsInstance(por_nombre("bono"), EstrategiaBono)

    def test_por_nombre_rechaza_desconocida(self):
        with self.assertRaises(ValueError):
            por_nombre("estrategia-inventada")

    def test_retencion_es_inyectable(self):
        estrategia = EstrategiaCodiciosa(retencion=RetencionNula())
        self.assertEqual(estrategia.retener(SEISES, (6, 6, 1, 2, 3)), ())


if __name__ == "__main__":
    unittest.main()
