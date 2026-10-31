"""Jerarquía de excepciones de SteelFire.

Todas heredan adicionalmente de ``ValueError`` para preservar la
compatibilidad hacia atrás con código que captura ``ValueError`` desde
``solve_thermal`` u otros validadores previos.
"""
from __future__ import annotations


class FireSteelError(ValueError):
    """Excepción base del paquete SteelFire."""


class ConfigurationError(FireSteelError):
    """Configuración inválida del usuario (dimensiones, mallas, dt CFL...)."""


class ConvergenceError(FireSteelError):
    """Fallo de convergencia del solver térmico."""


class DependencyError(FireSteelError):
    """Falta una dependencia opcional (por ejemplo FastAPI para la REST API)."""


__all__ = [
    "FireSteelError",
    "ConfigurationError",
    "ConvergenceError",
    "DependencyError",
]
