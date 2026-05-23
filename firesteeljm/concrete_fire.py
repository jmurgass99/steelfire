"""
concrete_fire.py - EN 1992-1-2 Reinforced concrete fire design.

Implements:
- Isotherm 500 method (Annex B.1, EN 1992-1-2)
- Zone method (Annex B.2)
- Concrete strength reduction kc(T) (Table 3.1, siliceous aggregate)
- Reinforcing steel reduction ks(T) (Table 3.2a)
- Minimum cover for R-rating (Table 5.2a)
"""
import math
from typing import Literal


def _iso834_gas_T(t_min: float) -> float:
    """ISO 834 fire curve: Theta_g = 20 + 345*log10(8t+1)."""
    return 20.0 + 345.0 * math.log10(8.0 * t_min + 1.0)


def concrete_kc_T(T: float) -> float:
    """
    Reduction factor kc(T) for concrete compressive strength fc.
    EN 1992-1-2 Table 3.1, siliceous aggregate (NC).

    :param T: temperature in degrees Celsius.
    :return: kc(T) in [0, 1].
    """
    # Table 3.1 anchors (siliceous): 20->1.0, 100->1.0, 200->0.95, 300->0.85,
    # 400->0.75, 500->0.60, 600->0.45, 700->0.30, 800->0.15, 900->0.08,
    # 1000->0.04, 1100->0.01 -> 1200->0.
    table = [
        (20.0, 1.00), (100.0, 1.00), (200.0, 0.95), (300.0, 0.85),
        (400.0, 0.75), (500.0, 0.60), (600.0, 0.45), (700.0, 0.30),
        (800.0, 0.15), (900.0, 0.08), (1000.0, 0.04), (1100.0, 0.01),
        (1200.0, 0.00),
    ]
    if T <= table[0][0]:
        return table[0][1]
    if T >= table[-1][0]:
        return 0.0
    for (T1, k1), (T2, k2) in zip(table[:-1], table[1:]):
        if T1 <= T <= T2:
            return k1 + (k2 - k1) * (T - T1) / (T2 - T1)
    return 0.0


def rebar_ks_T(T: float, ductility: Literal["hot_rolled", "cold_worked"] = "hot_rolled") -> float:
    """
    Reduction factor ks(T) for reinforcing steel yield strength fy.
    EN 1992-1-2 Table 3.2a (tension reinforcement, class N).

    :param T: temperature in degrees Celsius.
    :param ductility: 'hot_rolled' or 'cold_worked'.
    :return: ks(T) in [0, 1].
    """
    if ductility == "hot_rolled":
        # Table 3.2a hot rolled (eps_s,fi >= 2%): 20->1.0, 100->1.0, 200->1.0,
        # 300->1.0, 400->1.0, 500->0.78, 600->0.47, 700->0.23, 800->0.11,
        # 900->0.06, 1000->0.04, 1100->0.02, 1200->0.
        table = [
            (20.0, 1.00), (100.0, 1.00), (200.0, 1.00), (300.0, 1.00),
            (400.0, 1.00), (500.0, 0.78), (600.0, 0.47), (700.0, 0.23),
            (800.0, 0.11), (900.0, 0.06), (1000.0, 0.04), (1100.0, 0.02),
            (1200.0, 0.00),
        ]
    else:
        # Table 3.2a cold worked: 20->1.0, 100->1.0, 200->1.0, 300->1.0,
        # 400->0.94, 500->0.67, 600->0.40, 700->0.12, 800->0.11, 900->0.08,
        # 1000->0.05, 1100->0.03, 1200->0.
        table = [
            (20.0, 1.00), (100.0, 1.00), (200.0, 1.00), (300.0, 1.00),
            (400.0, 0.94), (500.0, 0.67), (600.0, 0.40), (700.0, 0.12),
            (800.0, 0.11), (900.0, 0.08), (1000.0, 0.05), (1100.0, 0.03),
            (1200.0, 0.00),
        ]
    if T <= table[0][0]:
        return table[0][1]
    if T >= table[-1][0]:
        return 0.0
    for (T1, k1), (T2, k2) in zip(table[:-1], table[1:]):
        if T1 <= T <= T2:
            return k1 + (k2 - k1) * (T - T1) / (T2 - T1)
    return 0.0


