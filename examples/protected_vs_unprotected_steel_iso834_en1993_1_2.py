"""Temperatura del acero bajo la curva ISO 834: perfil sin proteger y protegido.

Método incremental de EN 1993-1-2 §4.2.5. Se compara un perfil con factor de
sección Am/V = 150 m⁻¹ sin protección frente al mismo perfil con 20 mm de
vermiculita proyectada, y se indica a qué tiempo se alcanza la temperatura
crítica para un grado de utilización μ₀ = 0,6.

Ejecutar:  python examples/01_protected_vs_unprotected.py
"""
from steelfire.en_steel_temperature import (
    ProtectedSteel,
    UnprotectedSteel,
    critical_temperature,
    iso834_gas,
    steel_temperature_history,
)

AM_V = 150.0
MU0 = 0.60


def main() -> None:
    theta_cr = critical_temperature(mu_0=MU0)
    bare = UnprotectedSteel(Am_V_1_m=AM_V)
    prot = ProtectedSteel(Am_V_1_m=AM_V, dp_m=0.020, lambda_p=0.12, cp=1100.0, rho_p=350.0)

    hist_bare = steel_temperature_history(bare, duration_min=120.0, dt_s=5.0)
    hist_prot = steel_temperature_history(prot, duration_min=120.0, dt_s=5.0)

    print(f"Temperatura crítica para μ₀ = {MU0}: θ_cr = {theta_cr:.0f} °C\n")
    print(f"{'t [min]':>7} {'gas':>8} {'sin prot.':>10} {'vermiculita 20 mm':>18}")
    for t in (0, 5, 10, 15, 20, 30, 45, 60, 90, 120):
        tb = next(th for tm, th in hist_bare if tm >= t - 1e-6)
        tp = next(th for tm, th in hist_prot if tm >= t - 1e-6)
        print(f"{t:7d} {iso834_gas(t):8.0f} {tb:10.0f} {tp:18.0f}")

    def time_to(hist, limit):
        return next((tm for tm, th in hist if th >= limit), None)

    for name, hist in (("sin protección", hist_bare), ("con vermiculita", hist_prot)):
        t = time_to(hist, theta_cr)
        print(f"\n{name}: θ_cr se alcanza a los {t:.1f} min" if t else f"\n{name}: no alcanza θ_cr en 120 min")


if __name__ == "__main__":
    main()
