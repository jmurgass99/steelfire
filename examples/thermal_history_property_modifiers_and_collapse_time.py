"""Historia térmica para un análisis acoplado: modificadores de propiedad por paso y tiempo de colapso.

Un modelo de barras (SAP2000, ETABS) no degrada el acero con la temperatura: hay que
reasignar E y f_y en cada paso. `thermal_history` recibe la temperatura del acero en
cada instante (aquí la de un perfil sin proteger con Am/V = 150 m⁻¹ bajo ISO 834, ec.
4.25) y devuelve k_E y k_y como «Property Modifiers». `critical_time_to_failure` da el
instante en que k_y cae por debajo del grado de utilización.

Ejecutar:  python examples/thermal_history_property_modifiers_and_collapse_time.py
"""
import numpy as np

from steelfire.en_steel_temperature import UnprotectedSteel, steel_temperature_history
from steelfire.thermal_iter import critical_time_to_failure, thermal_history

AM_V = 150.0


def main() -> None:
    hist = steel_temperature_history(UnprotectedSteel(Am_V_1_m=AM_V, ksh=0.9), duration_min=60.0, dt_s=5.0)
    t_arr = np.array([t for t, _ in hist])
    T_arr = np.array([T for _, T in hist])
    steps = thermal_history(time_minutes=list(range(0, 61, 5)),
                            temperature_provider=lambda t: float(np.interp(t, t_arr, T_arr)),
                            sections=["IPE300_fire"])
    print(f"{'t [min]':>7} {'θ_a [°C]':>9} {'k_E':>6} {'k_y':>6}  modificadores")
    for s in steps:
        print(f"{s.t_min:7.0f} {s.T_celsius:9.0f} {s.k_E:6.3f} {s.k_y:6.3f}  "
              f"E×{s.property_modifiers['E_factor']:.3f}, Fy×{s.property_modifiers['Fy_factor']:.3f} → {s.property_modifiers['sections']}")
    for mu in (0.3, 0.5, 0.7):
        t_cr = critical_time_to_failure(steps, utilization_at_t0=mu)
        print(f"\nμ₀ = {mu}: k_y cae por debajo de μ₀ a los {t_cr:.0f} min (malla de 5 min)")


if __name__ == "__main__":
    main()
