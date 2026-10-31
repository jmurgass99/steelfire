"""Servicio tipado del solver térmico 2D: viga bajo forjado (tres caras expuestas) frente a pilar (cuatro).

`run_thermal_analysis` envuelve `solve_thermal` con entradas validadas y un resultado
serializable (series de T_max y T_media). Se comparan una viga 300×500 con la cara superior
protegida por el forjado y un pilar 300×300 expuesto por las cuatro caras, 30 minutos de
ISO 834. Una configuración inválida lanza ConfigurationError.

Ejecutar:  python examples/thermal_service_typed_api_three_sides_exposed.py
"""
from steelfire.exceptions import ConfigurationError
from steelfire.services.thermal import ThermalAnalysisInput, run_thermal_analysis


def main() -> None:
    cases = {
        "viga 300x500, 3 caras (superior cubierta)": ThermalAnalysisInput(
            b=0.30, h=0.50, n_x=12, n_y=20, exposed_faces=(True, True, False, True), t_total=1800.0),
        "pilar 300x300, 4 caras": ThermalAnalysisInput(b=0.30, h=0.30, n_x=12, n_y=12, t_total=1800.0),
        "pilar 300x300, 4 caras, 20 mm protección": ThermalAnalysisInput(
            b=0.30, h=0.30, n_x=12, n_y=12, protection_thickness=0.020, protection_k=0.12, t_total=1800.0),
    }
    for name, inp in cases.items():
        r = run_thermal_analysis(inp)
        i15 = min(range(len(r.times)), key=lambda k: abs(r.times[k] - 900.0))
        print(f"{name:<44} 15 min: máx {r.T_max_history[i15]:5.0f} / media {r.T_mean_history[i15]:5.0f} °C | "
              f"30 min: máx {r.T_final_max:5.0f} / media {r.T_final_mean:5.0f} °C  ({r.n_steps_saved} instantes guardados)")
    try:
        run_thermal_analysis(ThermalAnalysisInput(b=0.30, h=0.30, n_x=1, n_y=12))
    except ConfigurationError as exc:
        print(f"\nn_x = 1 → ConfigurationError: {exc}")


if __name__ == "__main__":
    main()
