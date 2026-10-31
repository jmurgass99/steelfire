"""Las cinco curvas nominales de fuego, con derivada e integral simbólicas (extra `analytic`).

ISO 834 y externa (EN 1991-1-2 §3.2.1 y §3.2.3), hidrocarburos (§3.2.2), ASTM E119 (ajuste
de Lie 1992) y RWS (túneles, Rijkswaterstaat). `fire_curves_sympy` devuelve cada curva como
expresión de sympy con su callable, su derivada (gradiente térmico, °C/min) y su primitiva
(para la energía acumulada). Se tabulan las temperaturas del gas, la velocidad de
calentamiento de ISO 834 en los primeros minutos y el área bajo la curva en una hora.
Requiere `pip install "steelfire[analytic]"`.

Ejecutar:  python examples/fire_curves_iso834_hydrocarbon_external_astm_rws_comparison.py
"""
from steelfire.fire_curves_sympy import astm_e119, external, hydrocarbon, iso_834, rws

TIMES = [0, 5, 10, 15, 30, 60, 90, 120]


def main() -> None:
    curves = [iso_834(), hydrocarbon(), external(), astm_e119(), rws()]
    print(f"{'t [min]':>7} | " + " | ".join(f"{c.name:>11}" for c in curves))
    for t in TIMES:
        print(f"{t:7d} | " + " | ".join(f"{float(c.lambda_t_min(t)):11.0f}" for c in curves))

    iso = iso_834()
    print(f"\n{iso.name}: {iso.expression_str}")
    print(f"  LaTeX: {iso.latex}")
    for t in (1, 5, 15, 30, 60):
        print(f"  dθ/dt a {t:2d} min = {float(iso.derivative_callable(t)):7.1f} °C/min")
    energy = float(iso.integral_callable(60)) - float(iso.integral_callable(0))
    print(f"  ∫₀⁶⁰ θ_g dt = {energy:.0f} °C·min  (media {energy / 60:.0f} °C en la primera hora)")
    hc = hydrocarbon()
    energy_hc = float(hc.integral_callable(60)) - float(hc.integral_callable(0))
    print(f"{hc.name}: ∫₀⁶⁰ θ_g dt = {energy_hc:.0f} °C·min  (media {energy_hc / 60:.0f} °C)")


if __name__ == "__main__":
    main()
