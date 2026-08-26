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


# ---------------------------------------------------------------------------
# GOLDEN — retention_multi.py duplica la Tabla 3.1 de thermal_iter.py en sus
# propios arrays (_EN_ky/_EN_kE). Se replican aqui los mismos anclajes
# interpolados de W01409/W01411 (ver tests/test_thermal_iter.py) para que una
# edicion accidental de ESTA copia de la tabla tambien falle en rojo.
# Oraculo independiente: interpolacion lineal manual de Tabla 3.1 EN 1993-1-2,
# no reimportada del modulo.
# ---------------------------------------------------------------------------

def test_golden_w01409_ky_eu_595_5C():
    """W01409 (viga IPE550/S235): eta_fi=k_y,theta=0.4840 -> Ta=595.5C.

    ky(595.5) = 0.780 - 0.31*(595.5-500)/100 = 0.48395 (Tabla 3.1, EU).
    """
    assert retention_factor(595.5, "Fy", "EU") == pytest.approx(0.48395, abs=1e-4)


def test_golden_w01411_ky_kE_eu_567_8C():
    """W01411 (pilar HEB, pandeo en fuego): Ta_crit=567.8C.

    ky(567.8) = 0.780 - 0.31*(567.8-500)/100 = 0.56982 (coincide con ficha).
    kE(567.8) = 0.600 - 0.29*(567.8-500)/100 = 0.40338 (ficha cita 0.4004,
    ERRATA de ~0.003 -- se ancla el valor recalculado, ver test_thermal_iter.py).
    """
    assert retention_factor(567.8, "Fy", "EU") == pytest.approx(0.56982, abs=1e-4)
    assert retention_factor(567.8, "E", "EU") == pytest.approx(0.40338, abs=1e-4)
