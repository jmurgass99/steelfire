"""Tests de la capa de servicios."""
from __future__ import annotations
import pytest

from steelfire.exceptions import ConfigurationError
from steelfire.services.iso834 import ISO834Input, evaluate_iso834
from steelfire.services.thermal import (
    ThermalAnalysisInput, run_thermal_analysis,
)


def test_iso834_service_basic():
    r = evaluate_iso834(ISO834Input(time_minutes=30, section_factor_amv=150))
    assert 800 < r.gas_temperature_C < 900
    assert r.status in ("OK", "DANGER")


def test_iso834_invalid_time():
    with pytest.raises(ConfigurationError):
        evaluate_iso834(ISO834Input(time_minutes=-1))


def test_iso834_protected_lower_steel_temp():
    r_un = evaluate_iso834(ISO834Input(time_minutes=20, is_protected=False))
    r_p = evaluate_iso834(ISO834Input(time_minutes=20, is_protected=True))
    assert r_p.steel_temperature_C < r_un.steel_temperature_C


def test_thermal_service_runs():
    inp = ThermalAnalysisInput(b=0.2, h=0.3, n_x=6, n_y=8, t_total=120.0)
    r = run_thermal_analysis(inp)
    assert r.T_final_mean > 20.0
    assert r.n_steps_saved == len(r.times)


def test_thermal_service_invalid_dim():
    with pytest.raises(ConfigurationError):
        run_thermal_analysis(ThermalAnalysisInput(b=0, h=0.2))


def test_thermal_service_cfl_violation_maps_to_config_error():
    inp = ThermalAnalysisInput(b=0.2, h=0.2, n_x=20, n_y=20,
                                t_total=10.0, dt=10.0)
    with pytest.raises(ConfigurationError):
        run_thermal_analysis(inp)
