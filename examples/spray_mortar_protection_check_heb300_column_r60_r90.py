"""Pilar HEB 300 con mortero proyectado o placa: chequeo R60 y R90 y espesor mínimo que cumple.

`check_fire_resistance_from_profile` aplica el espesor medio del rango típico del producto
y compara de verdad la temperatura protegida (ec. 4.27) con la crítica: el veredicto sale
de esa comparación. Después se busca a mano el espesor mínimo de placa que cumple R90,
integrando `ProtectedSteel` milímetro a milímetro.

Ejecutar:  python examples/spray_mortar_protection_check_heb300_column_r60_r90.py
"""
from steelfire.en_steel_temperature import (
    ProtectedSteel,
    check_fire_resistance_from_profile,
    critical_temperature,
    steel_temperature_at,
)
from steelfire.protection_catalog import lookup

AM_V, MU0 = 115.0, 0.65


def main() -> None:
    for rating, ptype in (("R60", "spray"), ("R90", "spray"), ("R90", "board"), ("R120", "board")):
        r = check_fire_resistance_from_profile("HEB 300", Am_V_m_inv=AM_V, load_ratio_mu0=MU0,
                                               required_rating=rating, preferred_protection_type=ptype)
        prot = r.recommended_protection
        extra = (f"{prot['code']} {prot['thickness_mm']:.1f} mm → θ_prot = {r.theta_protected_C:.0f} °C"
                 if prot and r.theta_protected_C is not None else "sin producto evaluado")
        print(f"{rating} con {ptype:<5}: θ_cr = {r.theta_crit_C:.0f} °C, θ sin proteger = {r.theta_unprotected_C:.0f} °C; "
              f"{extra}; estado {r.verification_status}")

    board = lookup("EN 90-board-cem")
    theta_cr = critical_temperature(MU0)
    print(f"\nEspesor mínimo de {board.code} para R90 (θ_cr = {theta_cr:.0f} °C):")
    for dp in range(8, 41, 2):
        sec = ProtectedSteel(Am_V_1_m=AM_V, dp_m=dp / 1000.0, lambda_p=board.lambda_p_W_per_mK,
                             cp=board.c_p_J_per_kgK, rho_p=board.rho_p_kg_m3)
        t90 = steel_temperature_at(sec, 90.0)
        print(f"  d_p = {dp:2d} mm → θ(90 min) = {t90:5.0f} °C {'OK' if t90 <= theta_cr else ''}")
        if t90 <= theta_cr:
            break


if __name__ == "__main__":
    main()
