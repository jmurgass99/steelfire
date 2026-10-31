"""Tests del endpoint REST (FastAPI TestClient)."""
from __future__ import annotations
import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from steelfire.api.app import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


def test_iso834_endpoint(client: TestClient) -> None:
    r = client.post("/api/thermal/iso834",
                     json={"time_minutes": 30, "section_factor_amv": 150})
    assert r.status_code == 200
    body = r.json()
    assert "gas_temperature_C" in body
    assert 800 < body["gas_temperature_C"] < 900


def test_iso834_endpoint_invalid(client: TestClient) -> None:
    r = client.post("/api/thermal/iso834", json={"time_minutes": -1})
    # pydantic validation -> 422
    assert r.status_code == 422


def test_section_endpoint(client: TestClient) -> None:
    r = client.post("/api/thermal/section",
                     json={"b": 0.2, "h": 0.3, "n_x": 6, "n_y": 8,
                           "t_total": 180.0, "t_save_every": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["T_final_mean"] > 20.0
    assert body["n_steps_saved"] >= 1


def test_section_endpoint_bad_config(client: TestClient) -> None:
    r = client.post("/api/thermal/section",
                     json={"b": 0.2, "h": 0.2, "n_x": 20, "n_y": 20,
                           "t_total": 10.0, "dt": 10.0})
    # CFL -> ConfigurationError -> 400
    assert r.status_code == 400


# --- nuevos endpoints sympy ---------------------------------------------------
_HAS_SYMPY = True
try:
    import sympy  # noqa: F401
except ImportError:  # pragma: no cover
    _HAS_SYMPY = False


def test_health(client: TestClient) -> None:
    r = client.get("/api/thermal/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["app"] == "SteelFire"


@pytest.mark.skipif(not _HAS_SYMPY, reason="sympy no instalado")
def test_fire_curve_iso834(client: TestClient) -> None:
    r = client.post("/fire/curve", json={
        "curve": "iso834",
        "t_minutes": [0, 30, 60, 120],
    })
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["curve_name"] == "ISO 834"
    assert len(data["theta_g_C"]) == 4
    assert abs(data["theta_g_C"][0] - 20.0) < 0.5
    # a 30 min ~ 842 C
    assert 830 < data["theta_g_C"][1] < 850
    assert "latex" in data and data["latex"]


@pytest.mark.skipif(not _HAS_SYMPY, reason="sympy no instalado")
def test_fire_curve_hydrocarbon(client: TestClient) -> None:
    r = client.post("/fire/curve", json={"curve": "hydrocarbon", "t_minutes": [120]})
    assert r.status_code == 200
    assert 1050 < r.json()["theta_g_C"][0] < 1100


@pytest.mark.skipif(not _HAS_SYMPY, reason="sympy no instalado")
def test_critical_temperature_endpoint(client: TestClient) -> None:
    r = client.post("/fire/critical_temperature", json={"utilization": 0.65})
    assert r.status_code == 200
    data = r.json()
    assert 500 < data["critical_temperature_C"] < 600


@pytest.mark.skipif(not _HAS_SYMPY, reason="sympy no instalado")
def test_critical_temperature_invalid(client: TestClient) -> None:
    r = client.post("/fire/critical_temperature", json={"utilization": 0.005})
    assert r.status_code in (400, 422)
