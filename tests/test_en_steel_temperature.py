# -*- coding: utf-8 -*-
"""Temperatura del acero EN 1993-1-2 §4.2.5 (metodo simple)."""
import pytest

from firesteeljm.en_steel_temperature import (
    ProtectedSteel,
    UnprotectedSteel,
    iso834_gas,
    shadow_factor_I,
    specific_heat_steel,
    steel_temperature_at,
    steel_temperature_history,
)


class TestSpecificHeat:
    def test_pico_cerca_735(self):
        # ca tiene un pico (singularidad fisica) cerca de 735°C.
        assert specific_heat_steel(730.0) > specific_heat_steel(400.0)

    def test_meseta_alta_temp(self):
        assert specific_heat_steel(1000.0) == 650.0


class TestUnprotected:
    def test_calienta_monotono(self):
        h = steel_temperature_history(UnprotectedSteel(Am_V_1_m=200.0), duration_min=30.0)
        temps = [t for _, t in h]
        assert all(b >= a - 1e-6 for a, b in zip(temps, temps[1:]))  # monotono
        assert temps[-1] > 500.0  # seccion ligera alcanza alta T en 30 min

    def test_mayor_factor_seccion_calienta_mas(self):
        ligera = steel_temperature_at(UnprotectedSteel(300.0), 20.0)
        pesada = steel_temperature_at(UnprotectedSteel(60.0), 20.0)
        assert ligera > pesada  # mas Am/V -> calienta mas rapido

    def test_no_supera_gas(self):
        h = steel_temperature_history(UnprotectedSteel(200.0), duration_min=30.0)
        for tmin, ta in h:
            assert ta <= iso834_gas(tmin) + 1.0


class TestProtected:
    def test_proteccion_retrasa_calentamiento(self):
        am_v = 150.0
        unprot = steel_temperature_at(UnprotectedSteel(am_v), 30.0)
        prot = steel_temperature_at(
            ProtectedSteel(Am_V_1_m=am_v, dp_m=0.020, lambda_p=0.12, cp=1100.0, rho_p=300.0),
            30.0,
        )
        assert prot < unprot  # la proteccion reduce la temperatura del acero

    def test_mas_espesor_mas_proteccion(self):
        base = dict(Am_V_1_m=150.0, lambda_p=0.12, cp=1100.0, rho_p=300.0)
        fino = steel_temperature_at(ProtectedSteel(dp_m=0.010, **base), 30.0)
        grueso = steel_temperature_at(ProtectedSteel(dp_m=0.030, **base), 30.0)
        assert grueso < fino


class TestShadow:
    def test_ksh_menor_1_para_I(self):
        # Para un perfil I, (Am/V)_box < (Am/V) -> ksh < 1.
        assert shadow_factor_I(Am_V_1_m=200.0, Am_V_box_1_m=150.0) < 1.0
