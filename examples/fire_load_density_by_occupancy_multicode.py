"""Densidad de carga de fuego por uso y norma, valor de cálculo y duración equivalente.

q_f,k característica por uso (EN 1991-1-2 Tabla E.4 y equivalentes de NFPA 557, AS, SS y
NSR-10), valor de cálculo q_f,d = q_f,k·m·δ_q1·δ_q2·δ_n y duración equivalente t_eq = k_c·q_f,d.
Los factores δ y k_c dependen del compartimento y de las medidas activas: aquí se usan los
valores por defecto del paquete (m = 0,8, δ_q1 = 1,2, k_c = 0,07 min·m²/MJ), que hay que
sustituir por los del proyecto.

Ejecutar:  python examples/fire_load_density_by_occupancy_multicode.py
"""
from steelfire.fire_load_density import FireLoadInput, equivalent_fire_duration_min, fire_load_density

OCCUPANCIES = ("vivienda", "oficina", "hospital", "hotel", "comercial", "biblioteca", "industria")
CODES = ("EU", "USA", "AU", "SG", "NSR")


def main() -> None:
    print("q_f,k [MJ/m²] por uso y norma:")
    print(f"{'uso':<12} | " + " | ".join(f"{c:>5}" for c in CODES))
    for occ in OCCUPANCIES:
        row = [fire_load_density(FireLoadInput(occupancy=occ, code=c)).qfk_MJ_m2 for c in CODES]
        print(f"{occ:<12} | " + " | ".join(f"{v:5.0f}" for v in row))

    print("\nOficina EU de 600 m², con rociadores (δ_n = 0,61):")
    r = fire_load_density(FireLoadInput(occupancy="oficina", floor_area_m2=600.0, delta_n=0.61, code="EU"))
    print(f"  q_f,k = {r.qfk_MJ_m2:.0f} MJ/m², q_f,d = {r.qfd_MJ_m2:.0f} MJ/m², energía total {r.total_energy_GJ:.0f} GJ")
    print(f"  t_eq = 0,07·q_f,d = {equivalent_fire_duration_min(r.qfd_MJ_m2):.0f} min")
    try:
        fire_load_density(FireLoadInput(occupancy="aparcamiento"))
    except ValueError as exc:
        print(f"\nUso no tabulado → ValueError: {exc}")


if __name__ == "__main__":
    main()
