"""
Factores de retención térmica multi-código.

EU/SG:  EN 1993-1-2 Tabla 3.1 (ya en `thermal_iter.py`)
US/CO:  AISC 360-16/22 Apéndice 4, Tabla A-4.2.1 (k_E, k_p, k_y en nodos de °F;
        valores tomados del Eurocódigo)
AU:     enrutado a la tabla EN sin ajustes (AS 4100 Tabla 12.1 NO está
        implementada; ver tests/test_retention_multi.py)
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

#: AISC 360-16/22 Tabla A-4.2.1, nodos 68/200/400/600/750/800/1000/1200/1400/
#: 1600/1800/2000/2200 °F convertidos a °C. Valores idénticos a EN 1993-1-2
#: Tabla 3.1 en los nodos de °C más próximos, redondeados a dos decimales.
_AISC_T = np.array(
    [20, 93, 204, 316, 399, 427, 538, 649, 760, 871, 982, 1093, 1204],
    dtype=float,
)
_AISC_kE = np.array(
    [1.00, 1.00, 0.90, 0.78, 0.70, 0.67, 0.49, 0.22, 0.11, 0.07, 0.05, 0.02, 0.00],
)
_AISC_kp = np.array(
    [1.00, 1.00, 0.807, 0.613, 0.420, 0.360, 0.180, 0.075, 0.050, 0.0375, 0.0250, 0.0125, 0.00],
)
_AISC_ky = np.array(
    [1.00, 1.00, 1.00, 1.00, 1.00, 0.94, 0.66, 0.35, 0.16, 0.07, 0.04, 0.02, 0.00],
)
_AISC_TABLES = {"E": _AISC_kE, "Fy": _AISC_ky, "kp": _AISC_kp}


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
        # AISC 360-16/22 Apéndice 4, Tabla A-4.2.1 "Properties of Steel at
        # Elevated Temperatures": columnas k_E = E(T)/E, k_p = F_p(T)/F_y y
        # k_y = F_y(T)/F_y en nodos de 200 °F. Son los valores de EN 1993-1-2
        # Tabla 3.1 (AISC los adopta del Eurocódigo) leídos en esos nodos.
        # Hasta 2026-10-31 esta rama usaba una "aproximación cuadrática" sin
        # fuente que daba k_E = 0 a 400 °C (la tabla da 0.70) y afirmaba que
        # AISC no define k_p, cuando la Tabla A-4.2.1 lo tabula.
        return float(np.interp(T_celsius, _AISC_T, _AISC_TABLES[quantity]))
    raise ValueError(f"código '{code}' no soportado")


__all__ = ["retention_factor"]
