"""Barra maciza de acero: solver 2D por diferencias finitas frente al modelo de masa concentrada de EN 1993-1-2.

Barra 60×60 mm expuesta por las cuatro caras: Am/V = perímetro/área = 4/0,06 = 66,7 m⁻¹.
La ec. 4.25 supone temperatura uniforme en la sección; el solver 2D resuelve la conducción
con k = 45 W/mK constante. Para una sección pequeña los dos deben acercarse; la diferencia
que queda procede de las hipótesis distintas (k constante y malla frente a masa concentrada
con c_a(θ)). Es un contraste de consistencia entre dos motores del paquete, no una
validación contra ensayo.

Ejecutar:  python examples/thermal_2d_vs_lumped_en1993_1_2_massive_bar.py
"""
from steelfire import ThermalSection, solve_thermal
from steelfire.en_steel_temperature import UnprotectedSteel, steel_temperature_history

SIDE = 0.06
AM_V = 4.0 / SIDE


def main() -> None:
    res = solve_thermal(ThermalSection(b=SIDE, h=SIDE, n_x=12, n_y=12), t_total=1800.0)
    lumped = steel_temperature_history(UnprotectedSteel(Am_V_1_m=AM_V, ksh=1.0), duration_min=30.0, dt_s=5.0)
    print(f"Barra {1000 * SIDE:.0f}×{1000 * SIDE:.0f} mm, Am/V = {AM_V:.1f} m⁻¹, ISO 834\n")
    print(f"{'t [min]':>7} {'2D media':>9} {'2D máx':>7} {'masa concentrada':>17} {'dif. media':>11}")
    for t_min in (5, 10, 15, 20, 25, 30):
        i = min(range(len(res.times)), key=lambda k: abs(res.times[k] - 60.0 * t_min))
        T_l = next(th for tm, th in lumped if tm >= t_min - 1e-9)
        print(f"{t_min:7d} {res.T_mean_history[i]:9.0f} {res.T_max_history[i]:7.0f} {T_l:17.0f} {res.T_mean_history[i] - T_l:+11.0f}")


if __name__ == "__main__":
    main()