def _approx_temperature_at_depth(x_mm: float, t_min: float, T_surface: float) -> float:
    """
    Simplified temperature profile inside concrete under nominal fire.
    Implements a semi-empirical model that incorporates:
    - Temperature-dependent diffusivity (representing loss of conductivity at high T).
    - Evaporation plateau of free water at 100 °C (delay in temperature rise).
    """
    T0 = 20.0
    t_s = max(t_min, 0.0) * 60.0
    if t_s <= 0:
        return T0
    x_m = x_mm / 1000.0
    
    # 1. Temperature-dependent diffusivity correction:
    # Thermal conductivity of siliceous concrete decreases by up to 50% at 800°C.
    # We use an effective average diffusivity that decreases as surface temperature increases.
    alpha_base = 0.417e-6  # m^2/s at 20°C
    # As T_surface increases, average diffusivity decreases due to microcracking and water loss.
    T_factor = max(0.0, (T_surface - T0) / 1000.0)
    alpha_eff = alpha_base * (1.0 - 0.25 * T_factor)
    
    arg = x_m / (2.0 * math.sqrt(alpha_eff * t_s))
    T_base = T0 + (T_surface - T0) * math.erfc(arg)
    
    # 2. Free water evaporation plateau (100°C plateau) emulation:
    # The latent heat of water evaporation creates a temperature shelf at 100°C.
    # This is prominent in the outer 100 mm where moisture escapes.
    if T_base > 100.0 and x_mm <= 100.0:
        # We compress the temperature near 100°C to emulate the plateau.
        # Below 100°C there is no plateau. Above 100°C, the temperature rise is delayed.
        dT = T_base - 100.0
        # The delay is stronger closer to the surface where water is evaporating,
        # but also deeper where heat takes longer to vaporize water.
        # Apply a smooth sigmoid-like plateau:
        plateau_delay = 40.0 * math.exp(-x_mm / 75.0)  # max 40°C delay near the heated face
        T_corr = 100.0 + dT * (1.0 - plateau_delay / (dT + 50.0))
        return max(100.0, min(T_corr, T_surface))
        
    return max(T0, min(T_base, T_surface))


def isotherm_method_500(b: float, h: float, t_exposure_min: float,
                        fire_curve: str = "ISO834") -> dict:
    """
    Isotherm 500 method (EN 1992-1-2 Annex B.1).

    The cross-section is reduced by discarding concrete with T > 500 deg C,
    yielding an effective reduced section (b_fi, h_fi) where T <= 500 deg C.
    Assumes 4-sided fire exposure.

    :param b: section width in mm.
    :param h: section height in mm.
    :param t_exposure_min: fire duration in minutes.
    :param fire_curve: nominal fire curve identifier (ISO834 supported).
    :return: dict with a500_mm (damaged depth per face), b_fi, h_fi, T_surface.
    """
    if fire_curve.upper() != "ISO834":
        raise ValueError("Only ISO834 supported in this implementation.")
    Ts = _iso834_gas_T(t_exposure_min)

    # Find depth x at which T(x) = 500 deg C (the 500 deg C isotherm).
    if Ts <= 500.0 or t_exposure_min <= 0:
        a500 = 0.0
    else:
        lo, hi = 0.0, 500.0  # search 0..500 mm
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            T_mid = _approx_temperature_at_depth(mid, t_exposure_min, Ts)
            if T_mid > 500.0:
                lo = mid
            else:
                hi = mid
        a500 = 0.5 * (lo + hi)

    b_fi = max(0.0, b - 2.0 * a500)
    h_fi = max(0.0, h - 2.0 * a500)
    return {
        "fire_curve": fire_curve,
        "t_min": t_exposure_min,
        "T_surface_C": round(Ts, 1),
        "a500_mm": round(a500, 2),
        "b_fi_mm": round(b_fi, 2),
        "h_fi_mm": round(h_fi, 2),
    }


