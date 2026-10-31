"""Distancia al eje de la armadura y dimensión mínima por clase R (EN 1992-1-2, método tabulado).

Tabla 5.2a para pilares (μ_fi = 0,7, expuestos por más de una cara), Tabla 5.5 para vigas
simplemente apoyadas y Tabla 5.8 para losas unidireccionales, de R30 a R240. Se comprueba
además si la dimensión disponible alcanza la mínima. Una clase no tabulada (R100) se
redondea a la siguiente disponible.

Ejecutar:  python examples/concrete_cover_axis_distance_for_r_rating_en1992_1_2.py
"""
from steelfire.concrete_fire import cover_for_R_rating

MEMBERS = (("column", 300.0), ("beam", 250.0), ("slab", 150.0))


def main() -> None:
    for member, dim in MEMBERS:
        print(f"{member}: dimensión disponible {dim:.0f} mm")
        print(f"  {'R':>5} {'b_min':>6} {'a [mm]':>7}  cumple b_min")
        for R in (30, 60, 90, 120, 180, 240):
            r = cover_for_R_rating(dim, R, member_type=member)
            print(f"  R{R:<4} {r['b_min_required_mm']:6.0f} {r['axis_distance_a_mm']:7.0f}  {'sí' if r['b_ok'] else 'NO'}")
    r = cover_for_R_rating(350.0, 100, member_type="column")
    print(f"\nR100 (no tabulado) → se evalúa como R{r['R_min']}: a = {r['axis_distance_a_mm']} mm")


if __name__ == "__main__":
    main()
