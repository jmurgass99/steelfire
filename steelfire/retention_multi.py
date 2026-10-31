"""
Factores de retención térmica multi-código.

EU/SG:  EN 1993-1-2 Tabla 3.1 (ya en `thermal_iter.py`)
US/CO:  AISC 360-22 Apéndice 4 / ASCE-29 (correlación cuadrática)
AU:     AS 4100 Tabla 12.1 (basado en EN con ajustes)
"""
from __future__ import annotations

from typing import Literal

import numpy as np


_EN_T = np.array(
    [20, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200],
    dtype=float,
)
_EN_kE = np.array(
    [1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.31, 0.13, 0.09, 0.0675, 0.045, 0.0225, 0.0],
)
_EN_ky = np.array(
    [1.0, 1.0, 1.0, 1.0, 1.0, 0.78, 0.47, 0.23, 0.11, 0.06, 0.04, 0.02, 0.0],
)
#: k_p(T) — límite de proporcionalidad (f_p,θ = k_p·f_y), EN 1993-1-2 Tabla 3.1.
#: Se importa de `thermal_iter` para no duplicar la tabla normativa: una copia
#: divergiría en silencio en cuanto alguien corrigiera solo una de las dos.
from .thermal_iter import _K_P as _EN_kp  # noqa: E402

#: Magnitudes soportadas -> tabla EN. Es un mapa EXPLÍCITO a propósito: la
#: versión anterior hacía `_EN_kE if quantity == "E" else _EN_ky`, así que
#: CUALQUIER otro valor caía en k_y sin avisar. `retention_factor(400, "kp")`
#: devolvía 1.000 en vez de 0.420 —un factor 2.38 de sobreestimación del límite
#: de proporcionalidad— y hasta un `"e"` en minúscula daba k_y en vez de k_E.
#: Un factor de seguridad de material no puede salir de un `else` por defecto.
_EN_TABLES = {"E": _EN_kE, "Fy": _EN_ky, "kp": _EN_kp}


def retention_factor(T_celsius: float,
                       quantity: Literal["E", "Fy", "kp"],
                       code: Literal["EU", "SG", "US", "CO", "AU"] = "EU"
                       ) -> float:
    """k_E(T), k_y(T) o k_p(T) según el código.

    Raises
    ------
    ValueError
        Si ``quantity`` o ``code`` no están soportados. NUNCA se degrada a una
        magnitud por defecto: devolver k_y cuando se pidió k_p es un error
        silencioso del lado inseguro.
    """
    code = code.upper()
    if quantity not in _EN_TABLES:
        raise ValueError(
            f"magnitud '{quantity}' no soportada; use uno de "
            f"{sorted(_EN_TABLES)} (distingue mayúsculas)"
        )
    if code in ("EU", "SG", "AU"):
        # AS 4100 sigue EN 1993-1-2 (con pequeñas diferencias en T<400°C)
        return float(np.interp(T_celsius, _EN_T, _EN_TABLES[quantity]))
    if code in ("US", "CO"):
        # AISC 360-22 Apéndice 4 — aproximación cuadrática
        if quantity == "kp":
            raise ValueError(
                "AISC 360-22 Apéndice 4 no define un k_p equivalente al de "
                "EN 1993-1-2 Tabla 3.1; no se sustituye por otra magnitud."
            )
        T = max(T_celsius, 20)
        if quantity == "E":
            # k_E ≈ 1 - 6e-4·T - 6e-6·T² (valida 20-700°C)
            ke = 1.0 - 6e-4 * (T - 20) - 6e-6 * (T - 20) ** 2
            return float(max(min(ke, 1.0), 0.0))
        # k_y ≈ 1 hasta 400, luego decae lineal hasta 0 a 800°C
        if T <= 400:
            return 1.0
        if T <= 800:
            return max(1.0 - (T - 400) / 400, 0.0)
        return 0.0
    raise ValueError(f"código '{code}' no soportado")


__all__ = ["retention_factor"]
