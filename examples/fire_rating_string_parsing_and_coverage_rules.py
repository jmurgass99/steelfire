"""Clasificaciones EN 13501-2: leer los minutos de «REI 90» y decidir si una certificación cubre un requisito.

El número de la clase son minutos y la comparación es numérica («R120» cubre «R90» aunque
como texto '1' < '9'); las letras son prestaciones distintas: R (capacidad portante), E
(integridad), I (aislamiento). Un producto R120 no cubre un EI90, un REI120 sí cubre un
R90. Una cadena ininteligible lanza ValueError en vez de caer a un valor por defecto.

Ejecutar:  python examples/fire_rating_string_parsing_and_coverage_rules.py
"""
from steelfire.en_steel_temperature import parse_fire_rating_minutes, rating_covers


def main() -> None:
    for s in ("R60", "R 90", "REI90", "REI-90", "EI30", "rei 120"):
        print(f"parse_fire_rating_minutes({s!r:>10}) = {parse_fire_rating_minutes(s):5.0f} min")

    print("\n¿cubre la certificación al requisito?")
    for cert, req in (("REI120", "R90"), ("R120", "EI90"), ("R90", "R120"), ("REI60", "REI60"),
                      ("REI90", "EI60"), ("R120", "R90")):
        print(f"  {cert:<7} → {req:<6}: {rating_covers(cert, req)}")

    for bad in ("R-abc", "60", "RX60", "R0"):
        try:
            parse_fire_rating_minutes(bad)
        except ValueError as exc:
            print(f"\n{bad!r} → ValueError: {str(exc)[:90]}…")


if __name__ == "__main__":
    main()
