"""Consistencia energética del solver térmico 2D: media ≈ masa concentrada y convergencia con la malla.

Para una barra maciza expuesta por las cuatro caras, el calor que entra por unidad de
longitud es q·P y la capacidad es ρ·c·A, de modo que la temperatura media de la sección
debe seguir el modelo de masa concentrada de EN 1993-1-2 §4.2.5.1 (ec. 4.25) con
Am/V = P/A y el mismo flujo neto (α_c = 25 W/m²K, ε = 0,7, k_sh = 1). Las diferencias
que quedan vienen de la conducción finita (k = 45 W/mK) y de evaluar c_a a la
temperatura media; para una barra de 60 mm son de pocos por ciento.

Hasta 2026-10-31 las celdas de borde no conducían hacia el interior: la media de una
sección 200x200 a 10 min daba 132/208/324 °C con 5/10/20 divisiones y la barra de 60 mm
calentaba casi el doble que el modelo de masa concentrada. Estos tests fijan la corrección.
"""
from __future__ import annotations

import pytest

from steelfire import ThermalSection, solve_thermal
from steelfire.en_steel_temperature import UnprotectedSteel, steel_temperature_history

SIDE = 0.06
AM_V = 4.0 / SIDE


def _mean_at(res, t_s: float) -> float:
    i = min(range(len(res.times)), key=lambda k: abs(res.times[k] - t_s))
    return float(res.T_mean_history[i])


def test_section_mean_tracks_lumped_en1993_1_2_model():
    res = solve_thermal(ThermalSection(b=SIDE, h=SIDE, n_x=12, n_y=12), t_total=1800.0)
    lumped = steel_temperature_history(UnprotectedSteel(Am_V_1_m=AM_V, ksh=1.0), duration_min=30.0, dt_s=5.0)
    for t_min in (10, 20, 30):
        T_l = next(th for tm, th in lumped if tm >= t_min - 1e-9)
        T_2d = _mean_at(res, 60.0 * t_min)
        assert T_2d == pytest.approx(T_l, rel=0.06), (t_min, T_2d, T_l)


def test_mean_temperature_converges_with_mesh():
    means = []
    for n in (5, 10, 20):
        res = solve_thermal(ThermalSection(b=0.20, h=0.20, n_x=n, n_y=n), t_total=600.0)
        means.append(float(res.T_mean_history[-1]))
    assert abs(means[1] - means[2]) / means[2] < 0.05
    assert abs(means[0] - means[2]) / means[2] < 0.10


def test_boundary_cells_conduct_inwards():
    """Con conducción real, la celda de borde no puede estar mucho más caliente que su vecina."""
    res = solve_thermal(ThermalSection(b=0.20, h=0.20, n_x=20, n_y=20), t_total=600.0)
    T = res.T_field[-1]
    mid = T.shape[1] // 2
    assert T[0, mid] - T[1, mid] < 60.0