def zone_method(b: float, h: float, t_exposure: float, fc: float,
                num_zones: int = 10) -> dict:
    """
    Zone method (EN 1992-1-2 Annex B.2).

    The half-width is divided into n parallel zones; each zone temperature
    is evaluated at its mid-depth, kc(T) is computed, and a mean reduction
    factor kc_m is obtained. The effective width is reduced by az:
        az = w * (1 - kc_m / kc(T_M))
    where w = b/2 and T_M is the temperature at the centerline.

    :param b: section width in mm.
    :param h: section height in mm.
    :param t_exposure: fire exposure in minutes.
    :param fc: characteristic concrete strength at 20 deg C [MPa].
    :param num_zones: number of zones (>=3).
    :return: dict with az_mm, b_fi_mm, h_fi_mm, kc_m, axial capacity estimate
             at ambient and fire conditions [kN].
    """
    if num_zones < 3:
        raise ValueError("num_zones must be >= 3")
    Ts = _iso834_gas_T(max(t_exposure, 0.0))
    w = b / 2.0  # half-width [mm]
    dz = w / num_zones
    # Sample at mid-depth of each zone (zone 1 nearest the fire-exposed face)
    kcs = []
    for i in range(num_zones):
        x_mid = (i + 0.5) * dz  # mm from heated face
        T_i = _approx_temperature_at_depth(x_mid, t_exposure, Ts) if t_exposure > 0 else 20.0
        kcs.append(concrete_kc_T(T_i))
    # Skip outer zone (i=0) per Annex B.2 procedure (most damaged neglected)
    n_eff = num_zones - 1
    kc_m = (1.0 - 0.2 / n_eff) * sum(kcs[1:]) / n_eff if n_eff > 0 else 0.0
    # Center temperature for kc(T_M)
    T_M = _approx_temperature_at_depth(w, t_exposure, Ts) if t_exposure > 0 else 20.0
    kc_TM = concrete_kc_T(T_M)
    if kc_TM <= 1e-9:
        az = w
    else:
        az = w * max(0.0, 1.0 - kc_m / kc_TM)
    b_fi = max(0.0, b - 2.0 * az)
    h_fi = max(0.0, h - 2.0 * az)
    # Capacity proxy: N = fc * Area (ambient) vs kc(T_M) * fc * A_fi
    N_amb = fc * b * h / 1000.0  # kN
    N_fire = kc_TM * fc * b_fi * h_fi / 1000.0  # kN
    return {
        "az_mm": round(az, 2),
        "b_fi_mm": round(b_fi, 2),
        "h_fi_mm": round(h_fi, 2),
        "kc_m": round(kc_m, 4),
        "kc_TM": round(kc_TM, 4),
        "N_ambient_kN": round(N_amb, 1),
        "N_fire_kN": round(N_fire, 1),
    }


def cover_for_R_rating(b: float, R_min: int,
                       member_type: Literal["column", "beam", "slab"] = "column") -> dict:
    """
    Minimum axis distance 'a' to longitudinal reinforcement for given R rating.
    EN 1992-1-2 Table 5.2a (columns, mu_fi = 0.7) and Table 5.5 (beams) /
    Table 5.8 (slabs) - simplified.

    :param b: minimum section dimension [mm].
    :param R_min: required fire rating in minutes (30, 60, 90, 120, 180, 240).
    :param member_type: 'column', 'beam', or 'slab'.
    :return: dict with required b_min, axis distance a [mm].
    """
    R = int(R_min)
    if member_type == "column":
        # EN 1992-1-2 Table 5.2a (mu_fi = 0.7): columns exposed on > 1 side.
        # (b_min [mm], a [mm]) per R rating.
        table = {
            30:  (200, 25),
            60:  (250, 46),
            90:  (350, 53),
            120: (350, 57),
            180: (450, 70),
            240: (450, 75),
        }
    elif member_type == "beam":
        # EN 1992-1-2 Table 5.5 simply supported beams (option a).
        table = {
            30:  (80,  25),
            60:  (120, 40),
            90:  (150, 55),
            120: (200, 65),
            180: (240, 80),
            240: (280, 90),
        }
    elif member_type == "slab":
        # EN 1992-1-2 Table 5.8 one-way solid slabs.
        table = {
            30:  (60,  10),
            60:  (80,  20),
            90:  (100, 30),
            120: (120, 40),
            180: (150, 55),
            240: (175, 65),
        }
    else:
        raise ValueError(f"Unknown member_type: {member_type}")

    if R not in table:
        # Pick the next higher rating available
        higher = [r for r in table if r >= R]
        if not higher:
            raise ValueError(f"R{R} exceeds tabulated values.")
        R = min(higher)
    b_min_req, a_req = table[R]
    return {
        "R_min": R,
        "member_type": member_type,
        "b_min_required_mm": b_min_req,
        "axis_distance_a_mm": a_req,
        "b_provided_mm": b,
        "b_ok": b >= b_min_req,
    }
