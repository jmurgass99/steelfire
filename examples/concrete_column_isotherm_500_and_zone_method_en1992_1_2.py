"""Pilar de hormigón en incendio: método de la isoterma de 500 °C y método de las zonas (EN 1992-1-2 Anexo B).

Pilar 300×300 expuesto por las cuatro caras a ISO 834. La isoterma de 500 °C descarta el
hormigón más caliente y deja una sección reducida b_fi × h_fi; el método de las zonas divide
la semianchura en franjas, promedia k_c(θ) y da un factor de reducción de la capacidad axial.
El perfil de temperaturas en el hormigón es un modelo semiempírico del paquete (difusividad
dependiente de la temperatura y meseta a 100 °C), no los perfiles del Anexo A: sirve para
dimensionado previo.

Ejecutar:  python examples/concrete_column_isotherm_500_and_zone_method_en1992_1_2.py
"""
from steelfire.concrete_fire import isotherm_method_500, zone_method


def main() -> None:
    print("Isoterma 500 °C (Anexo B.1), pilar 300×300:")
    for t in (30, 60, 90, 120):
        r = isotherm_method_500(300.0, 300.0, t)
        print(f"  R{t:<4} T_sup = {r['T_surface_C']:5.0f} °C, a_500 = {r['a500_mm']:5.1f} mm → sección reducida {r['b_fi_mm']:.0f} × {r['h_fi_mm']:.0f} mm")

    print("\nMétodo de las zonas (Anexo B.2), pilar 300×300, f_ck = 30 MPa:")
    for t in (30, 60, 90, 120):
        z = zone_method(300.0, 300.0, t, fc=30.0, num_zones=10)
        print(f"  R{t:<4} a_z = {z['az_mm']:5.1f} mm, k_c,m = {z['kc_m']:.3f}, k_c(θ_M) = {z['kc_TM']:.3f}, "
              f"N: {z['N_ambient_kN']:.0f} → {z['N_fire_kN']:.0f} kN ({z['N_fire_kN'] / z['N_ambient_kN']:.0%})")

    z = zone_method(400.0, 400.0, 90, fc=30.0)
    print(f"\nPilar 400×400 a R90: a_z = {z['az_mm']:.1f} mm, capacidad residual {z['N_fire_kN'] / z['N_ambient_kN']:.0%}")


if __name__ == "__main__":
    main()
