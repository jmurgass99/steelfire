"""Catálogo de protecciones pasivas: recomendar por clase exigida y presupuesto, y qué método verifica cada una.

Seis productos (dos intumescentes, mortero proyectado, dos placas y hormigón) con su
método de verificación: `inert_layer` (se integra §4.2.5.2 con λ_p, ρ_p, c_p) o
`certified_test` (solo por tabla de ensayo). `recommend` filtra por clase alcanzable y
coste y ordena por precio.

Ejecutar:  python examples/protection_catalog_recommend_by_rating_and_budget.py
"""
from steelfire.protection_catalog import CATALOG, lookup, recommend


def show(title, items):
    print(title)
    if not items:
        print("  (ninguna)")
    for p in items:
        lam = f"{p.lambda_p_W_per_mK:.2f}" if p.lambda_p_W_per_mK is not None else "—"
        print(f"  {p.code:<20} {p.type:<13} R{p.rating_minutes:<4} {p.cost_USD_per_m2:5.0f} USD/m²  "
              f"d = {p.typical_thickness_mm[0]:.1f}–{p.typical_thickness_mm[1]:.1f} mm  λ_p = {lam:<5} {p.design_method}")
    print()


def main() -> None:
    show(f"Catálogo completo ({len(CATALOG)} productos):", CATALOG)
    show("Candidatos para R60, por coste:", recommend(60))
    show("Candidatos para R90 con presupuesto ≤ 60 USD/m²:", recommend(90, budget_USD_per_m2=60.0))
    show("Candidatos para R180:", recommend(180))
    p = lookup("EN 120-board-silic")
    print(f"lookup('EN 120-board-silic') → ρ_p = {p.rho_p_kg_m3} kg/m³, c_p = {p.c_p_J_per_kgK} J/kgK, "
          f"filas certificadas: {len(p.certified_ratings)}")


if __name__ == "__main__":
    main()
