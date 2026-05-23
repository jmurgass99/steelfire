"""Tests para thermal_iter (EN 1993-1-2 retention + history)."""
import pytest

from firesteeljm.thermal_iter import (
    critical_time_to_failure,
    k_E,
    k_y,
    thermal_history,
)


def test_retencion_20C_es_1():
    assert k_E(20) == pytest.approx(1.0)
    assert k_y(20) == pytest.approx(1.0)


def test_retencion_500C_eurocodigo():
    # Tabla 3.1 EN 1993-1-2: k_E(500) = 0.60, k_y(500) = 0.78
    assert k_E(500) == pytest.approx(0.60)
    assert k_y(500) == pytest.approx(0.78)


def test_retencion_1200C_es_cero():
    assert k_E(1200) == 0.0
    assert k_y(1200) == 0.0


def test_thermal_history_genera_modifiers():
    def iso_simple(t_min: float) -> float:
        # Rampa lineal hasta 600 °C en 30 min
        return 20.0 + (600.0 - 20.0) * min(t_min / 30.0, 1.0)

    steps = thermal_history(
        time_minutes=[0, 5, 15, 30],
        temperature_provider=iso_simple,
        sections=["W14x90"],
    )
    assert len(steps) == 4
    assert steps[0].k_E == 1.0
    assert steps[-1].T_celsius == 600
    assert steps[-1].property_modifiers["E_factor"] == k_E(600)


def test_critical_time_to_failure():
    def hot_provider(t_min: float) -> float:
        return 20.0 + 30.0 * t_min  # crece rápido

    steps = thermal_history(time_minutes=list(range(0, 40)),
                             temperature_provider=hot_provider)
    # Util = 0.6 → cae primero en T tal que k_y < 0.6
    t_crit = critical_time_to_failure(steps, utilization_at_t0=0.6)
    assert 10 < t_crit < 30


def test_critical_time_inf_si_nunca_falla():
    steps = thermal_history(time_minutes=[0, 1, 2],
                             temperature_provider=lambda t: 20.0)
    assert critical_time_to_failure(steps, utilization_at_t0=0.5) == float("inf")


def test_utilizacion_invalida():
    steps = thermal_history(time_minutes=[0],
                             temperature_provider=lambda t: 20.0)
    with pytest.raises(ValueError):
        critical_time_to_failure(steps, utilization_at_t0=0)
