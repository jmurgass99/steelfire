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


class TestGoldenCriticalTemperature:
    """GOLDEN — theta_a,cr (EN 1993-1-2 §4.2.4, Eq. 4.22) anclada a casos
    resueltos a mano de la ficha W01437 ('Ejercicios de Fuego (EC3-1-2)',
    examenes UPC). Cada mu_0 -> theta_cr fue calculado independientemente por
    el alumno; aqui se verifica que la formula del modulo reproduce esos
    numeros. Los valores de referencia son LITERALES de la ficha (no derivados
    del propio modulo) -> golden honesto, no tautologico.

        theta_cr = 39.19 * ln[1/(0.9674*mu_0^3.833) - 1] + 482
    """

    # (mu_0, theta_cr_ficha_C, ejercicio) — W01437.
    # Tolerancia +-1.5°C: la ficha redondea theta_cr al grado.
    _CASOS = [
        (0.484, 589.9, "GT3 viga IPE550/S235"),
        (0.43, 609.0, "GT4 viga IPE270/S235"),
        (0.28, 674.0, "GT4 tirante 2L40x4"),
        (0.16, 758.55, "GT1/GT5 columna HEB220/240"),
        (0.571, 563.0, "GT5 columna HEB220 (metodo pandeo)"),
    ]

    @pytest.mark.parametrize("mu_0, theta_ref, label", _CASOS)
    def test_golden_w01437(self, mu_0, theta_ref, label):
        """W01437 §4.2.4 Eq 4.22: theta_cr(mu_0) reproduce el valor de examen."""
        assert _critical_temperature(mu_0) == pytest.approx(theta_ref, abs=1.5)

    def test_golden_w01437_exacto_mu_016(self):
        """W01437 ej.5: mu_0=0.16 -> theta_cr=758.55°C (coincide al centesimo)."""
        # La ficha cita 758.55°C; verificamos la concordancia estrecha.
        assert _critical_temperature(0.16) == pytest.approx(758.55, abs=0.1)


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
