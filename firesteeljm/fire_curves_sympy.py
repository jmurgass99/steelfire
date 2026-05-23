"""Curvas de fuego analiticas con sympy.

Provee expresiones simbolicas para curvas estandar de fuego:
  - ISO 834 (curva estandar): theta_g(t) = 20 + 345 * log10(8t + 1)
  - Hidrocarburica: theta_g(t) = 20 + 1080 * (1 - 0.325*exp(-0.167t) - 0.675*exp(-2.5t))
  - Externa: theta_g(t) = 660*(1 - 0.687*exp(-0.32t) - 0.313*exp(-3.8t)) + 20
  - ASTM E119 (Lie 1992): theta_g(t) = 750*(1 - exp(-3.79553*sqrt(th))) + 170.41*sqrt(th) + 20
  - RWS (Rijkswaterstaat): curva piecewise lineal de tuneles holandesa

Ventajas frente a numerico:
  - Derivada simbolica (gradiente termico instantaneo)
  - Integral simbolica (energia acumulada)
  - LaTeX para memorias

Cada funcion devuelve un ``FireCurveSpec`` con lambdified callable, latex,
derivada e integral simbolicas.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

try:
    import sympy as sp
    _HAS_SYMPY = True
except ImportError:  # pragma: no cover
    _HAS_SYMPY = False

log = logging.getLogger("firesteeljm.fire_curves_sympy")


@dataclass
class FireCurveSpec:
    """Especificacion de una curva de fuego."""
    name: str
    expression_str: str        # representacion humana
    lambda_t_min: object       # callable(t_min) -> theta_g_C
    latex: str
    derivative_callable: object  # dtheta/dt (C/min)
    integral_callable: object    # integral 0..t (C.min)


def _require_sympy() -> None:
    if not _HAS_SYMPY:
        raise ImportError("sympy no esta instalado (instalar firesteeljm[analytic])")


def iso_834() -> FireCurveSpec:
    """ISO 834 (curva estandar) - EN 1991-1-2 Anexo A.

    theta_g(t) = 20 + 345 * log10(8*t + 1)   con t en MINUTOS
    """
    _require_sympy()
    t = sp.Symbol("t", positive=True)
    expr = 20 + 345 * sp.log(8 * t + 1, 10)
    deriv = sp.diff(expr, t)
    integ = sp.integrate(expr, t)
    return FireCurveSpec(
        name="ISO 834",
        expression_str="theta_g(t) = 20 + 345*log10(8t + 1)",
        lambda_t_min=sp.lambdify(t, expr, "numpy"),
        latex=sp.latex(expr),
        derivative_callable=sp.lambdify(t, deriv, "numpy"),
        integral_callable=sp.lambdify(t, integ, "numpy"),
    )


def hydrocarbon() -> FireCurveSpec:
    """Curva hidrocarburica - EN 1991-1-2 Anexo A Eq. A.5.

    theta_g(t) = 20 + 1080*(1 - 0.325*exp(-0.167t) - 0.675*exp(-2.5t))
    """
    _require_sympy()
    t = sp.Symbol("t", positive=True)
    expr = 20 + 1080 * (
        1
        - sp.Rational(325, 1000) * sp.exp(sp.Rational(-167, 1000) * t)
        - sp.Rational(675, 1000) * sp.exp(sp.Rational(-25, 10) * t)
    )
    deriv = sp.diff(expr, t)
    integ = sp.integrate(expr, t)
    return FireCurveSpec(
        name="Hydrocarbon",
        expression_str="theta_g(t) = 20 + 1080*(1 - 0.325*exp(-0.167t) - 0.675*exp(-2.5t))",
        lambda_t_min=sp.lambdify(t, expr, "numpy"),
        latex=sp.latex(expr),
        derivative_callable=sp.lambdify(t, deriv, "numpy"),
        integral_callable=sp.lambdify(t, integ, "numpy"),
    )


def external() -> FireCurveSpec:
    """Curva externa - EN 1991-1-2 Anexo A Eq. A.4."""
    _require_sympy()
    t = sp.Symbol("t", positive=True)
    expr = 660 * (
        1
        - sp.Rational(687, 1000) * sp.exp(sp.Rational(-32, 100) * t)
        - sp.Rational(313, 1000) * sp.exp(sp.Rational(-38, 10) * t)
    ) + 20
    deriv = sp.diff(expr, t)
    integ = sp.integrate(expr, t)
    return FireCurveSpec(
        name="External",
        expression_str="theta_g(t) = 20 + 660*(1 - 0.687*exp(-0.32t) - 0.313*exp(-3.8t))",
        lambda_t_min=sp.lambdify(t, expr, "numpy"),
        latex=sp.latex(expr),
        derivative_callable=sp.lambdify(t, deriv, "numpy"),
        integral_callable=sp.lambdify(t, integ, "numpy"),
    )


def astm_e119() -> FireCurveSpec:
    """ASTM E119 (curva estandar americana) - Lie, 1992.

    theta_g(t) = 750*(1 - exp(-3.79553*sqrt(t_h))) + 170.41*sqrt(t_h) + 20
    donde t_h = t/60 (tiempo en horas).  t en MINUTOS para la interfaz.
    """
    _require_sympy()
    t = sp.Symbol("t", positive=True)
    t_h = t / 60
    expr = (
        750 * (1 - sp.exp(sp.Rational(-379553, 100000) * sp.sqrt(t_h)))
        + sp.Rational(17041, 100) * sp.sqrt(t_h)
        + 20
    )
    deriv = sp.diff(expr, t)
    integ = sp.integrate(expr, t)
    return FireCurveSpec(
        name="ASTM E119",
        expression_str=(
            "theta_g(t) = 750*(1 - exp(-3.79553*sqrt(t_h)))"
            " + 170.41*sqrt(t_h) + 20  [t_h = t/60]"
        ),
        lambda_t_min=sp.lambdify(t, expr, "numpy"),
        latex=sp.latex(expr),
        derivative_callable=sp.lambdify(t, deriv, "numpy"),
        integral_callable=sp.lambdify(t, integ, "numpy"),
    )


def rws() -> FireCurveSpec:
    """Curva RWS (Rijkswaterstaat) - curva de tuneles holandesa.

    Piecewise lineal entre puntos tabulados (t en minutos, theta en C):
      0->20, 5->1140, 10->1200, 30->1300, 60->1350,
      90->1300, 120->1200, 180->0
    """
    _require_sympy()
    t = sp.Symbol("t", positive=True)
    # Puntos de la curva: (t_min, theta_C)
    pts = [
        (0, 20), (5, 1140), (10, 1200), (30, 1300),
        (60, 1350), (90, 1300), (120, 1200), (180, 0),
    ]
    # Construir segmentos lineales: theta = theta_i + slope*(t - t_i)
    pieces = []
    for i in range(len(pts) - 1):
        t0, th0 = pts[i]
        t1, th1 = pts[i + 1]
        slope = sp.Rational(th1 - th0, t1 - t0)
        segment = th0 + slope * (t - t0)
        pieces.append((segment, t <= t1))
    # Despues de 180 min la curva se extingue
    pieces.append((sp.Integer(0), True))
    expr = sp.Piecewise(*pieces)
    deriv = sp.diff(expr, t)
    integ = sp.integrate(expr, t)
    return FireCurveSpec(
        name="RWS (Rijkswaterstaat)",
        expression_str="RWS piecewise: 0->20, 5->1140, ..., 180->0",
        lambda_t_min=sp.lambdify(t, expr, "numpy"),
        latex=sp.latex(expr),
        derivative_callable=sp.lambdify(t, deriv, "numpy"),
        integral_callable=sp.lambdify(t, integ, "numpy"),
    )


def critical_temperature_steel(R_d_over_R_fi: float) -> float:
    """Temperatura critica para perfil de acero EN 1993-1-2 §4.2.4.

    theta_a,cr = 39.19 * ln(1 / (0.9674 * mu^3.833) - 1) + 482
    mu = factor de utilizacion = R_fi/R_d (rango razonable 0.013-1.0)

    Devuelve la temperatura critica en grados Celsius.
    """
    _require_sympy()
    if not (0.013 <= R_d_over_R_fi <= 1.0):
        raise ValueError(
            f"R_d/R_fi fuera de rango [0.013, 1.0]: {R_d_over_R_fi}"
        )
    mu = sp.Rational(int(round(R_d_over_R_fi * 10000)), 10000)
    expr = 39.19 * sp.log(
        1 / (sp.Rational(9674, 10000) * mu ** sp.Rational(3833, 1000)) - 1
    ) + 482
    return float(expr.evalf())


__all__ = [
    "FireCurveSpec",
    "iso_834",
    "hydrocarbon",
    "external",
    "astm_e119",
    "rws",
    "critical_temperature_steel",
]
