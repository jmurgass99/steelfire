"""Tests del solver FEA térmica 2D."""
from __future__ import annotations
import math
import numpy as np
import pytest

from firesteeljm.thermal_fea import (
    ThermalSection, ThermalResult, solve_thermal, c_steel, _gas_temperature_iso834,
)


def test_iso834_at_zero():
    assert _gas_temperature_iso834(0) == pytest.approx(20.0, abs=0.1)


def test_iso834_at_30min():
    T = _gas_temperature_iso834(30 * 60)
    assert 800 < T < 900  # ~841 °C


def test_c_steel_below_600():
    assert c_steel(20) > 0 and c_steel(20) < 600


def test_c_steel_peak_at_735():
    # singular alrededor de 735°C
    assert c_steel(730) > c_steel(20)


def test_thermal_fully_exposed_heats_up():
    sec = ThermalSection(b=0.2, h=0.3, n_x=8, n_y=12,
                          exposed_faces=(True, True, True, True))
    res = solve_thermal(sec, t_total=300.0)  # 5 min
    assert res.T_mean_history[-1] > 20.0
    assert res.T_max_history[-1] > res.T_max_history[0]


def test_thermal_protected_heats_less():
    sec_unprot = ThermalSection(b=0.2, h=0.3, n_x=6, n_y=8)
    sec_prot = ThermalSection(b=0.2, h=0.3, n_x=6, n_y=8,
                                protection_thickness=0.015, protection_k=0.12)
    r1 = solve_thermal(sec_unprot, t_total=600.0)
    r2 = solve_thermal(sec_prot, t_total=600.0)
    assert r2.T_max_history[-1] < r1.T_max_history[-1]


def test_thermal_three_sides_less_than_four():
    """Sección con cara superior NO expuesta (típico viga bajo losa) se
    calienta menos que totalmente expuesta."""
    sec_full = ThermalSection(b=0.2, h=0.3, n_x=6, n_y=8,
                                exposed_faces=(True, True, True, True))
    sec_3 = ThermalSection(b=0.2, h=0.3, n_x=6, n_y=8,
                             exposed_faces=(True, True, False, True))
    r_full = solve_thermal(sec_full, t_total=600.0)
    r_3 = solve_thermal(sec_3, t_total=600.0)
    assert r_3.T_mean_history[-1] < r_full.T_mean_history[-1]


def test_dt_violation_raises():
    sec = ThermalSection(b=0.2, h=0.2, n_x=20, n_y=20)
    with pytest.raises(ValueError):
        solve_thermal(sec, t_total=10.0, dt=10.0)  # demasiado grande


def test_result_arrays_lengths_match():
    sec = ThermalSection(b=0.2, h=0.2, n_x=6, n_y=6)
    res = solve_thermal(sec, t_total=120.0, t_save_every=20)
    assert len(res.times) == len(res.T_field) == len(res.T_max_history)
