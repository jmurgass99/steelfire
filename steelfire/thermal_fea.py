"""FEA térmica 2D simplificada para secciones de acero expuestas a fuego.

Resuelve la ecuación de difusión de calor por diferencias finitas explícitas
sobre una malla cartesiana cubriendo la sección transversal.

    ρ·c · ∂T/∂t = k · (∂²T/∂x² + ∂²T/∂y²) + q_boundary

donde q_boundary incluye convección + radiación según EC3 Annex A.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np


# Propiedades térmicas del acero (EC3 §3.4)
RHO_STEEL = 7850.0        # kg/m³
K_STEEL = 45.0            # W/(m·K) — conservador, varía con T
EMISSIVITY = 0.7          # emisividad de superficie
ALPHA_CONV = 25.0         # coef. convección W/(m²·K)
SIGMA_SB = 5.67e-8        # constante Stefan-Boltzmann


def c_steel(T_C: float) -> float:
    """Calor específico del acero c(T) [J/(kg·K)] — EC3 §3.4.1.2."""
    T = T_C
    if T < 600:
        return 425.0 + 7.73e-1 * T - 1.69e-3 * T**2 + 2.22e-6 * T**3
    if T < 735:
        return 666.0 + 13002.0 / (738.0 - T)
    if T < 900:
        return 545.0 + 17820.0 / (T - 731.0)
    return 650.0


@dataclass
class ThermalSection:
    """Sección rectangular de acero (con o sin protección). Las cuatro caras
    pueden tener o no exposición al fuego.

    Atributos:
        b: ancho m (eje x)
        h: peralte m (eje y)
        n_x: divisiones malla en x
        n_y: divisiones malla en y
        exposed_faces: tuple de booleanos (bottom, right, top, left) — True = expuesto
        protection_thickness: m de material protector (0 = sin protección)
        protection_k: conductividad protección W/(m·K) (típico vermiculita 0.12)
    """
    b: float
    h: float
    n_x: int = 20
    n_y: int = 20
    exposed_faces: tuple[bool, bool, bool, bool] = (True, True, True, True)
    protection_thickness: float = 0.0
    protection_k: float = 0.12


@dataclass
class ThermalResult:
    times: np.ndarray              # s
    T_field: list[np.ndarray]      # lista de mallas (n_y, n_x) en °C
    T_max_history: np.ndarray      # máximo de T sobre toda la sección, por tiempo
    T_mean_history: np.ndarray     # media de T sobre la sección, por tiempo


def _gas_temperature_iso834(t_s: float) -> float:
    """Curva ISO 834 (incendio celulósico)."""
    t_min = t_s / 60.0
    return 20.0 + 345.0 * math.log10(8.0 * t_min + 1.0)


def _boundary_flux(T_steel_C: float, T_gas_C: float,
                    h_protection: float, k_protection: float) -> float:
    """Flujo de calor entrante por unidad de área de superficie expuesta.

    Combina convección + radiación (cuerpo gris):
        q = α·(Tg - Ts) + ε·σ·((Tg+273)^4 - (Ts+273)^4)

    Si hay protección, se reduce el flujo por la conductividad efectiva.
    """
    Tg_K = T_gas_C + 273.15
    Ts_K = T_steel_C + 273.15
    q_conv = ALPHA_CONV * (T_gas_C - T_steel_C)
    q_rad = EMISSIVITY * SIGMA_SB * (Tg_K**4 - Ts_K**4)
    q = q_conv + q_rad
    if h_protection > 0:
        # Reducción simplificada: resistencia térmica de la capa
        R = h_protection / max(k_protection, 1e-6)
        q = q / (1.0 + R * ALPHA_CONV)
    return q


def solve_thermal(
    section: ThermalSection,
    t_total: float = 1800.0,     # 30 min default
    dt: float | None = None,
    t_save_every: int = 10,
    gas_temperature_fn: Callable[[float], float] = _gas_temperature_iso834,
) -> ThermalResult:
    """Integra la ecuación de calor 2D por diferencias finitas explícitas.

    Args:
        section: definición de la sección.
        t_total: duración total de exposición (s).
        dt: paso de tiempo (s). Si None se calcula para estabilidad (CFL).
        t_save_every: guardar el campo cada N steps.
        gas_temperature_fn: función T_gas(t_s) en °C; por defecto ISO 834.

    Returns:
        ThermalResult con historial de campos T(x,y) y series de T_max, T_mean.
    """
    n_x, n_y = section.n_x, section.n_y
    dx = section.b / n_x
    dy = section.h / n_y
    # Estabilidad CFL para difusión explícita:
    # dt <= (1 / 2α) · (dx²·dy²) / (dx² + dy²)
    alpha_diff_max = K_STEEL / (RHO_STEEL * 425.0)  # diffusividad mínima ~ c bajo
    dt_max = 0.5 * (dx**2 * dy**2) / (dx**2 + dy**2) / alpha_diff_max
    if dt is None:
        dt = 0.4 * dt_max  # margen de seguridad
    elif dt > dt_max:
        raise ValueError(
            f"dt={dt:.4f}s viola CFL (dt_max={dt_max:.4f}s). Reduce dt o aumenta resolución."
        )

    T = np.full((n_y, n_x), 20.0)  # condición inicial: 20 °C uniforme
    n_steps = int(t_total / dt) + 1

    times: list[float] = [0.0]
    T_fields: list[np.ndarray] = [T.copy()]
    T_max: list[float] = [float(T.max())]
    T_mean: list[float] = [float(T.mean())]

    for step in range(1, n_steps):
        t = step * dt
        Tg = gas_temperature_fn(t)
        c = c_steel(float(T.mean()))
        alpha = K_STEEL / (RHO_STEEL * c)
        # Conducción en TODA la malla, con gradiente nulo en los bordes (nodos
        # fantasma por replicación). Hasta 2026-10-31 el laplaciano solo se
        # aplicaba al interior y las celdas de borde se actualizaban únicamente
        # con el flujo del gas: nunca cedían calor hacia dentro, de modo que su
        # temperatura y la media de la sección crecían al refinar la malla
        # (200x200 mm, 10 min: media 132/208/324 °C con 5/10/20 divisiones) y
        # una barra de 60 mm calentaba casi el doble que el modelo de masa
        # concentrada de EN 1993-1-2 §4.2.5.1 con el mismo flujo.
        Tp = np.pad(T, 1, mode="edge")
        lap = ((Tp[1:-1, 2:] - 2.0 * T + Tp[1:-1, :-2]) / dx**2
               + (Tp[2:, 1:-1] - 2.0 * T + Tp[:-2, 1:-1]) / dy**2)
        T_new = T + alpha * dt * lap
        # Flujo del gas en las caras expuestas, absorbido por la celda de borde
        # (energía q·dt por unidad de área de cara, capacidad ρ·c·Δn por área).
        bot, right, top, left = section.exposed_faces
        if bot:
            q = np.array([_boundary_flux(float(T[0, i]), Tg,
                                           section.protection_thickness,
                                           section.protection_k)
                          for i in range(n_x)])
            T_new[0, :] += dt * q / (RHO_STEEL * c * dy)
        if top:
            q = np.array([_boundary_flux(float(T[-1, i]), Tg,
                                           section.protection_thickness,
                                           section.protection_k)
                          for i in range(n_x)])
            T_new[-1, :] += dt * q / (RHO_STEEL * c * dy)
        if left:
            q = np.array([_boundary_flux(float(T[j, 0]), Tg,
                                           section.protection_thickness,
                                           section.protection_k)
                          for j in range(n_y)])
            T_new[:, 0] += dt * q / (RHO_STEEL * c * dx)
        if right:
            q = np.array([_boundary_flux(float(T[j, -1]), Tg,
                                           section.protection_thickness,
                                           section.protection_k)
                          for j in range(n_y)])
            T_new[:, -1] += dt * q / (RHO_STEEL * c * dx)
        T = T_new
        if step % t_save_every == 0:
            times.append(t)
            T_fields.append(T.copy())
            T_max.append(float(T.max()))
            T_mean.append(float(T.mean()))

    return ThermalResult(
        times=np.array(times),
        T_field=T_fields,
        T_max_history=np.array(T_max),
        T_mean_history=np.array(T_mean),
    )
