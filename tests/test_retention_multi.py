"""Tests retention factors multi-código."""
import pytest

from firesteeljm.retention_multi import retention_factor


def test_20C_es_1_en_todos():
    for c in ("EU", "SG", "US", "CO", "AU"):
        assert retention_factor(20, "E", c) == 1.0
        assert retention_factor(20, "Fy", c) == 1.0


def test_eu_500C():
    assert retention_factor(500, "E", "EU") == pytest.approx(0.60)
    assert retention_factor(500, "Fy", "EU") == pytest.approx(0.78)


def test_us_diferente_de_eu():
    # AISC quadratic differs from EN piecewise
    eu = retention_factor(400, "E", "EU")
    us = retention_factor(400, "E", "US")
    assert abs(eu - us) > 0  # son distintos


def test_T_alto_va_a_cero():
    for c in ("EU", "US", "AU"):
        assert retention_factor(1200, "E", c) <= 0.05
