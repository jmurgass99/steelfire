"""Diferencias finitas 2D: refinamiento de malla, paso de tiempo por CFL y qué pasa si se viola.

Sección de 200×200 mm con las cuatro caras expuestas 10 minutos a ISO 834. Para 5, 10 y 20
divisiones por lado se calcula el Δt máximo estable (Δt ≤ ½·Δx²Δy²/(Δx²+Δy²)/α, con α la
difusividad para c_a = 425 J/kgK) y la temperatura máxima y media al final. Un Δt mayor que
el límite lanza ValueError en vez de devolver un campo inestable.

Ejecutar:  python examples/thermal_2d_mesh_refinement_and_cfl_time_step.py
"""
from steelfire import ThermalSection, solve_thermal
from steelfire.thermal_fea import K_STEEL, RHO_STEEL

B = H = 0.20
T_TOTAL = 600.0


def dt_max(n: int) -> float:
    dx = dy = B / n
    alpha = K_STEEL / (RHO_STEEL * 425.0)
    return 0.5 * (dx ** 2 * dy ** 2) / (dx ** 2 + dy ** 2) / alpha


def main() -> None:
    means = {}
    print(f"{'n':>3} {'Δx [mm]':>8} {'Δt_max [s]':>11} {'pasos':>7} {'T_max 10 min':>13} {'T_media':>8}")
    for n in (5, 10, 20):
        res = solve_thermal(ThermalSection(b=B, h=H, n_x=n, n_y=n), t_total=T_TOTAL)
        means[n] = res.T_mean_history[-1]
        print(f"{n:3d} {1000 * B / n:8.0f} {dt_max(n):11.3f} {len(res.times) * 10:7d} {res.T_max_history[-1]:13.0f} {res.T_mean_history[-1]:8.0f}")
    try:
        solve_thermal(ThermalSection(b=B, h=H, n_x=10, n_y=10), t_total=T_TOTAL, dt=5.0 * dt_max(10))
    except ValueError as exc:
        print(f"\nΔt = 5·Δt_max → ValueError: {exc}")
    print(f"\nDiferencia de la media respecto a la malla de 20: n = 5 → {means[5] / means[20] - 1:+.1%}, "
          f"n = 10 → {means[10] / means[20] - 1:+.1%}. La máxima (celda de esquina) sí depende del tamaño de celda.")


if __name__ == "__main__":
    main()
