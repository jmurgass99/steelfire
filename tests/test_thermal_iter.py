"""Tests para thermal_iter (EN 1993-1-2 retention + history)."""
import pytest

from firesteeljm.thermal_iter import (
    critical_time_to_failure,
    k_E,
    k_p,
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


# ---------------------------------------------------------------------------
# GOLDEN — EN 1993-1-2 §3.2.1 Tabla 3.1 (factores de reduccion del acero al
# carbono). Valores normativos tabulados, transcritos de ficha W01421
# (apuntes UPC "Fire design new_2022", tabla pp. 76-91, columnas ky,θ / kp,θ /
# kE,θ). Anclados como LITERALES (no leidos de los arrays del modulo) -> actuan
# como guarda de regresion frente a edicion accidental de las tablas.
# ---------------------------------------------------------------------------

# (theta_C, k_y, k_E) en los nodos exactos de la Tabla 3.1.
_TABLA_3_1_KY_KE = [
    (20, 1.000, 1.000),
    (100, 1.000, 1.000),
    (200, 1.000, 0.900),
    (300, 1.000, 0.800),
    (400, 1.000, 0.700),
    (500, 0.780, 0.600),
    (600, 0.470, 0.310),
    (700, 0.230, 0.130),
    (800, 0.110, 0.090),
    (900, 0.060, 0.0675),
    (1000, 0.040, 0.0450),
    (1100, 0.020, 0.0225),
    (1200, 0.000, 0.000),
]


@pytest.mark.parametrize("theta_C, ky_ref, kE_ref", _TABLA_3_1_KY_KE)
def test_golden_tabla_3_1_ky_kE(theta_C, ky_ref, kE_ref):
    """W01421 / EN 1993-1-2 §3.2.1 Tabla 3.1: ky,θ y kE,θ exactos en cada nodo."""
    assert k_y(theta_C) == pytest.approx(ky_ref, abs=1e-6)
    assert k_E(theta_C) == pytest.approx(kE_ref, abs=1e-6)


# (theta_C, k_p,θ) — limite de proporcionalidad, Tabla 3.1 columna kp,θ.
_TABLA_3_1_KP = [
    (20, 1.000),
    (100, 1.000),
    (200, 0.807),
    (300, 0.613),
    (400, 0.420),
    (500, 0.360),
    (600, 0.180),
    (700, 0.075),
    (800, 0.050),
    (900, 0.0375),
    (1000, 0.0250),
    (1100, 0.0125),
    (1200, 0.000),
]


@pytest.mark.parametrize("theta_C, kp_ref", _TABLA_3_1_KP)
def test_golden_tabla_3_1_kp(theta_C, kp_ref):
    """W01421 / EN 1993-1-2 §3.2.1 Tabla 3.1: kp,θ (limite proporcional) exacto."""
    assert k_p(theta_C) == pytest.approx(kp_ref, abs=1e-6)


def test_golden_kp_discrimina_de_ky():
    """200/300/400°C: ky,θ=1.0 pero kp,θ=0.807/0.613/0.420 (Tabla 3.1).

    En este tramo kp,θ ya degrada mientras ky,θ aun vale 1.0 -> prueba que
    k_p NO es un alias de k_y (anclaje discriminante, W01421).
    """
    for theta_C, kp_ref in [(200, 0.807), (300, 0.613), (400, 0.420)]:
        assert k_y(theta_C) == pytest.approx(1.0)
        assert k_p(theta_C) == pytest.approx(kp_ref, abs=1e-6)
        assert k_p(theta_C) < k_y(theta_C)


def test_golden_kp_interpola_lineal_550C():
    """kp,θ interpola linealmente entre nodos: 550°C -> (0.360+0.180)/2 = 0.270."""
    assert k_p(550) == pytest.approx(0.270, abs=1e-6)


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
