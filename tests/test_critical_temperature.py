"""Tests para la memoria de temperatura critica (EN 1993-1-2 S4.2.4)."""
from __future__ import annotations

import math

import pytest

from firesteeljm.memos.critical_temperature import (
    CriticalTempMemoInput,
    render_critical_temp_memo,
    render_critical_temp_memo_full,
    _critical_temperature,
)


class TestCriticalTemperature:
    """Verificacion de la formula de temperatura critica."""

    def test_mu_05_gives_585(self):
        """mu_0 = 0.5 -> theta_cr ~ 585 C (valor tabulado EN 1993-1-2)."""
        theta_cr = _critical_temperature(0.5)
        assert theta_cr == pytest.approx(585, abs=2)

    def test_low_load_ratio_high_temperature(self):
        """Baja carga -> alta temperatura critica."""
        theta_cr = _critical_temperature(0.1)
        assert theta_cr > 700

    def test_high_load_ratio_low_temperature(self):
        """Alta carga -> baja temperatura critica."""
        theta_cr = _critical_temperature(0.9)
        assert theta_cr < 500

    def test_monotone_decreasing(self):
        """theta_cr debe decrecer con mu_0."""
        mus = [0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
        temps = [_critical_temperature(m) for m in mus]
        for i in range(len(temps) - 1):
            assert temps[i] > temps[i + 1]


class TestRenderMemoString:
    """Verificacion de la funcion render_critical_temp_memo (string)."""

    def test_render_not_empty(self):
        """El render debe devolver una cadena no vacia."""
        result = render_critical_temp_memo(
            member_type="beam",
            load_ratio=0.5,
            section="IPE 300",
            Am_V=200.0,
        )
        assert isinstance(result, str)
        assert len(result) > 100

    def test_render_contains_critical_temperature(self):
        """El markdown debe contener la temperatura critica."""
        result = render_critical_temp_memo(load_ratio=0.5)
        assert "585" in result or "584" in result

    def test_render_contains_section_info(self):
        """El markdown debe contener info de seccion."""
        result = render_critical_temp_memo(
            section="HEB 200", member_type="column",
        )
        assert "HEB 200" in result
        assert "column" in result


class TestRenderMemoFull:
    """Verificacion de render_critical_temp_memo_full."""

    def test_mu_05_result(self):
        """mu_0=0.5 produce resultado coherente."""
        data = CriticalTempMemoInput(load_ratio=0.5, Am_V=200.0)
        result = render_critical_temp_memo_full(data)
        assert result.mu_0 == 0.5
        assert result.theta_cr_C == pytest.approx(585, abs=2)
        assert result.t_cr_min is not None
        assert result.t_cr_min > 0
        assert len(result.markdown) > 0
        assert len(result.latex) > 0

    def test_collapse_time_increases_with_protection(self):
        """Seccion protegida debe tener mayor tiempo de colapso."""
        data_bare = CriticalTempMemoInput(load_ratio=0.5, Am_V=200.0)
        data_prot = CriticalTempMemoInput(
            load_ratio=0.5, Am_V=200.0,
            protected=True, dp_m=0.02,
            lambda_p=0.12, cp=1200.0, rho_p=600.0,
        )
        r_bare = render_critical_temp_memo_full(data_bare)
        r_prot = render_critical_temp_memo_full(data_prot)
        assert r_prot.t_cr_min is not None
        assert r_bare.t_cr_min is not None
        assert r_prot.t_cr_min > r_bare.t_cr_min

    def test_pass_check_with_fire_resistance(self):
        """Verificacion pass/fail con requisito de resistencia."""
        data = CriticalTempMemoInput(load_ratio=0.5, Am_V=200.0)
        result = render_critical_temp_memo_full(data, fire_resistance_min=5.0)
        # t_cr para seccion sin proteger con Am/V=200 y mu=0.5
        # deberia estar alrededor de 10-20 min
        assert result.pass_check is True

    def test_to_dict(self):
        """to_dict produce diccionario con campos esperados."""
        data = CriticalTempMemoInput(load_ratio=0.5, Am_V=200.0)
        result = render_critical_temp_memo_full(data)
        d = result.to_dict()
        assert "mu_0" in d
        assert "theta_cr_C" in d
        assert "t_cr_min" in d
        assert "pass_check" in d

    def test_invalid_load_ratio_raises(self):
        """load_ratio fuera de rango debe lanzar ValueError."""
        data = CriticalTempMemoInput(load_ratio=1.5, Am_V=200.0)
        with pytest.raises(ValueError):
            render_critical_temp_memo_full(data)
