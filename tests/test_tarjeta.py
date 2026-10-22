"""Pruebas de la tarjeta de puntuación."""

from __future__ import annotations

import unittest

from yahtzee.puntuacion import BONO_SUPERIOR, CATEGORIAS, SEISES, UNOS, YAHTZEE
from yahtzee.tarjeta import Tarjeta


class TestTarjeta(unittest.TestCase):
    def test_nueva_tiene_trece_casillas_libres(self):
        tarjeta = Tarjeta()
        self.assertEqual(len(tarjeta.disponibles()), len(CATEGORIAS))
        self.assertFalse(tarjeta.completa())

    def test_registrar_ocupa_la_casilla(self):
        tarjeta = Tarjeta()
        tarjeta.registrar(YAHTZEE, 50)
        self.assertNotIn(YAHTZEE, tarjeta.disponibles())
        self.assertEqual(tarjeta.puntajes[YAHTZEE], 50)

    def test_no_permite_repetir_categoria(self):
        tarjeta = Tarjeta()
        tarjeta.registrar(YAHTZEE, 50)
        with self.assertRaises(ValueError):
            tarjeta.registrar(YAHTZEE, 0)

    def test_rechaza_categoria_inexistente(self):
        with self.assertRaises(ValueError):
            Tarjeta().registrar("Categoria inventada", 10)

    def test_cero_es_distinto_de_casilla_libre(self):
        tarjeta = Tarjeta()
        tarjeta.registrar(YAHTZEE, 0)
        self.assertIn(YAHTZEE, tarjeta.puntajes)
        self.assertNotIn(YAHTZEE, tarjeta.disponibles())

    def test_bono_se_otorga_al_alcanzar_el_umbral(self):
        tarjeta = Tarjeta()
        for categoria in (UNOS, "Doses", "Treses", "Cuatros", "Cincos"):
            tarjeta.registrar(categoria, 12)
        self.assertEqual(tarjeta.total_superior(), 60)
        self.assertEqual(tarjeta.bono(), 0)

        tarjeta.registrar(SEISES, 6)
        self.assertEqual(tarjeta.total_superior(), 66)
        self.assertEqual(tarjeta.bono(), BONO_SUPERIOR)

    def test_falta_bono_es_alcanzable_al_inicio(self):
        self.assertTrue(Tarjeta().falta_bono())

    def test_falta_bono_deja_de_ser_alcanzable(self):
        tarjeta = Tarjeta()
        for categoria in (UNOS, "Doses", "Treses", "Cuatros", "Cincos", SEISES):
            tarjeta.registrar(categoria, 0)
        self.assertFalse(tarjeta.falta_bono())

    def test_total_suma_categorias_mas_bono(self):
        tarjeta = Tarjeta()
        tarjeta.registrar(YAHTZEE, 50)
        self.assertEqual(tarjeta.total(), 50)

    def test_copia_es_independiente(self):
        original = Tarjeta()
        original.registrar(YAHTZEE, 50)
        clon = original.copia()
        clon.registrar(UNOS, 3)
        self.assertIsNone(original.puntajes[UNOS])
        self.assertEqual(clon.puntajes[UNOS], 3)


if __name__ == "__main__":
    unittest.main()
