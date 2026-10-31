"""
Iteración térmica acoplada acero — degradación de propiedades vs T(t)
(gotcha #6 + EN 1993-1-2 §3.2).

A diferencia de los Time-History térmicos de SAP (mal documentados),
este módulo expone una curva de retención y un generador de
`Property Modifiers` por paso de tiempo que el wrapper OAPI reasigna
masivamente a las secciones afectadas por el fuego.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np


# Tabla EN 1993-1-2 §3.2.1 Tabla 3.1 — factores de retención del acero al carbono
# k_y(T): límite de fluencia efectivo (f_y,θ = k_y·f_y)
# k_p(T): límite de proporcionalidad (f_p,θ = k_p·f_y)
# k_E(T): pendiente del tramo elástico / módulo (E_a,θ = k_E·E_a)
_RETENTION_T = np.array(
    [20, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200],
    dtype=float,
)
_K_E = np.array(
    [1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.31, 0.13, 0.09, 0.0675, 0.045, 0.0225, 0.0],
    dtype=float,
)
_K_Y = np.array(
    [1.0, 1.0, 1.0, 1.0, 1.0, 0.78, 0.47, 0.23, 0.11, 0.06, 0.04, 0.02, 0.0],
    dtype=float,
)
_K_P = np.array(
    [1.0, 1.0, 0.807, 0.613, 0.420, 0.360, 0.180, 0.075, 0.050, 0.0375,
     0.0250, 0.0125, 0.0],
    dtype=float,
)


def k_E(T_celsius: float) -> float:
    """Factor de retención del módulo de elasticidad (k_E,θ, Tabla 3.1)."""
    return float(np.interp(T_celsius, _RETENTION_T, _K_E))


def k_y(T_celsius: float) -> float:
    """Factor de retención del límite de fluencia (k_y,θ, Tabla 3.1)."""
    return float(np.interp(T_celsius, _RETENTION_T, _K_Y))


def k_p(T_celsius: float) -> float:
    """Factor de retención del límite de proporcionalidad (k_p,θ, Tabla 3.1).

    f_p,θ = k_p,θ · f_y. Marca el fin del tramo lineal-elástico de la relación
    tensión-deformación del acero a temperatura elevada (EN 1993-1-2 §3.2.1):
    por debajo de f_p,θ la respuesta es elástica con pendiente E_a,θ = k_E,θ·E_a.
    Para 20°C ≤ θa ≤ 400°C, k_y,θ se mantiene en 1.0 mientras k_p,θ ya degrada
    (200°C→0.807, 300°C→0.613, 400°C→0.420): el límite proporcional cae antes de
    que lo haga la resistencia de fluencia efectiva.

    Nota: no confundir con k_0.2p,θ (tensión de prueba al 0.2% para secciones
    Clase 4, EN 1993-1-2 Anexo E / Tabla E.1), que es una columna distinta
    (p.ej. 0.53 a 500°C, 0.30 a 600°C).
    """
    return float(np.interp(T_celsius, _RETENTION_T, _K_P))


@dataclass(frozen=True)
class ThermalStep:
    """Paso de tiempo de la iteración térmica."""
    t_min: float
    T_celsius: float
    k_E: float
    k_y: float
    property_modifiers: dict[str, float] = field(default_factory=dict)


def thermal_history(time_minutes: Sequence[float],
                     temperature_provider: Callable[[float], float],
                     sections: Sequence[str] | None = None
                     ) -> list[ThermalStep]:
    """Genera la historia de degradación.

    Args:
        time_minutes: malla temporal del análisis (minutos desde t=0).
        temperature_provider: callable(t_min) -> T(°C). Suele ser ISO 834
            (`steelfire.iso834.iso834_temperature`) o equivalente.
        sections: nombres de secciones a las que aplicar el modificador
            (sólo informativo en el dict ``property_modifiers``).

    Returns:
        Lista de ``ThermalStep`` con el factor k_E y k_y ya calculados
        — el wrapper OAPI los inyecta como Property Modifiers para
        Area/Moment of Inertia y para la resistencia de diseño.
    """
    steps: list[ThermalStep] = []
    for t in time_minutes:
        T = float(temperature_provider(t))
        ke = k_E(T)
        ky = k_y(T)
        mods = {"E_factor": ke, "Fy_factor": ky}
        if sections:
            mods["sections"] = list(sections)  # type: ignore[assignment]
        steps.append(ThermalStep(t_min=t, T_celsius=T, k_E=ke, k_y=ky,
                                 property_modifiers=mods))
    return steps


def critical_time_to_failure(steps: Sequence[ThermalStep],
                              utilization_at_t0: float,
                              k_y_critical: float | None = None) -> float:
    """Tiempo crítico (min) en el que ``k_y(T(t)) < utilization_at_t0``.

    Si nunca falla en la historia, devuelve ``inf``.
    """
    if not 0 < utilization_at_t0 <= 1.0:
        raise ValueError("utilization_at_t0 ∈ (0, 1]")
    target = k_y_critical if k_y_critical is not None else utilization_at_t0
    for s in steps:
        if s.k_y < target:
            return s.t_min
    return float("inf")


__all__ = [
    "k_E", "k_y", "k_p",
    "ThermalStep", "thermal_history",
    "critical_time_to_failure",
]
