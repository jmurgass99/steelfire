"""Tests FEM 1D thermal."""
import pytest

from steelfire.fem_thermal_1d import Material1D, solve_1d_thermal


def iso834(t_min: float) -> float:
    """ISO 834 — temperatura del fuego (°C)."""
    import math
    return 345 * math.log10(8 * t_min + 1) + 20


def test_solver_runs_without_error():
    layers = [
        Material1D("intumescent", 0.003, 0.10, 1300, 900),
        Material1D("steel", 0.020, 50.0, 7850, 600),
    ]
    r = solve_1d_thermal(layers, iso834, duration_s=600, dt_s=30,
                          n_elements_per_layer=4)
    assert len(r.times_s) > 0
    assert len(r.temperatures_K) == len(r.times_s)


def test_acero_se_calienta():
    layers = [
        Material1D("steel", 0.020, 50.0, 7850, 600),
    ]
    r = solve_1d_thermal(layers, iso834, duration_s=900, dt_s=30,
                          n_elements_per_layer=5)
    # La temperatura en el último snapshot debe ser > inicial
    T_final = r.temperatures_K[-1]
    assert max(T_final) > 350  # > 80°C (293+80)
