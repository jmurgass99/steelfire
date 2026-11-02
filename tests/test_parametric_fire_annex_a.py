"""Curva paramétrica de EN 1991-1-2 Anexo A: continuidad en t_max y definición de t*_max (Ec. A.12)."""
import math

import pytest

from steelfire.en_steel_temperature import parametric_fire_gas


def _heating(t_star):
    return 20.0 + 1325.0 * (1 - 0.324 * math.exp(-0.2 * t_star) - 0.204 * math.exp(-1.7 * t_star)
                            - 0.472 * math.exp(-19.0 * t_star))


@pytest.mark.parametrize("O, q", [(0.04, 150.0), (0.10, 150.0), (0.10, 300.0), (0.15, 100.0)])
def test_gas_temperature_is_continuous_at_t_max(O, q):
    t_max_min = max(0.2e-3 * q / O, 20.0 / 60.0) * 60.0
    before = parametric_fire_gas(t_max_min - 1e-6, O_m_half=O, q_t_d_MJ_m2=q)
    after = parametric_fire_gas(t_max_min + 1e-6, O_m_half=O, q_t_d_MJ_m2=q)
    assert after == pytest.approx(before, abs=0.1)


def test_fuel_controlled_cooling_by_hand():
    """O = 0,10, q = 150, b = 1160, t_lim = 20 min: fuego controlado por el combustible (18 < 20 min)."""
    O, q = 0.10, 150.0
    gamma = (O / 0.04) ** 2
    o_lim = 0.1e-3 * q / (20.0 / 60.0)
    gamma_lim = (o_lim / 0.04) ** 2
    theta_max = _heating(gamma_lim * 20.0 / 60.0)
    t_star_max = gamma * 0.2e-3 * q / O                      # Ec. (A.12)
    x = (20.0 / 60.0) * gamma / t_star_max
    t = 40.0
    expected = theta_max - 250.0 * (3.0 - t_star_max) * (gamma * t / 60.0 - t_star_max * x)
    assert 0.5 < t_star_max < 2.0
    assert parametric_fire_gas(t, O_m_half=O, q_t_d_MJ_m2=q) == pytest.approx(max(expected, 20.0), rel=1e-9)
