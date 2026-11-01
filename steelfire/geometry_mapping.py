"""Mapeo semántico -> celdas térmicas 2D (``ThermalSectionMapping``):
``region_to_cells`` para alas y alma de perfiles en I bajo fuego.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ThermalSectionMapping:
    """Mapeo entre regiones semánticas del perfil (bottom_flange, web, top_flange)
    y las celdas térmicas discretas ``(x_mm, y_mm, dx_mm, dy_mm, am_v_m_inv)``.
    """

    region_to_cells: Dict[str, List[int]] = field(default_factory=dict)
    cells: List[Tuple[float, float, float, float, float]] = field(default_factory=list)


def build_isection_thermal_mesh(
    h_mm: float = 300.0,
    b_mm: float = 150.0,
    tf_mm: float = 10.7,
    tw_mm: float = 7.1,
    divisions_per_region: int = 5,
) -> ThermalSectionMapping:
    """Subdivide las tres regiones de un perfil IPE/HEA en ``divisions_per_region``
    celdas térmicas cada una, preservando ``region_to_cells``.
    """
    n_div = max(1, int(divisions_per_region))
    region_to_cells: Dict[str, List[int]] = {
        "bottom_flange": [],
        "web": [],
        "top_flange": [],
    }
    cells: List[Tuple[float, float, float, float, float]] = []

    half_h = 0.5 * h_mm
    half_b = 0.5 * b_mm
    amv_flange = 2000.0 / max(tf_mm, 1.0)
    amv_web = 2000.0 / max(tw_mm, 1.0)

    # Bottom flange
    dx_f = b_mm / float(n_div)
    for k in range(n_div):
        xc = -half_b + (k + 0.5) * dx_f
        yc = -half_h + 0.5 * tf_mm
        region_to_cells["bottom_flange"].append(len(cells))
        cells.append((round(xc, 4), round(yc, 4), round(dx_f, 4), float(tf_mm), round(amv_flange, 2)))

    # Web
    h_web = max(h_mm - 2.0 * tf_mm, 10.0)
    dy_w = h_web / float(n_div)
    for k in range(n_div):
        xc = 0.0
        yc = -0.5 * h_web + (k + 0.5) * dy_w
        region_to_cells["web"].append(len(cells))
        cells.append((xc, round(yc, 4), float(tw_mm), round(dy_w, 4), round(amv_web, 2)))

    # Top flange
    for k in range(n_div):
        xc = -half_b + (k + 0.5) * dx_f
        yc = half_h - 0.5 * tf_mm
        region_to_cells["top_flange"].append(len(cells))
        cells.append((round(xc, 4), round(yc, 4), round(dx_f, 4), float(tf_mm), round(amv_flange, 2)))

    return ThermalSectionMapping(region_to_cells=region_to_cells, cells=cells)
