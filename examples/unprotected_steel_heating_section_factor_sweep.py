"""Calentamiento de perfiles sin proteger bajo ISO 834 según su factor de sección Am/V.

Método incremental de EN 1993-1-2 §4.2.5.1 (ec. 4.25) con Δt = 5 s, α_c = 25 W/m²K y
ε_res = 0,7, sin efecto sombra. Se compara desde un perfil macizo (Am/V = 50 m⁻¹, p. ej.
un HEM) hasta uno muy esbelto (300 m⁻¹, chapa fina): temperatura a 15, 30 y 60 minutos
y tiempo en alcanzar 500 °C, que es el orden de la temperatura crítica para un grado de
utilización habitual.

Ejecutar:  python examples/unprotected_steel_heating_section_factor_sweep.py
"""
from steelfire.en_steel_temperature import UnprotectedSteel, iso834_gas, steel_temperature_history

SECTION_FACTORS = (50.0, 100.0, 150.0, 200.0, 300.0)


def temp_at(hist, t_min):
    return next(th for tm, th in hist if tm >= t_min - 1e-9)


def main() -> None:
    print(f"Gas ISO 834: 15 min → {iso834_gas(15):.0f} °C, 30 min → {iso834_gas(30):.0f} °C, 60 min → {iso834_gas(60):.0f} °C\n")
    print(f"{'Am/V [1/m]':>10} {'θ 15 min':>9} {'θ 30 min':>9} {'θ 60 min':>9} {'t(500 °C)':>10}")
    for amv in SECTION_FACTORS:
        hist = steel_temperature_history(UnprotectedSteel(Am_V_1_m=amv), duration_min=60.0, dt_s=5.0)
        t500 = next((tm for tm, th in hist if th >= 500.0), None)
        print(f"{amv:10.0f} {temp_at(hist, 15):9.0f} {temp_at(hist, 30):9.0f} {temp_at(hist, 60):9.0f} "
              f"{(f'{t500:.1f} min' if t500 else '> 60 min'):>10}")
    print("\nPor encima de Am/V ≈ 100 m⁻¹ el acero sigue al gas con poco retraso: sin protección no hay R30 "
          "salvo con grados de utilización muy bajos.")


if __name__ == "__main__":
    main()
