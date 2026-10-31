"""Efecto sombra en perfiles en I: k_sh = 0,9·[Am/V]_b/[Am/V] (EN 1993-1-2 §4.2.5.1, ec. 4.26a).

Un perfil en I no recibe radiación en toda su superficie desarrollada: la norma lo corrige
con el factor de sombra calculado con el factor de sección del contorno encajonado. Para
un IPE con Am/V = 200 m⁻¹ y [Am/V]_b = 140 m⁻¹ sale k_sh = 0,63, y el calentamiento a 30
minutos baja de forma apreciable. El módulo implementa solo la ec. 4.26a (perfiles en I,
fuego nominal); para otras secciones la ec. 4.26b (sin el 0,9) no está disponible.

Ejecutar:  python examples/shadow_factor_i_section_boxed_section_factor.py
"""
from steelfire.en_steel_temperature import UnprotectedSteel, shadow_factor_I, steel_temperature_at

CASES = [("IPE 300", 200.0, 140.0), ("IPE 500", 150.0, 110.0), ("HEB 300", 115.0, 85.0)]


def main() -> None:
    print(f"{'perfil':<8} {'Am/V':>6} {'[Am/V]_b':>9} {'k_sh':>6} | {'θ 30 min k_sh=1':>16} {'θ 30 min con k_sh':>18}")
    for name, amv, amv_box in CASES:
        ksh = shadow_factor_I(amv, amv_box)
        t1 = steel_temperature_at(UnprotectedSteel(Am_V_1_m=amv, ksh=1.0), 30.0)
        t2 = steel_temperature_at(UnprotectedSteel(Am_V_1_m=amv, ksh=ksh), 30.0)
        print(f"{name:<8} {amv:6.0f} {amv_box:9.0f} {ksh:6.3f} | {t1:16.0f} {t2:18.0f}")
    print("\nk_sh solo depende del cociente [Am/V]_b/[Am/V]; el chequeo por perfil del paquete usa k_sh = 0,90 por defecto.")


if __name__ == "__main__":
    main()
