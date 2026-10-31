"""Comprobación de resistencia al fuego de un perfil con clase exigida (R30/R60/R90).

Dado un perfil, su factor de sección y el grado de utilización en situación de
incendio, se evalúa si necesita protección para la clase exigida y se verifica la
protección del catálogo del tipo pedido: con capa inerte (mortero, placa) se integra
EN 1993-1-2 §4.2.5.2 con el espesor medio del producto y se compara con θ_cr; con
pintura intumescente no hay cálculo posible y, sin tabla de ensayo cargada, el
resultado es NO_VERIFICADO.

Ejecutar:  python examples/02_fire_rating_check_by_profile.py
"""
from steelfire.en_steel_temperature import check_fire_resistance_from_profile

CASES = [
    # perfil, Am/V [1/m], μ0, clase exigida, tipo de protección preferido
    ("IPE 300 (viga de forjado)", 200.0, 0.55, "R30", "spray"),
    ("IPE 300 (viga de forjado)", 200.0, 0.55, "R60", "board"),
    ("HEB 300 (pilar)", 115.0, 0.65, "R60", "spray"),
    ("HEB 300 (pilar)", 115.0, 0.65, "R90", "board"),
    ("HEB 300 (pilar)", 115.0, 0.65, "R60", "intumescent"),
]


def main() -> None:
    for name, am_v, mu0, rating, ptype in CASES:
        r = check_fire_resistance_from_profile(name, Am_V_m_inv=am_v, load_ratio_mu0=mu0,
                                               required_rating=rating, preferred_protection_type=ptype)
        print(f"{name} — Am/V = {am_v:.0f} m⁻¹, μ₀ = {mu0}, exigido {rating} ({r.duration_min:.0f} min), protección {ptype}")
        print(f"  θ_cr = {r.theta_crit_C:.0f} °C | θ sin protección a {r.duration_min:.0f} min = {r.theta_unprotected_C:.0f} °C")
        print(f"  ¿requiere protección? {'sí' if r.requires_protection else 'no'}")
        if r.recommended_protection:
            print(f"  protección propuesta: {r.recommended_protection}")
        if r.theta_protected_C is not None:
            print(f"  θ con protección = {r.theta_protected_C:.0f} °C")
        print(f"  estado: {r.verification_status} | seguro: {r.is_safe}")
        for n in r.notes:
            print(f"  nota: {n}")
        print()


if __name__ == "__main__":
    main()
