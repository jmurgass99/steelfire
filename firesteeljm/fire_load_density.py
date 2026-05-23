"""
Carga de fuego (fire load density) por uso (idea #15).

EN 1991-1-2 Tabla E.4 y NFPA 557 — densidad característica q_f,k [MJ/m2]
para distintos usos (vivienda, oficina, etc.). Soporta:
- EN 1991-1-2 (EU)
- NFPA 557 (USA)
- AS 1170.4 (AU)
- SS-EN 1991-1-2 (SG)
- NSR-10 (CO) [aproxima a EN]

Calcula:
- q_f,d valor de cálculo = q_f,k * m * δq1 * δq2 * δn
- Resistencia equivalente t_eq con kc según Eurocode parametric.
"""
from dataclasses import dataclass


# Valores característicos típicos [MJ/m2] de varios usos
_FIRE_LOADS = {
    "EU": {
        "vivienda": 780.0,
        "oficina": 420.0,
        "hospital": 230.0,
        "hotel": 310.0,
        "biblioteca": 1500.0,
        "comercial": 600.0,
        "industria": 1180.0,
    },
    "USA": {
        "vivienda": 790.0,
        "oficina": 415.0,
        "hospital": 240.0,
        "hotel": 305.0,
        "biblioteca": 1450.0,
        "comercial": 580.0,
        "industria": 1100.0,
    },
    "AU": {
        "vivienda": 800.0, "oficina": 400.0, "hospital": 250.0, "hotel": 320.0,
        "biblioteca": 1480.0, "comercial": 590.0, "industria": 1200.0,
    },
    "SG": {  # similar EU
        "vivienda": 780.0, "oficina": 420.0, "hospital": 230.0, "hotel": 310.0,
        "biblioteca": 1500.0, "comercial": 600.0, "industria": 1180.0,
    },
    "NSR": {
        "vivienda": 800.0, "oficina": 430.0, "hospital": 250.0, "hotel": 320.0,
        "biblioteca": 1480.0, "comercial": 620.0, "industria": 1200.0,
    },
}


@dataclass(frozen=True)
class FireLoadInput:
    occupancy: str
    floor_area_m2: float = 100.0
    m_factor: float = 0.8        # combustion factor
    delta_q1: float = 1.2        # riesgo activación área
    delta_q2: float = 1.0        # riesgo activación uso
    delta_n: float = 1.0         # protección activa
    code: str = "EU"


@dataclass(frozen=True)
class FireLoadResult:
    qfk_MJ_m2: float
    qfd_MJ_m2: float
    total_energy_GJ: float
    code: str


def fire_load_density(inp: FireLoadInput) -> FireLoadResult:
    c = inp.code.upper()
    if c in ("EU", "EUROCODE"):
        table = _FIRE_LOADS["EU"]
    elif c in ("USA", "NFPA"):
        table = _FIRE_LOADS["USA"]
    elif c in ("AS", "AU"):
        table = _FIRE_LOADS["AU"]
    elif c in ("SG", "SS"):
        table = _FIRE_LOADS["SG"]
    elif c in ("NSR", "CO"):
        table = _FIRE_LOADS["NSR"]
    else:
        raise ValueError(f"Código desconocido: {inp.code}")
    if inp.occupancy not in table:
        raise ValueError(f"Uso desconocido: {inp.occupancy}")
    qfk = table[inp.occupancy]
    qfd = qfk * inp.m_factor * inp.delta_q1 * inp.delta_q2 * inp.delta_n
    total_GJ = qfd * inp.floor_area_m2 / 1000.0
    return FireLoadResult(qfk_MJ_m2=qfk, qfd_MJ_m2=qfd,
                          total_energy_GJ=total_GJ, code=inp.code)


def equivalent_fire_duration_min(qfd_MJ_m2: float, kc: float = 0.07) -> float:
    """t_eq = kc * q_fd  (kc en min·m2/MJ)."""
    if qfd_MJ_m2 < 0:
        raise ValueError("qfd >= 0")
    return kc * qfd_MJ_m2
