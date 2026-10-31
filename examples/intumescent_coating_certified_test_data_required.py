"""Pintura intumescente: sin tabla de ensayo no hay veredicto; con ella, se verifica por clasificación certificada.

Un recubrimiento reactivo se expande 20–50 veces y su conductividad cambia con la
temperatura: no es la capa inerte de EN 1993-1-2 §4.2.5.2, así que el paquete no integra
la ec. 4.27 con su λ_p de película seca (daba 917 °C para un IPE 300, «la pintura no
protege»). El chequeo responde NO_VERIFICADO hasta que se cargan filas del informe de
ensayo (UL 263 / EN 13381-8). Aquí se carga una fila ILUSTRATIVA, no un dato real, para
mostrar el camino certificado y que fuera del Am/V ensayado no se extrapola.

Ejecutar:  python examples/intumescent_coating_certified_test_data_required.py
"""
from dataclasses import replace

from steelfire.en_steel_temperature import check_fire_resistance_from_profile
from steelfire.protection_catalog import CertifiedRating, certified_specification, lookup


def main() -> None:
    r = check_fire_resistance_from_profile("IPE 300", Am_V_m_inv=200.0, load_ratio_mu0=0.65,
                                           required_rating="R60", preferred_protection_type="intumescent")
    print(f"Catálogo tal cual: estado = {r.verification_status}, is_safe = {r.is_safe}")
    for n in r.notes:
        print(f"  nota: {n}")

    base = lookup("UL 60-INT-acrylic")
    illustrative = replace(base, certified_ratings=(
        CertifiedRating(Am_V_max_1_m=220.0, thickness_mm=1.20, rating="R60",
                        source="fila ILUSTRATIVA de este ejemplo; sustituir por el DoP / informe UL del fabricante"),
    ))
    print(f"\nProducto {illustrative.code} con una fila de ensayo cargada ({illustrative.design_method}):")
    for amv in (150.0, 200.0, 250.0):
        spec = certified_specification(illustrative, amv, "R60")
        if spec is None:
            print(f"  Am/V = {amv:.0f} m⁻¹ → sin fila aplicable (no se extrapola fuera del Am/V ensayado)")
        else:
            print(f"  Am/V = {amv:.0f} m⁻¹ → {spec.rating} con {spec.thickness_mm:.2f} mm (hasta {spec.Am_V_max_1_m:.0f} m⁻¹); fuente: {spec.source}")
    print(f"  requisito R90 con la misma fila → {certified_specification(illustrative, 200.0, 'R90')}")


if __name__ == "__main__":
    main()
