"""P1: que falte un extra opcional es un 503 con motivo, no un 500.

MEDIDO el 2026-09-17 recorriendo las 356 rutas del OpenAPI del gateway: de las
356 llamadas, **un solo 500**, y era este.

    POST /fire/curve  ->  500 Internal Server Error
    ImportError: sympy no esta instalado (instalar steelfire[analytic])

La guarda ya existia... en el sitio equivocado. `post_fire_curve` envuelve el
**import** de `fire_curves_sympy` en un `try/except ImportError -> 503`, pero ese
modulo importa perfectamente sin sympy: se guarda `_HAS_SYMPY = False` y lanza
mas tarde, dentro de `iso_834()`, cuando ya nadie escucha. El `except` cubria
una linea que nunca falla.

Un extra opcional que no esta instalado no es un fallo del servidor: es una
capacidad ausente, y el cliente tiene derecho a saber CUAL y como instalarla.
Es la misma clase que `/api/reports/pdf` con WeasyPrint sin GTK (503, no 500).

Estos tests corren instalado o no sympy: simulan la ausencia poniendo
`_HAS_SYMPY = False`, que es exactamente lo que el modulo mira.
"""
from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from steelfire.api.app import create_app  # noqa: E402


@pytest.fixture
def cliente() -> TestClient:
    return TestClient(create_app())


@pytest.fixture
def sin_sympy(monkeypatch):
    """Finge que el extra `analytic` no esta instalado."""
    from steelfire import fire_curves_sympy

    monkeypatch.setattr(fire_curves_sympy, "_HAS_SYMPY", False)
    return fire_curves_sympy


@pytest.mark.parametrize("curva", ["iso834", "hydrocarbon", "external"])
def test_la_curva_de_fuego_sin_sympy_responde_503(cliente, sin_sympy, curva) -> None:
    r = cliente.post("/fire/curve", json={"curve": curva, "t_minutes": [0, 30]})
    assert r.status_code == 503, (
        f"un extra opcional ausente no es un error del servidor: {r.status_code}")


def test_el_503_dice_QUE_falta_y_como_instalarlo(cliente, sin_sympy) -> None:
    r = cliente.post("/fire/curve", json={"curve": "iso834", "t_minutes": [0]})
    detalle = r.json().get("detail", "")
    assert "sympy" in detalle, detalle
    assert "steelfire[analytic]" in detalle, (
        "un 503 sin decir como resolverlo obliga al cliente a adivinar")


def test_la_temperatura_critica_sin_sympy_tambien_responde_503(cliente, sin_sympy) -> None:
    """La misma guarda mal puesta estaba en el segundo endpoint."""
    r = cliente.post("/fire/critical_temperature", json={"utilization": 0.6})
    assert r.status_code == 503
    assert "steelfire[analytic]" in r.json().get("detail", "")


def test_con_sympy_la_curva_se_calcula_de_verdad(cliente) -> None:
    """La guarda no puede tapar el camino bueno: con sympy instalado, ISO 834 a
    los 30 min vale 20 + 345*log10(8*30+1) = 841.8 C."""
    pytest.importorskip("sympy")
    r = cliente.post("/fire/curve", json={"curve": "iso834", "t_minutes": [30]})
    assert r.status_code == 200, r.text
    assert r.json()["theta_g_C"][0] == pytest.approx(841.8, abs=0.5)


def test_una_curva_invalida_sigue_siendo_422(cliente) -> None:
    """El 503 no puede comerse la validacion de entrada."""
    r = cliente.post("/fire/curve", json={"curve": "no-existe", "t_minutes": [0]})
    assert r.status_code == 422
