"""Transmisión de calor 1D a través de placa de protección y chapa de acero (elementos finitos, Crank-Nicolson).

Capa de silicato cálcico de 20 mm (λ = 0,17 W/mK, ρ = 450, c = 1 100) sobre chapa de acero de
10 mm, cara izquierda expuesta a ISO 834 (convección combinada h = 25 W/m²K) y cara derecha
a ambiente (h = 9 W/m²K). `solve_1d_thermal` da el perfil de temperaturas cada minuto; se
imprime la cara expuesta, la interfaz placa-acero y la cara fría. Modelo con propiedades
constantes: sirve para comparar protecciones, no sustituye a §4.2.5.2 para el veredicto.

Ejecutar:  python examples/thermal_1d_board_protected_steel_plate_crank_nicolson.py
"""
from steelfire.en_steel_temperature import iso834_gas
from steelfire.fem_thermal_1d import Material1D, solve_1d_thermal

LAYERS = [
    Material1D("placa silicato", thickness_m=0.020, k_W_per_mK=0.17, rho_kg_m3=450.0, c_J_per_kgK=1100.0),
    Material1D("acero", thickness_m=0.010, k_W_per_mK=45.0, rho_kg_m3=7850.0, c_J_per_kgK=600.0),
]


def main() -> None:
    res = solve_1d_thermal(LAYERS, fire_curve=iso834_gas, duration_s=3600.0, dt_s=30.0, n_elements_per_layer=6)
    n = len(res.temperatures_K[0])
    i_interface = n // 2
    print(f"{n} nodos; nodo de la interfaz placa-acero ≈ {i_interface}\n")
    print(f"{'t [min]':>7} {'gas':>6} {'cara expuesta':>14} {'interfaz':>9} {'cara fría':>10}")
    for t_s, T in zip(res.times_s, res.temperatures_K):
        t_min = t_s / 60.0
        if t_min in (0, 5, 10, 15, 20, 30, 40, 50, 60):
            print(f"{t_min:7.0f} {iso834_gas(t_min):6.0f} {T[0] - 273.15:14.0f} {T[i_interface] - 273.15:9.0f} {T[-1] - 273.15:10.0f}")
    print("\nLa chapa queda casi isoterma (conductividad alta frente a la placa): el salto térmico lo absorbe la placa.")


if __name__ == "__main__":
    main()
