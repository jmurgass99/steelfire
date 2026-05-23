"""
Memoria de calculo handcalcs -- temperatura critica + tiempo de colapso
bajo curva ISO 834 (EN 1993-1-2 S4.2.4).

Produce LaTeX/Markdown paso-a-paso del calculo:

    mu_0 = E_fi / R_fi,20C                  (nivel de carga)
    theta_cr = 39.19 * ln(1/(0.9674*mu_0^3.833) - 1) + 482   (temperatura critica)
    t_cr : theta_a(t_cr) = theta_cr          (tiempo de colapso via ISO 834)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, List, Tuple

try:
    from handcalcs.decorator import handcalc
    _HAS_HANDCALCS = True
except ImportError:  # pragma: no cover
    _HAS_HANDCALCS = False

    def handcalc(*args, **kwargs):
        def deco(f):
            return f
        return deco


# ---------------------------------------------------------------------------
# Input / Output dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CriticalTempMemoInput:
    """Datos de entrada para la memoria de temperatura critica.

    Args:
        member_type: tipo de elemento ('beam', 'column', 'brace', etc.)
        load_ratio: mu_0 = E_fi / R_fi,20C (rango valido ~0.013 .. 1.0)
        section_label: etiqueta de la seccion (ej. 'IPE 300')
        Am_V: factor de seccion Am/V [1/m] (para calculo de t_cr)
        ksh: factor de sombra (1.0 para conservador)
        protected: True si la seccion esta protegida
        dp_m: espesor proteccion [m] (solo si protected=True)
        lambda_p: conductividad proteccion [W/mK]
        cp: calor especifico proteccion [J/kgK]
        rho_p: densidad proteccion [kg/m3]
    """
    member_type: str = "beam"
    load_ratio: float = 0.5
    section_label: str = "IPE 300"
    Am_V: float = 200.0
    ksh: float = 1.0
    protected: bool = False
    dp_m: float = 0.0
    lambda_p: float = 0.0
    cp: float = 0.0
    rho_p: float = 0.0

    def validate(self) -> None:
        if not (0.013 <= self.load_ratio <= 1.0):
            raise ValueError(
                f"load_ratio fuera de rango [0.013, 1.0]: {self.load_ratio}"
            )
        if self.Am_V <= 0:
            raise ValueError(f"Am_V debe ser > 0 (recibido {self.Am_V})")


@dataclass(frozen=True)
class CriticalTempMemoResult:
    """Resultado de la memoria de temperatura critica."""
    mu_0: float
    theta_cr_C: float
    t_cr_min: float | None
    pass_check: bool
    latex: str
    markdown: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "mu_0": self.mu_0,
            "theta_cr_C": self.theta_cr_C,
            "t_cr_min": self.t_cr_min,
            "pass_check": self.pass_check,
        }


# ---------------------------------------------------------------------------
# Core calculations
# ---------------------------------------------------------------------------

def _critical_temperature(mu_0: float) -> float:
    """Temperatura critica EN 1993-1-2 S4.2.4, Eq. 4.22.

        theta_cr = 39.19 * ln(1 / (0.9674 * mu_0^3.833) - 1) + 482

    Valida para 0.013 <= mu_0 <= 1.0.
    Devuelve grados Celsius.
    """
    argument = 1.0 / (0.9674 * mu_0 ** 3.833) - 1.0
    if argument <= 0:
        raise ValueError(
            f"mu_0={mu_0} produce argumento no-positivo para ln: {argument}"
        )
    return 39.19 * math.log(argument) + 482.0


def _collapse_time_iso834(
    theta_cr: float,
    Am_V: float,
    ksh: float = 1.0,
    protected: bool = False,
    dp_m: float = 0.0,
    lambda_p: float = 0.0,
    cp: float = 0.0,
    rho_p: float = 0.0,
    dt_s: float = 5.0,
    max_duration_min: float = 240.0,
) -> float | None:
    """Tiempo de colapso t_cr tal que theta_a(t_cr) = theta_cr bajo ISO 834.

    Usa la historia de temperatura del acero de en_steel_temperature.
    Devuelve minutos o None si no se alcanza theta_cr en max_duration_min.
    """
    from ..en_steel_temperature import (
        UnprotectedSteel,
        ProtectedSteel,
        steel_temperature_history,
    )

    if protected:
        section = ProtectedSteel(
            Am_V_1_m=Am_V,
            dp_m=dp_m,
            lambda_p=lambda_p,
            cp=cp,
            rho_p=rho_p,
        )
    else:
        section = UnprotectedSteel(Am_V_1_m=Am_V, ksh=ksh)

    history: List[Tuple[float, float]] = steel_temperature_history(
        section, duration_min=max_duration_min, dt_s=dt_s,
    )

    # Buscar primer cruce: theta_a >= theta_cr
    for i in range(1, len(history)):
        t_prev, theta_prev = history[i - 1]
        t_curr, theta_curr = history[i]
        if theta_curr >= theta_cr:
            # Interpolar linealmente el instante exacto
            if theta_curr == theta_prev:
                return t_curr
            frac = (theta_cr - theta_prev) / (theta_curr - theta_prev)
            return t_prev + frac * (t_curr - t_prev)

    return None  # no se alcanza en el rango simulado


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render_critical_temp_memo(
    member_type: str = "beam",
    load_ratio: float = 0.5,
    section: str = "IPE 300",
    Am_V: float = 200.0,
    ksh: float = 1.0,
    protected: bool = False,
    dp_m: float = 0.0,
    lambda_p: float = 0.0,
    cp: float = 0.0,
    rho_p: float = 0.0,
    fire_resistance_min: float | None = None,
) -> str:
    """Genera memoria Markdown de temperatura critica + tiempo de colapso.

    Args:
        member_type: tipo de elemento (beam, column, brace, ...)
        load_ratio: mu_0 = E_fi / R_fi,20C
        section: etiqueta de la seccion
        Am_V: factor de seccion Am/V [1/m]
        ksh: factor de sombra
        protected: si la seccion esta protegida
        dp_m, lambda_p, cp, rho_p: propiedades proteccion
        fire_resistance_min: resistencia requerida (min), para check pass/fail

    Returns:
        string con la memoria completa en Markdown.
    """
    data = CriticalTempMemoInput(
        member_type=member_type,
        load_ratio=load_ratio,
        section_label=section,
        Am_V=Am_V,
        ksh=ksh,
        protected=protected,
        dp_m=dp_m,
        lambda_p=lambda_p,
        cp=cp,
        rho_p=rho_p,
    )
    data.validate()
    result = render_critical_temp_memo_full(data, fire_resistance_min)
    return result.markdown


def render_critical_temp_memo_full(
    data: CriticalTempMemoInput,
    fire_resistance_min: float | None = None,
) -> CriticalTempMemoResult:
    """Genera memoria completa con LaTeX, Markdown y resultado numerico.

    Args:
        data: datos de entrada completos.
        fire_resistance_min: resistencia requerida para verificacion pass/fail.

    Returns:
        CriticalTempMemoResult con todos los campos.
    """
    data.validate()
    mu_0 = data.load_ratio

    # --- Temperatura critica ---
    theta_cr = _critical_temperature(mu_0)

    # --- Tiempo de colapso ---
    t_cr = _collapse_time_iso834(
        theta_cr=theta_cr,
        Am_V=data.Am_V,
        ksh=data.ksh,
        protected=data.protected,
        dp_m=data.dp_m,
        lambda_p=data.lambda_p,
        cp=data.cp,
        rho_p=data.rho_p,
    )

    # --- Pass / Fail ---
    if fire_resistance_min is not None and t_cr is not None:
        pass_check = t_cr >= fire_resistance_min
    else:
        pass_check = True  # sin requisito, no se puede fallar

    # --- LaTeX ---
    latex = (
        r"\mu_0 = \frac{E_{fi}}{R_{fi,20°C}} = "
        rf"{mu_0:.4f}" r"\\"
        r"\theta_{{cr}} = 39.19 \cdot \ln\!\left("
        r"\frac{1}{0.9674 \cdot \mu_0^{3.833}} - 1\right) + 482 = "
        rf"{theta_cr:.1f}\;°C" r"\\"
    )
    if t_cr is not None:
        latex += (
            r"\text{Curva ISO 834: } \theta_a(t_{cr}) = \theta_{cr}"
            rf" \Rightarrow t_{{cr}} = {t_cr:.1f}\;\text{{min}}"
        )

    # --- Markdown ---
    prot_label = "protegido" if data.protected else "sin proteger"
    md_parts = [
        "# Memoria -- Temperatura critica del acero (EN 1993-1-2)\n\n",
        f"**Elemento:** {data.member_type}\n",
        f"**Seccion:** {data.section_label} ({prot_label})\n",
        f"**Factor de seccion:** Am/V = {data.Am_V:.0f} m^-1\n",
    ]
    if not data.protected:
        md_parts.append(f"**Factor de sombra:** ksh = {data.ksh:.2f}\n")
    else:
        md_parts.append(
            f"**Proteccion:** dp = {data.dp_m*1000:.1f} mm, "
            f"lambda_p = {data.lambda_p:.2f} W/mK, "
            f"c_p = {data.cp:.0f} J/kgK, "
            f"rho_p = {data.rho_p:.0f} kg/m3\n"
        )
    md_parts.append("\n## Nivel de carga\n\n")
    md_parts.append(
        f"$$\\mu_0 = \\frac{{E_{{fi}}}}{{R_{{fi,20°C}}}} = {mu_0:.4f}$$\n\n"
    )
    md_parts.append("## Temperatura critica\n\n")
    md_parts.append(
        f"$$\\theta_{{cr}} = 39.19 \\cdot \\ln\\!\\left("
        f"\\frac{{1}}{{0.9674 \\cdot \\mu_0^{{3.833}}}} - 1\\right) + 482"
        f" = {theta_cr:.1f}\\;°C$$\n\n"
    )
    md_parts.append("## Tiempo de colapso (ISO 834)\n\n")
    if t_cr is not None:
        md_parts.append(
            f"$$\\theta_a(t_{{cr}}) = \\theta_{{cr}} \\Rightarrow "
            f"t_{{cr}} = {t_cr:.1f}\\;\\text{{min}}$$\n\n"
        )
    else:
        md_parts.append(
            "No se alcanza la temperatura critica en el rango simulado.\n\n"
        )

    # Check
    if fire_resistance_min is not None:
        verdict = "PASS" if pass_check else "FAIL"
        md_parts.append(
            f"## Verificacion\n\n"
            f"Resistencia requerida: R = {fire_resistance_min:.0f} min\n"
        )
        if t_cr is not None:
            md_parts.append(
                f"Tiempo de colapso: t_cr = {t_cr:.1f} min\n"
                f"t_cr {'>='}  R -> **{verdict}**\n"
                if pass_check else
                f"Tiempo de colapso: t_cr = {t_cr:.1f} min\n"
                f"t_cr < R -> **{verdict}**\n"
            )

    markdown = "".join(md_parts)

    return CriticalTempMemoResult(
        mu_0=mu_0,
        theta_cr_C=theta_cr,
        t_cr_min=t_cr,
        pass_check=pass_check,
        latex=latex,
        markdown=markdown,
    )


__all__ = [
    "CriticalTempMemoInput",
    "CriticalTempMemoResult",
    "render_critical_temp_memo",
    "render_critical_temp_memo_full",
]
