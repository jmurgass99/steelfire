"""Análisis térmico 2D de una sección rectangular de acero por diferencias finitas.

Se resuelve la ecuación del calor en la sección (malla n_x × n_y) bajo la curva
ISO 834 con las cuatro caras expuestas, sin protección y con 15 mm de
protección, y se comparan la temperatura máxima y media a 15 y 30 minutos.
También se muestra el efecto de exponer solo tres caras (viga bajo forjado).

Ejecutar:  python examples/03_thermal_fea_section.py
"""
from steelfire import ThermalSection, solve_thermal

T_TOTAL = 1800.0   # 30 min


def summary(label: str, section: ThermalSection) -> None:
    res = solve_thermal(section, t_total=T_TOTAL)
    times = res.times
    def at(t_s):
        i = min(range(len(times)), key=lambda k: abs(times[k] - t_s))
        return res.T_max_history[i], res.T_mean_history[i]
    tmax15, tmean15 = at(900.0)
    tmax30, tmean30 = at(T_TOTAL)
    print(f"{label:<42} 15 min: máx {tmax15:6.0f} / media {tmean15:6.0f} °C | "
          f"30 min: máx {tmax30:6.0f} / media {tmean30:6.0f} °C")


def main() -> None:
    print("Sección 200 x 400 mm, curva ISO 834\n")
    summary("4 caras expuestas, sin protección",
            ThermalSection(b=0.20, h=0.40, n_x=10, n_y=20))
    summary("3 caras expuestas (cara superior protegida)",
            ThermalSection(b=0.20, h=0.40, n_x=10, n_y=20, exposed_faces=(True, True, False, True)))
    summary("4 caras, 15 mm de protección (k = 0,12 W/mK)",
            ThermalSection(b=0.20, h=0.40, n_x=10, n_y=20, protection_thickness=0.015, protection_k=0.12))


if __name__ == "__main__":
    main()
