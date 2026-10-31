"""Servicio de análisis térmico 2D para secciones de acero expuestas a fuego.

Envuelve :func:`steelfire.thermal_fea.solve_thermal` con tipos estables
(dataclasses) pensados para integraciones (REST API, CLI, otros paquetes).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from ..exceptions import ConfigurationError, ConvergenceError


@dataclass
class ThermalAnalysisInput:
    """Entrada tipada para el solver térmico.

    Atributos:
        b: ancho de la sección (m).
        h: peralte de la sección (m).
        n_x: divisiones de la malla en x.
        n_y: divisiones de la malla en y.
        exposed_faces: (bottom, right, top, left).
        protection_thickness: espesor de protección (m, 0 = sin protección).
        protection_k: conductividad de la protección (W/m·K).
        t_total: duración total de la exposición (s).
        dt: paso de tiempo (s) o None para autocalcular por CFL.
        t_save_every: cada cuántos pasos guardar el campo.
    """
    b: float
    h: float
    n_x: int = 20
    n_y: int = 20
    exposed_faces: tuple[bool, bool, bool, bool] = (True, True, True, True)
    protection_thickness: float = 0.0
    protection_k: float = 0.12
    t_total: float = 1800.0
    dt: float | None = None
    t_save_every: int = 10

    def validate(self) -> None:
        """Valida los parámetros de entrada.

        Raises:
            ConfigurationError: si las dimensiones o mallas son inválidas.
        """
        if self.b <= 0 or self.h <= 0:
            raise ConfigurationError("b y h deben ser positivos")
        if self.n_x < 2 or self.n_y < 2:
            raise ConfigurationError("n_x y n_y deben ser >= 2")
        if self.t_total <= 0:
            raise ConfigurationError("t_total debe ser positivo")
        if self.protection_thickness < 0:
            raise ConfigurationError("protection_thickness debe ser >= 0")
        if len(self.exposed_faces) != 4:
            raise ConfigurationError("exposed_faces debe tener 4 booleanos")


@dataclass
class ThermalAnalysisResult:
    """Resultado tipado del análisis térmico."""
    times: list[float]
    T_max_history: list[float]
    T_mean_history: list[float]
    T_final_max: float
    T_final_mean: float
    n_steps_saved: int


def run_thermal_analysis(inp: ThermalAnalysisInput) -> ThermalAnalysisResult:
    """Ejecuta el análisis térmico.

    Args:
        inp: configuración del análisis.

    Returns:
        Resultado serializable con series temporales.

    Raises:
        ConfigurationError: configuración inválida.
        ConvergenceError: el solver no pudo converger.
    """
    inp.validate()
    # Lazy import para evitar pagar el coste de numpy en quien no usa el servicio.
    from ..thermal_fea import ThermalSection, solve_thermal

    section = ThermalSection(
        b=inp.b, h=inp.h, n_x=inp.n_x, n_y=inp.n_y,
        exposed_faces=inp.exposed_faces,
        protection_thickness=inp.protection_thickness,
        protection_k=inp.protection_k,
    )
    try:
        res = solve_thermal(
            section,
            t_total=inp.t_total,
            dt=inp.dt,
            t_save_every=inp.t_save_every,
        )
    except ValueError as exc:
        # Re-clasifica las violaciones CFL como ConfigurationError.
        if "CFL" in str(exc):
            raise ConfigurationError(str(exc)) from exc
        raise ConvergenceError(str(exc)) from exc

    return ThermalAnalysisResult(
        times=[float(t) for t in res.times],
        T_max_history=[float(t) for t in res.T_max_history],
        T_mean_history=[float(t) for t in res.T_mean_history],
        T_final_max=float(res.T_max_history[-1]),
        T_final_mean=float(res.T_mean_history[-1]),
        n_steps_saved=len(res.times),
    )
