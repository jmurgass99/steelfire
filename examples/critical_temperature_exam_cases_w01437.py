"""Temperatura crítica θ_a,cr (EN 1993-1-2 §4.2.4, ec. 4.22) en cinco casos de examen del máster.

Ficha W01437 («Ejercicios de Fuego, EC3-1-2», exámenes UPC): cada grado de utilización μ₀
fue resuelto a mano por el alumno. Se reproducen los cinco y se comprueba la variante
simbólica del extra `analytic`. Fuera del dominio (μ₀ > 1 o ≤ 0) la función lanza
ValueError en lugar de devolver una temperatura sin sentido.

Ejecutar:  python examples/critical_temperature_exam_cases_w01437.py
"""
from steelfire.en_steel_temperature import critical_temperature
from steelfire.fire_curves_sympy import critical_temperature_steel

CASES = [
    (0.484, 589.9, "GT3 viga IPE 550 / S235"),
    (0.43, 609.0, "GT4 viga IPE 270 / S235"),
    (0.28, 674.0, "GT4 tirante 2L 40x4"),
    (0.16, 758.55, "GT1/GT5 columna HEB 220/240"),
    (0.571, 563.0, "GT5 columna HEB 220 (método del pandeo)"),
]


def main() -> None:
    print(f"{'μ₀':>6} {'θ_cr [°C]':>10} {'ficha':>8}  caso")
    for mu, ref, label in CASES:
        print(f"{mu:6.3f} {critical_temperature(mu):10.1f} {ref:8.1f}  {label}")
    print(f"\nVariante simbólica (sympy), μ₀ = 0,16: {critical_temperature_steel(0.16):.2f} °C")
    print("\nCurva completa:")
    for mu in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        print(f"  μ₀ = {mu:.1f} → θ_cr = {critical_temperature(mu):6.1f} °C")
    try:
        critical_temperature(1.05)
    except ValueError as exc:
        print(f"\nμ₀ = 1,05 → ValueError: {exc}")


if __name__ == "__main__":
    main()
