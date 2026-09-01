"""Golden test para chequeo de resistencia al fuego de perfiles estructurales (EN 1993-1-2 y catálogo).

Requisitos:
1. Cálculo de temperatura crítica θ_crit según EN 1993-1-2 §4.2.4 para grado de utilización μ_0.
2. Comprobación a 60 min (R60): detección de necesidad de protección pasiva.
3. Dimensionado y selección desde protection_catalog con espesor en mm y especificación de material.
"""
from __future__ import annotations

import pytest
from firesteeljm.en_steel_temperature import (
    critical_temperature,
    check_fire_resistance_from_profile,
)


def test_golden_fire_resistance_check_ipe300_r60():
    """GOLDEN. Verificación de temperatura crítica y protección pasiva para IPE 300 bajo R60."""
    mu0 = 0.65
    Am_V = 200.0  # m^-1

    # 1. Temperatura crítica analítica exacta EN 1993-1-2 §4.2.4
    theta_crit = critical_temperature(mu0)
    assert theta_crit == pytest.approx(539.87, rel=1e-3)

    # 2. Chequeo de perfil para R60
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=Am_V,
        load_ratio_mu0=mu0,
        required_rating="R60",
        preferred_protection_type="intumescent",
    )

    assert res.section_name == "IPE 300"
    assert res.required_rating == "R60"
    assert res.duration_min == 60.0
    assert res.theta_crit_C == pytest.approx(539.87, rel=1e-3)

    # Sin protección, la temperatura supera con creces los 540 °C (> 800 °C)
    assert res.theta_unprotected_C > 750.0
    assert res.requires_protection is True

    # 3. Asignación de protección pasiva desde el catálogo
    assert res.recommended_protection is not None
    prot = res.recommended_protection
    assert "INT" in prot["code"] or "mortar" in prot["code"]
    assert prot["thickness_mm"] > 0.0
    assert prot["cost_USD_per_m2"] > 0.0
