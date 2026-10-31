"""Tests curvas de fuego analiticas."""
from __future__ import annotations

import pytest

sympy = pytest.importorskip("sympy")

from steelfire.fire_curves_sympy import (  # noqa: E402
    iso_834,
    hydrocarbon,
    external,
    astm_e119,
    rws,
    critical_temperature_steel,
)


def test_iso834_starts_at_20C() -> None:
    spec = iso_834()
    assert abs(float(spec.lambda_t_min(0)) - 20.0) < 0.1


def test_iso834_at_30_min_around_842C() -> None:
    """ISO 834 a 30 min ~ 842 C (valor canonico)."""
    spec = iso_834()
    val = float(spec.lambda_t_min(30))
    assert 830 < val < 850


def test_iso834_monotonic_increasing() -> None:
    spec = iso_834()
    vals = [float(spec.lambda_t_min(t)) for t in [1, 5, 10, 30, 60, 120]]
    for i in range(1, len(vals)):
        assert vals[i] > vals[i - 1]


def test_iso834_latex_and_derivative() -> None:
    spec = iso_834()
    assert "log" in spec.latex
    # derivada en t=1 min positiva (curva sube)
    assert float(spec.derivative_callable(1)) > 0


def test_hydrocarbon_reaches_1080_plus_20() -> None:
    """Hidrocarburica asintotica a ~1100 C."""
    spec = hydrocarbon()
    val = float(spec.lambda_t_min(120))
    assert 1050 < val < 1100


def test_external_lower_than_iso834() -> None:
    """Externa siempre <= ISO 834 a 60 min."""
    iso = float(iso_834().lambda_t_min(60))
    ext = float(external().lambda_t_min(60))
    assert ext < iso


def test_critical_temperature_decreasing_with_utilization() -> None:
    """Mayor utilizacion -> menor temperatura critica."""
    t1 = critical_temperature_steel(0.3)
    t2 = critical_temperature_steel(0.7)
    assert t1 > t2


def test_critical_temperature_typical_range() -> None:
    """utilizacion 0.65 -> ~ 545 C (tabulado EN 1993-1-2)."""
    t = critical_temperature_steel(0.65)
    assert 530 < t < 565


def test_critical_temperature_invalid_raises() -> None:
    with pytest.raises(ValueError):
        critical_temperature_steel(0.005)
    with pytest.raises(ValueError):
        critical_temperature_steel(1.5)


# ---- ASTM E119 ----

def test_astm_e119_at_t0_is_20() -> None:
    spec = astm_e119()
    assert abs(float(spec.lambda_t_min(0)) - 20.0) < 0.1


def test_astm_e119_monotone() -> None:
    """ASTM E119 es monotona creciente en [0, 4h]."""
    spec = astm_e119()
    vals = [float(spec.lambda_t_min(t)) for t in [0, 1, 5, 10, 30, 60, 120, 240]]
    for i in range(1, len(vals)):
        assert vals[i] > vals[i - 1]


def test_astm_e119_at_1h_approx_927() -> None:
    """ASTM E119 a 60 min ~ 920-935 C (Lie formula analitica)."""
    spec = astm_e119()
    val = float(spec.lambda_t_min(60))
    assert 920 < val < 935


# ---- RWS (Rijkswaterstaat) ----

def test_rws_at_t0_is_20() -> None:
    spec = rws()
    assert abs(float(spec.lambda_t_min(0)) - 20.0) < 0.1


def test_rws_peak_1350() -> None:
    """RWS alcanza su maximo de 1350 C a 60 min."""
    spec = rws()
    val = float(spec.lambda_t_min(60))
    assert abs(val - 1350.0) < 1e-6


def test_rws_at_180_is_zero() -> None:
    """RWS se extingue a 180 min (0 C)."""
    spec = rws()
    val = float(spec.lambda_t_min(180))
    assert abs(val - 0.0) < 1e-6
