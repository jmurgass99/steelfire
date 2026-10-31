"""Factores de reducción k_y,θ, k_E,θ y k_p,θ de EN 1993-1-2 Tabla 3.1 y dos casos del máster.

Tabla completa de 20 a 1 200 °C con interpolación lineal, y los dos valores de examen:
W01409 (viga IPE 550 / S235): η_fi = k_y,θ = 0,4840 → θ_a = 595,5 °C → k_y(595,5) = 0,484.
W01411 (pilar HEB en pandeo): θ_a,cr = 567,8 °C → k_y = 0,5698 y k_E = 0,4034 (la ficha
imprime 0,4004: errata de 0,003, se ancla el valor recalculado). k_p cae antes que k_y
(0,807 a 200 °C con k_y = 1), de ahí que no deba usarse una por la otra.

Ejecutar:  python examples/reduction_factors_ky_ke_kp_table_3_1_w01409_w01411.py
"""
from steelfire.iso834 import ky_from_temperature
from steelfire.thermal_iter import k_E, k_p, k_y


def main() -> None:
    print(f"{'θ [°C]':>7} {'k_y,θ':>7} {'k_p,θ':>7} {'k_E,θ':>7}")
    for T in range(20, 1201, 100):
        T = 20 if T == 20 else T - 20
        print(f"{T:7d} {k_y(T):7.3f} {k_p(T):7.3f} {k_E(T):7.3f}")
    print("\nCasos del máster:")
    print(f"  W01409  θ_a = 595,5 °C → k_y = {k_y(595.5):.4f}  (ficha 0,4840)")
    print(f"  W01411  θ_a = 567,8 °C → k_y = {k_y(567.8):.4f}, k_E = {k_E(567.8):.4f}  (ficha 0,5698 / 0,4004 errata)")
    print(f"\nky_from_temperature(650) = {ky_from_temperature(650.0):.3f} (misma tabla, módulo iso834)")
    print(f"k_y(1150) = {k_y(1150.0):.3f}; k_y(1250) = {k_y(1250.0):.3f} (por encima de 1 200 °C vale 0, no un residuo constante)")


if __name__ == "__main__":
    main()
