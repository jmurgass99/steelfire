# -*- coding: utf-8 -*-
"""Modelo de calculo simple de temperatura del acero (EN 1993-1-2 §4.2.5).

Evolucion incremental de la temperatura de una seccion de acero bajo fuego, por
el factor de seccion Am/V (1/m):
  - §4.2.5.1 elemento sin proteger (con efecto sombra ksh).
  - §4.2.5.2 elemento protegido (material de proteccion dp, lambda_p, cp, rho_p).

Calor especifico del acero ca(θ) segun §3.4.1.2 (piecewise). Curva de gas por
defecto ISO 834.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, List, Tuple

_RHO_A = 7850.0      # kg/m3
_SIGMA = 5.67e-8     # W/m2K4
_ALPHA_C = 25.0      # W/m2K (fuego nominal estandar)
_EMISS = 0.7         # emisividad resultante (εm·εf)


def specific_heat_steel(theta_C: float) -> float:
    """Calor especifico del acero ca(θ) en J/kgK (EN 1993-1-2 §3.4.1.2)."""
    t = theta_C
    if t < 600.0:
        return 425.0 + 0.773 * t - 1.69e-3 * t ** 2 + 2.22e-6 * t ** 3
    if t < 735.0:
        return 666.0 + 13002.0 / (738.0 - t)
    if t < 900.0:
        return 545.0 + 17820.0 / (t - 731.0)
    return 650.0


def iso834_gas(t_min: float) -> float:
    """Curva de gas ISO 834 (°C)."""
    return 20.0 + 345.0 * math.log10(8.0 * t_min + 1.0)


@dataclass(frozen=True)
class UnprotectedSteel:
    Am_V_1_m: float          # factor de seccion Am/V (1/m)
    ksh: float = 1.0         # factor de sombra (I-sections < 1)


@dataclass(frozen=True)
class ProtectedSteel:
    Am_V_1_m: float          # Ap/V del material de proteccion
    dp_m: float              # espesor de la proteccion
    lambda_p: float          # conductividad W/mK
    cp: float                # calor especifico J/kgK
    rho_p: float             # densidad kg/m3


def steel_temperature_history(
    section,
    duration_min: float = 60.0,
    dt_s: float = 5.0,
    gas_curve: Callable[[float], float] = iso834_gas,
) -> List[Tuple[float, float]]:
    """Historia (t_min, θ_a) de la temperatura del acero.

    ``section`` es UnprotectedSteel o ProtectedSteel. Integra por Euler con paso
    dt_s. Devuelve lista de (tiempo_min, temperatura_°C).
    """
    theta_a = 20.0
    t = 0.0
    out = [(0.0, theta_a)]
    n = int(duration_min * 60.0 / dt_s)
    protected = isinstance(section, ProtectedSteel)
    for _ in range(n):
        t_min = t / 60.0
        theta_g = gas_curve(t_min)
        theta_g_next = gas_curve((t + dt_s) / 60.0)
        ca = specific_heat_steel(theta_a)
        if not protected:
            # §4.2.5.1: hnet = conveccion + radiacion.
            hnet_c = _ALPHA_C * (theta_g - theta_a)
            hnet_r = _EMISS * _SIGMA * ((theta_g + 273.0) ** 4 - (theta_a + 273.0) ** 4)
            dtheta = section.ksh * (section.Am_V_1_m / (ca * _RHO_A)) * (hnet_c + hnet_r) * dt_s
        else:
            # §4.2.5.2: con phi del material de proteccion.
            phi = (section.cp * section.rho_p / (ca * _RHO_A)) * section.dp_m * section.Am_V_1_m
            term = (section.lambda_p * section.Am_V_1_m / (section.dp_m * ca * _RHO_A))
            dtheta = term * (theta_g - theta_a) / (1.0 + phi / 3.0) * dt_s
            dtheta -= (math.exp(phi / 10.0) - 1.0) * (theta_g_next - theta_g)
            dtheta = max(dtheta, 0.0)  # no enfriamiento mientras el gas sube
        theta_a += dtheta
        t += dt_s
        out.append((t / 60.0, theta_a))
    return out


def steel_temperature_at(section, duration_min: float, dt_s: float = 5.0,
                         gas_curve: Callable[[float], float] = iso834_gas) -> float:
    """Temperatura del acero al cabo de ``duration_min`` (°C)."""
    return steel_temperature_history(section, duration_min, dt_s, gas_curve)[-1][1]


def shadow_factor_I(Am_V_1_m: float, Am_V_box_1_m: float) -> float:
    """Efecto sombra para perfiles I (§4.2.5.1): ksh = 0.9·(Am/V)_box/(Am/V)."""
    return 0.9 * Am_V_box_1_m / Am_V_1_m


__all__ = [
    "specific_heat_steel", "iso834_gas", "UnprotectedSteel", "ProtectedSteel",
    "steel_temperature_history", "steel_temperature_at", "shadow_factor_I",
]
