from __future__ import annotations

import pytest

from steelfire.en_steel_temperature import (
    ParametricFireInput,
    UnprotectedSteel,
    parametric_fire_curve,
    parametric_fire_gas,
    steel_temperature_at,
)
from steelfire.fem_thermal_1d import Material1D, solve_1d_thermal
from steelfire.services.iso834 import ISO834Input, evaluate_iso834
from steelfire.thermal_fea import ThermalSection, k_steel, solve_thermal


def test_k_steel_en1993_1_2_and_2d_variable_k():
    assert k_steel(20.0) == pytest.approx(54.0 - 3.33e-2 * 20.0)
    assert k_steel(800.0) == pytest.approx(27.3)
    assert k_steel(1000.0) == pytest.approx(27.3)

    sec = ThermalSection(b=0.10, h=0.10, n_x=8, n_y=8)
    res_const = solve_thermal(sec, t_total=300.0, variable_k=False)
    res_var = solve_thermal(sec, t_total=300.0, variable_k=True)
    assert res_var.T_max_history[-1] > 20.0
    assert res_var.T_mean_history[-1] != pytest.approx(res_const.T_mean_history[-1], rel=1e-4)


def test_1d_fem_variable_steel_and_radiation():
    layers = [
        Material1D("Vermiculite", thickness_m=0.015, k_W_per_mK=0.12, rho_kg_m3=400.0, c_J_per_kgK=1100.0),
        Material1D("Steel flange", thickness_m=0.012, k_W_per_mK=45.0, rho_kg_m3=7850.0, c_J_per_kgK=600.0),
    ]
    r_base = solve_1d_thermal(layers, lambda t_min: 20.0 + 345.0 * (0.5 if t_min > 0 else 0.0), duration_s=600.0)
    r_rad = solve_1d_thermal(
        layers,
        lambda t_min: 20.0 + 345.0 * (0.5 if t_min > 0 else 0.0),
        duration_s=600.0,
        variable_steel_properties=True,
        include_radiation=True,
    )
    assert r_rad.temperatures_K[-1][0] > r_base.temperatures_K[-1][0]


def test_parametric_fire_curve_heating_and_cooling():
    inp = ParametricFireInput(O_m_half=0.08, b_J_m2s05K=1160.0, q_t_d_MJ_m2=120.0)
    curve = parametric_fire_curve(inp)
    t_peak = curve(18.0)
    t_cool = curve(60.0)
    assert t_peak > 600.0
    # After burnout (t > t_max = 18 min), cooling phase reduces gas temperature
    assert t_cool < t_peak

    t_steel = steel_temperature_at(UnprotectedSteel(Am_V_1_m=150.0), duration_min=30.0, gas_curve=curve)
    assert t_steel > 200.0


def test_iso834_service_exact_en1993_incremental():
    inp_simp = ISO834Input(time_minutes=30.0, section_factor_amv=150.0, use_en1993_exact_c_a=False)
    inp_exact = ISO834Input(time_minutes=30.0, section_factor_amv=150.0, use_en1993_exact_c_a=True)
    res_simp = evaluate_iso834(inp_simp)
    res_exact = evaluate_iso834(inp_exact)
    assert res_exact.steel_temperature_C > 500.0
    assert res_exact.steel_temperature_C != res_simp.steel_temperature_C
