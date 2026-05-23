"""
Catálogo de protecciones pasivas para acero estructural — UL/EN.

Tipos:
    intumescent      — pintura intumescente (acrílica/epóxica)
    spray_mortar     — mortero proyectado base cementicia / yeso
    board            — placa cartón-yeso / cemento / silicato calcio
    concrete         — recubrimiento de hormigón
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FireProtection:
    code: str
    type: str
    lambda_p_W_per_mK: float       # conductividad térmica
    rho_p_kg_m3: float             # densidad
    c_p_J_per_kgK: float           # calor específico
    typical_thickness_mm: tuple[float, float]   # min, max
    cost_USD_per_m2: float
    rating_minutes: int            # R-rating típico


CATALOG: list[FireProtection] = [
    FireProtection("UL 60-INT-acrylic",  "intumescent",  0.10, 1300,  900,
                    (0.6, 3.0),   45.0, 60),
    FireProtection("UL 120-INT-epoxy",   "intumescent",  0.08, 1300,  900,
                    (1.2, 6.0),   85.0, 120),
    FireProtection("UL 60-spray-mortar", "spray_mortar", 0.12,  300, 1100,
                    (15.0, 35.0), 35.0, 60),
    FireProtection("EN 90-board-cem",    "board",        0.20,  900, 1000,
                    (12.5, 25.0), 55.0, 90),
    FireProtection("EN 120-board-silic", "board",        0.17,  450, 1100,
                    (20.0, 40.0), 70.0, 120),
    FireProtection("Concrete-R180",      "concrete",     1.40, 2300, 1000,
                    (30.0, 60.0), 25.0, 180),
]


def recommend(target_rating_min: int,
                budget_USD_per_m2: float | None = None
                ) -> list[FireProtection]:
    out = [p for p in CATALOG if p.rating_minutes >= target_rating_min]
    if budget_USD_per_m2 is not None:
        out = [p for p in out if p.cost_USD_per_m2 <= budget_USD_per_m2]
    return sorted(out, key=lambda p: p.cost_USD_per_m2)


def lookup(code: str) -> FireProtection | None:
    for p in CATALOG:
        if p.code == code:
            return p
    return None


__all__ = ["FireProtection", "CATALOG", "recommend", "lookup"]
