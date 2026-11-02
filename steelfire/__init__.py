"""
SteelFire - Structural Fire Design for Steel EN 1993-1-2
"""

__version__ = "1.2.1"

from .thermal_fea import (
    ThermalSection,
    ThermalResult,
    solve_thermal,
    c_steel,
)
from .exceptions import (
    FireSteelError,
    ConfigurationError,
    ConvergenceError,
    DependencyError,
)

__all__ = [
    "ThermalSection",
    "ThermalResult",
    "solve_thermal",
    "c_steel",
    "FireSteelError",
    "ConfigurationError",
    "ConvergenceError",
    "DependencyError",
]

try:  # optional: requires sympy
    from .fire_curves_sympy import (  # noqa: F401
        FireCurveSpec,
        iso_834,
        hydrocarbon,
        external,
        astm_e119,
        rws,
        critical_temperature_steel,
    )
    __all__ += [
        "FireCurveSpec",
        "iso_834",
        "hydrocarbon",
        "external",
        "astm_e119",
        "rws",
        "critical_temperature_steel",
    ]
except ImportError:  # pragma: no cover
    pass
