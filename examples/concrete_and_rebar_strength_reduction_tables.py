"""Reducción de resistencia del hormigón k_c(θ) y de la armadura k_s(θ) con la temperatura (EN 1992-1-2 Tablas 3.1 y 3.2a).

Hormigón de áridos silíceos y acero de armar laminado en caliente o estirado en frío,
de 20 a 1 200 °C. El k_s del acero laminado en caliente coincide con el k_y,θ del acero
estructural de EN 1993-1-2: la misma tabla en dos normas.

Ejecutar:  python examples/concrete_and_rebar_strength_reduction_tables.py
"""
from steelfire.concrete_fire import concrete_kc_T, rebar_ks_T
from steelfire.thermal_iter import k_y


def main() -> None:
    print(f"{'θ [°C]':>7} {'k_c hormigón':>13} {'k_s laminado':>13} {'k_s estirado':>13} {'k_y,θ EN 1993-1-2':>18}")
    for T in (20, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200):
        print(f"{T:7d} {concrete_kc_T(T):13.2f} {rebar_ks_T(T, 'hot_rolled'):13.2f} {rebar_ks_T(T, 'cold_worked'):13.2f} {k_y(T):18.2f}")
    print(f"\nInterpolación: k_c(450) = {concrete_kc_T(450.0):.3f}, k_s(650, estirado) = {rebar_ks_T(650.0, 'cold_worked'):.3f}")


if __name__ == "__main__":
    main()
