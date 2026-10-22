"""Pruebas de las reglas de puntuación."""

from __future__ import annotations

import unittest

from yahtzee.puntuacion import (
    CATEGORIAS,
    CHANCE,
    CINCOS,
    CUATROS,
    DOSES,
    ESCALERA_CORTA,
    ESCALERA_LARGA,
    FULL,
    POKER,
    SEISES,
    TRIO,
    UNOS,
    YAHTZEE,
    es_cinco_iguales,
    puntuar,
)


class TestSeccionSuperior(unittest.TestCase):
    def test_suma_solo_los_dados_de_la_cara(self):
        self.assertEqual(puntuar(UNOS, (1, 1, 3, 4, 1)), 3)
        self.assertEqual(puntuar(SEISES, (6, 6, 3, 1, 2)), 12)

    def test_sin_coincidencias_vale_cero(self):
        self.assertEqual(puntuar(CINCOS, (1, 2, 3, 4, 6)), 0)

    def test_caras_altas(self):
        self.assertEqual(puntuar(DOSES, (2, 2, 2, 2, 2)), 10)
        self.assertEqual(puntuar(CUATROS, (4, 4, 4, 4, 4)), 20)


class TestSeccionInferior(unittest.TestCase):
    def test_trio(self):
        self.assertEqual(puntuar(TRIO, (2, 2, 2, 5, 6)), 17)
        self.assertEqual(puntuar(TRIO, (2, 2, 5, 5, 6)), 0)

    def test_poker(self):
        self.assertEqual(puntuar(POKER, (2, 2, 2, 2, 5)), 13)
        self.assertEqual(puntuar(POKER, (2, 2, 2, 5, 5)), 0)

    def test_full_exige_tres_y_dos(self):
        self.assertEqual(puntuar(FULL, (3, 3, 3, 5, 5)), 25)
        self.assertEqual(puntuar(FULL, (3, 3, 5, 5, 6)), 0)

    def test_yahtzee_no_vale_como_full(self):
        # Variante estricta: cinco iguales no es un full.
        self.assertEqual(puntuar(FULL, (4, 4, 4, 4, 4)), 0)

    def test_escalera_corta(self):
        self.assertEqual(puntuar(ESCALERA_CORTA, (1, 2, 3, 4, 6)), 30)
        self.assertEqual(puntuar(ESCALERA_CORTA, (2, 3, 4, 5, 5)), 30)
        self.assertEqual(puntuar(ESCALERA_CORTA, (1, 2, 3, 5, 6)), 0)

    def test_escalera_larga(self):
        self.assertEqual(puntuar(ESCALERA_LARGA, (1, 2, 3, 4, 5)), 40)
        self.assertEqual(puntuar(ESCALERA_LARGA, (2, 3, 4, 5, 6)), 40)
        self.assertEqual(puntuar(ESCALERA_LARGA, (1, 2, 3, 4, 6)), 0)

    def test_yahtzee(self):
        self.assertEqual(puntuar(YAHTZEE, (6, 6, 6, 6, 6)), 50)
        self.assertEqual(puntuar(YAHTZEE, (6, 6, 6, 6, 5)), 0)

    def test_chance_suma_todo(self):
        self.assertEqual(puntuar(CHANCE, (1, 1, 1, 1, 1)), 5)
        self.assertEqual(puntuar(CHANCE, (1, 2, 3, 4, 6)), 16)


class TestContrato(unittest.TestCase):
    def test_categoria_desconocida(self):
        with self.assertRaises(ValueError):
            puntuar("Escalera imposible", (1, 2, 3, 4, 5))

    def test_toda_categoria_tiene_regla(self):
        for categoria in CATEGORIAS:
            self.assertIsInstance(puntuar(categoria, (1, 2, 3, 4, 5)), int)

    def test_puntajes_no_negativos(self):
        for categoria in CATEGORIAS:
            for valores in [(1, 1, 1, 1, 1), (1, 2, 3, 4, 5), (6, 6, 5, 5, 4)]:
                self.assertGreaterEqual(puntuar(categoria, valores), 0)

    def test_es_cinco_iguales(self):
        self.assertTrue(es_cinco_iguales((3, 3, 3, 3, 3)))
        self.assertFalse(es_cinco_iguales((3, 3, 3, 3, 4)))


if __name__ == "__main__":
    unittest.main()
