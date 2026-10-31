"""Calor específico del acero (EN 1993-1-2 §3.4.1.2) y la meseta de calentamiento hacia 735 °C.

c_a(θ) crece hasta un pico en 735 °C (transformación de fase) y vuelve a 650 J/kgK por
encima de 900 °C. El incremento Δθ de la ec. 4.25 es inversamente proporcional a c_a, así
que un perfil sin proteger frena su calentamiento al acercarse a 735 °C y luego lo
reanuda. Se tabula c_a y se mide la velocidad de calentamiento de un perfil con
Am/V = 150 m⁻¹ en distintas franjas de temperatura.

Ejecutar:  python examples/specific_heat_peak_735c_and_heating_rate.py
"""
from steelfire.en_steel_temperature import UnprotectedSteel, specific_heat_steel, steel_temperature_history


def main() -> None:
    print(f"{'θ [°C]':>7} {'c_a [J/kgK]':>12}")
    for T in (20, 200, 400, 600, 700, 720, 730, 734, 736, 740, 760, 800, 900, 1000):
        print(f"{T:7d} {specific_heat_steel(float(T)):12.1f}")

    hist = steel_temperature_history(UnprotectedSteel(Am_V_1_m=150.0), duration_min=40.0, dt_s=5.0)
    print("\nVelocidad media de calentamiento por franja (Am/V = 150 m⁻¹, ISO 834):")
    bands = [(100, 300), (300, 500), (500, 650), (650, 720), (720, 750), (750, 800)]
    for lo, hi in bands:
        t_lo = next((tm for tm, th in hist if th >= lo), None)
        t_hi = next((tm for tm, th in hist if th >= hi), None)
        if t_lo is None or t_hi is None:
            print(f"  {lo}–{hi} °C: no se alcanza en 40 min")
            continue
        print(f"  {lo:3d}–{hi:3d} °C: {(hi - lo) / (t_hi - t_lo):6.1f} °C/min  (de {t_lo:.1f} a {t_hi:.1f} min)")


if __name__ == "__main__":
    main()
