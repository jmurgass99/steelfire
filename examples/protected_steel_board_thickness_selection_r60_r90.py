"""Espesor de placa de protección para R60 y R90 de una viga con Am/V = 200 m⁻¹ (EN 1993-1-2 §4.2.5.2).

Placa de silicato cálcico (λ_p = 0,17 W/mK, ρ_p = 450 kg/m³, c_p = 1 100 J/kgK) adosada al
contorno (A_p/V = Am/V). Para cada espesor se integra la ec. 4.27 bajo ISO 834 y se compara la
temperatura del acero a 60 y 90 minutos con la temperatura crítica de un grado de utilización
μ₀ = 0,60 (θ_cr = 554 °C). La primera fila que cumple da el espesor mínimo de catálogo.

Ejecutar:  python examples/protected_steel_board_thickness_selection_r60_r90.py
"""
from steelfire.en_steel_temperature import ProtectedSteel, critical_temperature, steel_temperature_at

AM_V, MU0 = 200.0, 0.60
BOARD = dict(lambda_p=0.17, rho_p=450.0, cp=1100.0)


def main() -> None:
    theta_cr = critical_temperature(MU0)
    print(f"Am/V = {AM_V:.0f} m⁻¹, μ₀ = {MU0} → θ_cr = {theta_cr:.0f} °C; placa λ_p = {BOARD['lambda_p']} W/mK\n")
    print(f"{'d_p [mm]':>8} {'θ 60 min':>9} {'R60':>5} {'θ 90 min':>9} {'R90':>5}")
    for dp in (12.5, 15.0, 20.0, 25.0, 30.0, 40.0):
        sec = ProtectedSteel(Am_V_1_m=AM_V, dp_m=dp / 1000.0, **BOARD)
        t60 = steel_temperature_at(sec, 60.0)
        t90 = steel_temperature_at(sec, 90.0)
        print(f"{dp:8.1f} {t60:9.0f} {'OK' if t60 <= theta_cr else 'NO':>5} {t90:9.0f} {'OK' if t90 <= theta_cr else 'NO':>5}")
    print("\nLa ec. 4.27 anula el enfriamiento ficticio del término exponencial mientras el gas sube; "
          "el espesor final debe tomarse del catálogo del fabricante para ese A_p/V.")


if __name__ == "__main__":
    main()
