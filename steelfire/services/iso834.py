"""Servicio ISO 834 — temperatura del gas y evaluación simplificada de acero."""
from __future__ import annotations

from dataclasses import dataclass

from ..exceptions import ConfigurationError


@dataclass
class ISO834Input:
    """Entrada para evaluación ISO 834.

    Atributos:
        time_minutes: tiempo de exposición (min).
        section_factor_amv: factor de masividad Am/V (m^-1).
        is_protected: True si la sección está protegida.
    """
    time_minutes: float
    section_factor_amv: float = 150.0
    is_protected: bool = False
    use_en1993_exact_c_a: bool = False

    def validate(self) -> None:
        if self.time_minutes < 0:
            raise ConfigurationError("time_minutes debe ser >= 0")
        if self.section_factor_amv <= 0:
            raise ConfigurationError("section_factor_amv debe ser > 0")


@dataclass
class ISO834Result:
    """Resultado tipado de evaluación ISO 834."""
    time_minutes: float
    gas_temperature_C: float
    steel_temperature_C: float
    yield_reduction_factor_ky: float
    status: str


def evaluate_iso834(inp: ISO834Input) -> ISO834Result:
    """Ejecuta la evaluación ISO 834 (gas + acero + ky).

    Args:
        inp: entrada validada.

    Returns:
        Resultado serializable.

    Raises:
        ConfigurationError: parámetros inválidos.
    """
    inp.validate()
    from ..iso834 import FireEvaluator
    fe = FireEvaluator(
        time_minutes=inp.time_minutes,
        section_factor_amv=inp.section_factor_amv,
        is_protected=inp.is_protected,
        use_en1993_exact_c_a=inp.use_en1993_exact_c_a,
    )
    rep = fe.evaluation_report()
    return ISO834Result(
        time_minutes=rep["time_minutes"],
        gas_temperature_C=rep["gas_temperature_C"],
        steel_temperature_C=rep["steel_temperature_C"],
        yield_reduction_factor_ky=rep["yield_reduction_factor_ky"],
        status=rep["status"],
    )
