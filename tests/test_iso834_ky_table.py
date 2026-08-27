# -*- coding: utf-8 -*-
"""Bug senalado por la campana de goldens: `iso834.yield_reduction_factor` devolvia
una CONSTANTE 0.05 por encima de 800 C, cuando la Tabla 3.1 de EN 1993-1-2 sigue
decayendo: 0.11 (800) -> 0.06 (900) -> 0.04 (1000) -> 0.02 (1100) -> 0.00 (1200).

Dos defectos en uno:
* DISCONTINUIDAD en 800 C: la rama <=800 termina en 0.11 y la de >800 saltaba a
  0.05 — un salto del 55% por un epsilon de temperatura.
* Lado INSEGURO en 1100-1200 C: devolver 0.05 donde la tabla da 0.02/0.00
  SOBRESTIMA la resistencia residual (en 850-1000 C el error iba del lado
  conservador; en muy alta temperatura, del inseguro).

Oraculo: los nodos de la Tabla 3.1 transcritos A MANO aqui (los mismos que ya
vendorizo test_thermal_iter.py de forma independiente), no la funcion bajo prueba.
"""
from __future__ import annotations

import pytest

from firesteeljm.iso834 import FireEvaluator, ky_from_temperature

# EN 1993-1-2 Tabla 3.1 — k_y,theta en los nodos (transcripcion manual)
_TABLE_31 = [
    (20.0, 1.000), (100.0, 1.000), (200.0, 1.000), (300.0, 1.000),
    (400.0, 1.000), (500.0, 0.780), (600.0, 0.470), (700.0, 0.230),
    (800.0, 0.110), (900.0, 0.060), (1000.0, 0.040), (1100.0, 0.020),
    (1200.0, 0.000),
]


@pytest.mark.parametrize("t_C,ky", _TABLE_31)
def test_ky_matches_table_31_nodes(t_C, ky):
    assert ky_from_temperature(t_C) == pytest.approx(ky, abs=1e-9)


def test_no_discontinuity_at_800C():
    """El bug saltaba de 0.11 a 0.05 al cruzar 800 C por un epsilon."""
    below = ky_from_temperature(800.0)
    above = ky_from_temperature(800.0 + 1e-6)
    assert above == pytest.approx(below, abs=1e-4)


@pytest.mark.parametrize("t_C,lo,hi", [
    (850.0, 0.060, 0.110),     # interpolado entre 800 y 900
    (1150.0, 0.000, 0.020),    # interpolado entre 1100 y 1200 (el lado inseguro del bug)
])
def test_ky_interpolates_between_nodes(t_C, lo, hi):
    ky = ky_from_temperature(t_C)
    assert lo < ky < hi


def test_ky_is_zero_at_and_beyond_1200C():
    """A 1200 C el acero no aporta resistencia; el bug devolvia 0.05 eterno."""
    assert ky_from_temperature(1200.0) == pytest.approx(0.0)
    assert ky_from_temperature(1500.0) == pytest.approx(0.0)


def test_ky_is_monotonically_nonincreasing():
    temps = [20.0 + 10.0 * i for i in range(130)]
    kys = [ky_from_temperature(t) for t in temps]
    assert all(kys[i] >= kys[i + 1] - 1e-12 for i in range(len(kys) - 1))


def test_evaluator_method_uses_the_same_table():
    """El metodo de instancia debe delegar en la funcion pura (misma respuesta)."""
    ev = FireEvaluator(time_minutes=30.0, section_factor_amv=150.0)
    assert ev.yield_reduction_factor() == pytest.approx(
        ky_from_temperature(ev.steel_temperature()), abs=1e-12)
