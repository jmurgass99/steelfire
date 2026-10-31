# -*- coding: utf-8 -*-
"""Temperatura del acero EN 1993-1-2 §4.2.5 (metodo simple)."""
import pytest

from steelfire.en_steel_temperature import (
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


# ---------------------------------------------------------------------------
# GOLDEN — EN 1993-1-2:2005 §4.2.5.1, incremento de temperatura de una seccion
# de acero SIN PROTEGER.
#
# Fuente citada, Ecuacion (4.25):
#
#     Delta_theta_a,t = ksh · (Am/V)/(ca·rho_a) · h_net,d · Delta_t
#
# con h_net,d = h_net,c + h_net,r (EN 1991-1-2 §3.3.1):
#
#     h_net,c = alpha_c·(theta_g - theta_m)                        Ec. (3.1)
#     h_net,r = Phi·eps_m·eps_f·sigma·[(theta_g+273)^4 - (theta_m+273)^4]
#                                                                  Ec. (3.2)
#
# Constantes que usa el modulo (coinciden con la norma para fuego nominal
# estandar):  alpha_c = 25 W/m^2K (EN 1991-1-2 §3.2.1),  Phi = 1.0,
# eps_m·eps_f = 0.7 (EN 1993-1-2 §2.2(2) eps_m = 0.7, eps_f = 1.0),
# sigma = 5.67e-8 W/m^2K^4,  rho_a = 7850 kg/m^3 (§3.2.2).
# El calor especifico ca(theta) es el de EN 1993-1-2 §3.4.1.2.
#
# Para que la derivacion sea reproducible sin depender de la curva ISO 834
# (que en t = 0 da theta_g = 20 C y por tanto Delta_theta = 0), los goldens
# usan una curva de gas CONSTANTE inyectada por ``gas_curve``. La ecuacion
# integrada es exactamente la misma.
#
# ca(20 C) por §3.4.1.2, rama theta < 600 C:
#     ca = 425 + 0.773·20 - 1.69e-3·20^2 + 2.22e-6·20^3
#        = 425 + 15.46 - 0.676 + 0.01776 = 439.80176 J/kgK
#     ca·rho_a = 439.80176·7850 = 3 452 443.816 J/m^3K
# ---------------------------------------------------------------------------

class TestGoldenEN1993_1_2_4_2_5_1:

    def test_golden_delta_theta_primer_paso_gas_600C(self):
        """Ec. (4.25), primer paso de Euler. Am/V = 200 1/m, ksh = 1.0,
        Delta_t = 5 s, theta_a,0 = 20 C, gas constante theta_g = 600 C.

        Conveccion, Ec. (3.1):
            h_net,c = 25·(600 - 20) = 25·580 = 14 500 W/m^2
        Radiacion, Ec. (3.2) (temperaturas absolutas via +273):
            (600+273)^4 = 873^4 = 580 840 612 641 K^4
            ( 20+273)^4 = 293^4 =   7 370 050 801 K^4
            diferencia          = 573 470 561 840 K^4
            h_net,r = 0.7·5.67e-8·573 470 561 840 = 22 761.047 W/m^2
        Total:
            h_net,d = 14 500 + 22 761.047 = 37 261.047 W/m^2

        Incremento:
            Delta_theta = 1.0·(200/3 452 443.816)·37 261.047·5
                        = 5.79300e-5 · 37 261.047 · 5
                        = 2.158532 · 5
                        = 10.79266 C

        theta_a tras el primer paso = 20 + 10.79266 = 30.79266 C.
        """
        h = steel_temperature_history(
            UnprotectedSteel(Am_V_1_m=200.0, ksh=1.0),
            duration_min=1.0, dt_s=5.0, gas_curve=lambda t_min: 600.0,
        )
        assert h[0] == (0.0, 20.0)
        assert h[1][1] - 20.0 == pytest.approx(10.79266, abs=1e-4)
        assert h[1][1] == pytest.approx(30.79266, abs=1e-4)

    def test_golden_delta_theta_primer_paso_gas_400C_con_ksh(self):
        """Ec. (4.25) con factor de sombra. Am/V = 100 1/m, ksh = 0.7,
        Delta_t = 5 s, theta_a,0 = 20 C, gas constante theta_g = 400 C.

        Conveccion:
            h_net,c = 25·(400 - 20) = 25·380 = 9 500 W/m^2
        Radiacion:
            (400+273)^4 = 673^4 = 205 144 679 041 K^4
            ( 20+273)^4 = 293^4 =   7 370 050 801 K^4
            diferencia          = 197 774 628 240 K^4
            h_net,r = 0.7·5.67e-8·197 774 628 240 = 7 849.675 W/m^2
        Total:
            h_net,d = 9 500 + 7 849.675 = 17 349.675 W/m^2

        Incremento:
            Delta_theta = 0.7·(100/3 452 443.816)·17 349.675·5
                        = 0.7·2.896500e-5·17 349.675·5
                        = 0.7·0.5025330·5
                        = 0.7·2.512665 = 1.758866 C

        theta_a tras el primer paso = 21.758866 C. Ejercita ademas la
        linealidad en ksh: sin sombra (ksh = 1.0) el mismo paso daria
        2.512665 C.
        """
        h = steel_temperature_history(
            UnprotectedSteel(Am_V_1_m=100.0, ksh=0.7),
            duration_min=1.0, dt_s=5.0, gas_curve=lambda t_min: 400.0,
        )
        assert h[1][1] - 20.0 == pytest.approx(1.758866, abs=1e-5)

        sin_sombra = steel_temperature_history(
            UnprotectedSteel(Am_V_1_m=100.0, ksh=1.0),
            duration_min=1.0, dt_s=5.0, gas_curve=lambda t_min: 400.0,
        )
        assert sin_sombra[1][1] - 20.0 == pytest.approx(2.512665, abs=1e-5)

    def test_golden_calor_especifico_3_4_1_2(self):
        """EN 1993-1-2 §3.4.1.2, ca(theta) por tramos. Valores derivados a
        mano en los dos tramos que intervienen en los goldens de arriba y en
        el tramo singular:

        20 C (tramo 20 <= theta < 600):
            ca = 425 + 0.773·20 - 1.69e-3·400 + 2.22e-6·8 000
               = 425 + 15.46 - 0.676 + 0.01776 = 439.80176 J/kgK
        700 C (tramo 600 <= theta < 735):
            ca = 666 + 13002/(738 - 700) = 666 + 13002/38
               = 666 + 342.15789 = 1 008.15789 J/kgK
        800 C (tramo 735 <= theta < 900):
            ca = 545 + 17820/(800 - 731) = 545 + 17820/69
               = 545 + 258.26087 = 803.26087 J/kgK
        1000 C (tramo theta >= 900): ca = 650 J/kgK (constante)
        """
        assert specific_heat_steel(20.0) == pytest.approx(439.80176, abs=1e-5)
        assert specific_heat_steel(700.0) == pytest.approx(1008.15789, abs=1e-5)
        assert specific_heat_steel(800.0) == pytest.approx(803.26087, abs=1e-5)
        assert specific_heat_steel(1000.0) == 650.0

    def test_golden_shadow_factor_I_eq_4_26a(self):
        """EN 1993-1-2 §4.2.5.1(2), Ec. (4.26a) — perfiles en I bajo fuego
        nominal estandar:

            ksh = 0.9·[Am/V]_b / [Am/V]

        Caso derivado a mano: perfil con [Am/V] = 200 1/m y encajonado
        [Am/V]_b = 140 1/m  ->  ksh = 0.9·140/200 = 0.9·0.70 = 0.63.
        Segundo caso: 250 y 175 1/m -> ksh = 0.9·175/250 = 0.63 tambien
        (solo depende del cociente).

        LIMITACION documentada: el modulo solo implementa la Ec. (4.26a) (el
        0.9 esta cableado). La Ec. (4.26b), ksh = [Am/V]_b/[Am/V] para los
        demas casos (secciones no I, o fuego no nominal), NO es seleccionable.
        Usar esta funcion fuera de perfiles I devuelve un ksh un 10 % bajo.
        """
        assert shadow_factor_I(Am_V_1_m=200.0, Am_V_box_1_m=140.0) == \
            pytest.approx(0.63, abs=1e-12)
        assert shadow_factor_I(Am_V_1_m=250.0, Am_V_box_1_m=175.0) == \
            pytest.approx(0.63, abs=1e-12)
