"""Curva paramétrica de EN 1991-1-2 Anexo A: incendio controlado por ventilación frente a controlado por combustible, y la temperatura de un perfil sin proteger.

Recinto con cerramiento de b = 1160 J/(m²·s^0,5·K) (Γ = (O/b)²/(0,04/1160)²), crecimiento medio
(t_lim = 20 min). Con O = 0,04 m^½ y q_t,d = 150 MJ/m² el fuego lo controla la ventilación
(t_max = 0,2·10⁻³·q_t,d/O = 0,75 h > t_lim); con O = 0,10 m^½ lo controla el combustible
(0,30 h < t_lim) y el calentamiento usa Γ_lim (Ec. A.8). Se tabula Θ_g, se rehace a mano el pico y
un punto de enfriamiento 10 min después del pico (Ec. A.11 con t*_max = (0,2·10⁻³·q_t,d/O)·Γ, Ec. A.12) y se calcula la
temperatura de un perfil sin proteger con Am/V = 200 m⁻¹ frente a ISO 834. La API REST no sirve
todavía esta curva.

Ejecutar:  python examples/parametric_fire_annex_a_ventilation_vs_fuel_controlled_steel_temperature.py
"""
import math

from steelfire.en_steel_temperature import (
    ParametricFireInput,
    UnprotectedSteel,
    parametric_fire_curve,
    parametric_fire_gas,
    steel_temperature_history,
)

Q, B, T_LIM = 150.0, 1160.0, 20.0
TIMES = [0, 10, 20, 30, 45, 60, 75, 90, 120]


def heating(t_star: float) -> float:
    return 20 + 1325 * (1 - 0.324 * math.exp(-0.2 * t_star) - 0.204 * math.exp(-1.7 * t_star) - 0.472 * math.exp(-19 * t_star))


def main() -> None:
    print(f"q_t,d = {Q:.0f} MJ/m², b = {B:.0f}, t_lim = {T_LIM:.0f} min\n")
    print(f"  {'t [min]':>7} " + " ".join(f"{t:6d}" for t in TIMES))
    for O in (0.04, 0.10):
        row = [parametric_fire_gas(t, O_m_half=O, b_J_m2s05K=B, q_t_d_MJ_m2=Q, t_lim_min=T_LIM) for t in TIMES]
        print(f"  O = {O:.2f} " + " ".join(f"{v:6.0f}" for v in row))

    print("\nA mano:")
    for O in (0.04, 0.10):
        gamma = (O / 0.04) ** 2 / (B / 1160) ** 2
        t_vent = 0.2e-3 * Q / O
        fuel = t_vent < T_LIM / 60
        t_max = max(t_vent, T_LIM / 60)
        g_heat = ((0.1e-3 * Q / (T_LIM / 60)) / 0.04) ** 2 / (B / 1160) ** 2 if fuel else gamma
        th_max = heating(g_heat * t_max)
        ts_max = gamma * t_vent
        x = (T_LIM / 60) * gamma / ts_max if fuel else 1.0
        t = t_max * 60 + 10.0   # 10 min después del pico
        slope = 625 if ts_max <= 0.5 else (250 * (3 - ts_max) if ts_max < 2 else 250)
        th60 = max(th_max - slope * (gamma * t / 60 - ts_max * x), 20.0)
        pkg = parametric_fire_gas(t, O_m_half=O, b_J_m2s05K=B, q_t_d_MJ_m2=Q, t_lim_min=T_LIM)
        print(f"  O = {O:.2f}: {'combustible' if fuel else 'ventilación'}, Γ = {gamma:.2f}, t_max = {t_max * 60:.0f} min, "
              f"Θ_max = {th_max:.0f} °C, t*_max = {ts_max:.3f}; Θ_g({t:.0f} min) = {th60:.0f} °C (paquete {pkg:.0f})")
        before = parametric_fire_gas(t_max * 60 - 0.01, O_m_half=O, q_t_d_MJ_m2=Q)
        after = parametric_fire_gas(t_max * 60 + 0.01, O_m_half=O, q_t_d_MJ_m2=Q)
        print(f"    continuidad en t_max: {before:.1f} → {after:.1f} °C")

    sec = UnprotectedSteel(Am_V_1_m=200.0)
    print("\nPerfil sin proteger, Am/V = 200 m⁻¹ (θ_a máxima y cuándo):")
    iso = steel_temperature_history(sec, duration_min=120.0)
    print(f"  ISO 834:            θ_a(120 min) = {iso[-1][1]:.0f} °C")
    for O in (0.04, 0.10):
        h = steel_temperature_history(sec, duration_min=120.0, gas_curve=parametric_fire_curve(
            ParametricFireInput(O_m_half=O, b_J_m2s05K=B, q_t_d_MJ_m2=Q, t_lim_min=T_LIM)))
        pk = max(h, key=lambda p: p[1])
        print(f"  paramétrica O = {O:.2f}: θ_a,max = {pk[1]:.0f} °C a los {pk[0]:.0f} min; a 120 min {h[-1][1]:.0f} °C")


if __name__ == "__main__":
    main()
