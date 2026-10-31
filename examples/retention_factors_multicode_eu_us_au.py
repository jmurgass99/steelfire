"""Factores de retención del acero a alta temperatura según la norma: EN 1993-1-2, AISC 360 Ap. 4, AS 4100.

`retention_factor` devuelve k_E, k_y o k_p para EU/SG/AU (Tabla 3.1 de EN 1993-1-2) y para
US/CO (AISC 360 Apéndice 4, Tabla A-4.2.1, que adopta los valores del Eurocódigo en nodos de
°F: coinciden en los nodos y difieren algo entre ellos). Una magnitud o un código no
soportados lanzan ValueError en vez de devolver otra magnitud. Hasta esta versión la rama US
usaba una cuadrática sin fuente que daba k_E = 0 a 400 °C.

Ejecutar:  python examples/retention_factors_multicode_eu_us_au.py
"""
from steelfire.retention_multi import retention_factor


def main() -> None:
    print(f"{'θ [°C]':>7} | {'k_E EU':>7} {'k_E US':>7} | {'k_y EU':>7} {'k_y US':>7} | {'k_p EU':>7} {'k_p US':>7}")
    for T in (20, 204, 300, 399, 500, 538, 600, 700, 800):
        print(f"{T:7d} | {retention_factor(T, 'E', 'EU'):7.3f} {retention_factor(T, 'E', 'US'):7.3f} | "
              f"{retention_factor(T, 'Fy', 'EU'):7.3f} {retention_factor(T, 'Fy', 'US'):7.3f} | "
              f"{retention_factor(T, 'kp', 'EU'):7.3f} {retention_factor(T, 'kp', 'US'):7.3f}")
    print(f"\nAU sigue la tabla EN: k_y(600, AU) = {retention_factor(600, 'Fy', 'AU'):.3f}")
    for args in ((400, "fy", "EU"), (400, "Fy", "BR")):
        try:
            retention_factor(*args)
        except ValueError as exc:
            print(f"retention_factor{args} → ValueError: {exc}")


if __name__ == "__main__":
    main()
