"""Tests de integración y golden para comprobación de resistencia al fuego de perfiles.

Norma: EN 1993-1-2 §4.2.4 (Temperatura crítica) y §4.2.5 (Evolución térmica del acero).
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from steelfire.api.app import create_router
from steelfire.en_steel_temperature import (
    critical_temperature,
    check_fire_resistance_from_profile,
)


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(create_router())
    return TestClient(app)


def test_critical_temperature_golden_hand_calc():
    """Golden analítico exacto de temperatura crítica según EN 1993-1-2 §4.2.4.

    theta_a,cr = 39.19 * ln(1 / (0.9674 * mu0^3.833) - 1) + 482
    Para mu0 = 0.65:
      theta_crit = 539.87 °C
    """
    mu0 = 0.65
    theta_cr = critical_temperature(mu0)
    assert theta_cr == pytest.approx(539.87, rel=1e-3)


def test_fire_check_profile_api_endpoint(client):
    """Verifica endpoint HTTP /api/fire/check-profile."""
    payload = {
        "section_name": "IPE 300",
        "Am_V_m_inv": 200.0,
        "load_ratio_mu0": 0.65,
        "required_rating": "R60",
        "preferred_protection_type": "spray_mortar",
    }
    resp = client.post("/api/fire/check-profile", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["section_name"] == "IPE 300"
    assert data["required_rating"] == "R60"
    assert data["duration_min"] == 60.0
    assert data["theta_crit_C"] == pytest.approx(539.87, rel=1e-3)
    assert data["requires_protection"] is True
    assert data["theta_unprotected_C"] > 750.0
