"""De la carga de fuego del local al veredicto de la viga: duración equivalente y temperatura del acero.

Biblioteca EU (q_f,k = 1 500 MJ/m²) sin rociadores frente a oficina con rociadores: valor
de cálculo q_f,d, duración equivalente t_eq y temperatura que alcanza en t_eq una viga IPE
con Am/V = 200 m⁻¹ (k_sh = 0,9) sin proteger y con 20 mm de placa, comparada con la
temperatura crítica para μ₀ = 0,6. Encadena tres módulos del paquete; los factores δ y k_c
son los por defecto y deben ajustarse al proyecto.

Ejecutar:  python examples/compartment_equivalent_fire_duration_vs_steel_heating.py
"""
from steelfire.en_steel_temperature import ProtectedSteel, UnprotectedSteel, critical_temperature, steel_temperature_at
from steelfire.fire_load_density import FireLoadInput, equivalent_fire_duration_min, fire_load_density

AM_V, MU0 = 200.0, 0.60
CASES = [("biblioteca sin rociadores", FireLoadInput(occupancy="biblioteca", floor_area_m2=400.0)),
         ("oficina con rociadores", FireLoadInput(occupancy="oficina", floor_area_m2=400.0, delta_n=0.61)),
         ("vivienda", FireLoadInput(occupancy="vivienda", floor_area_m2=90.0, delta_q1=1.0))]


def main() -> None:
    theta_cr = critical_temperature(MU0)
    bare = UnprotectedSteel(Am_V_1_m=AM_V, ksh=0.9)
    board = ProtectedSteel(Am_V_1_m=AM_V, dp_m=0.020, lambda_p=0.20, cp=1000.0, rho_p=900.0)
    print(f"Viga Am/V = {AM_V:.0f} m⁻¹, μ₀ = {MU0} → θ_cr = {theta_cr:.0f} °C\n")
    print(f"{'local':<27} {'q_f,d':>7} {'t_eq':>6} | {'θ sin prot.':>11} {'':>3} {'θ placa 20':>10} {'':>3}")
    for name, inp in CASES:
        r = fire_load_density(inp)
        t_eq = equivalent_fire_duration_min(r.qfd_MJ_m2)
        tb = steel_temperature_at(bare, t_eq)
        tp = steel_temperature_at(board, t_eq)
        print(f"{name:<27} {r.qfd_MJ_m2:7.0f} {t_eq:6.0f} | {tb:11.0f} {'OK' if tb <= theta_cr else 'NO':>3} {tp:10.0f} {'OK' if tp <= theta_cr else 'NO':>3}")


if __name__ == "__main__":
    main()
