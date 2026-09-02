"""
Catálogo de protecciones pasivas para acero estructural — UL/EN.

Tipos:
    intumescent      — pintura intumescente (acrílica/epóxica)
    spray_mortar     — mortero proyectado base cementicia / yeso
    board            — placa cartón-yeso / cemento / silicato calcio
    concrete         — recubrimiento de hormigón

MÉTODO DE VERIFICACIÓN (``design_method``)
------------------------------------------
No todos los productos se verifican igual, y es una distinción física, no
administrativa:

``inert_layer`` — mortero, placa, hormigón. Aislante de espesor ``dp`` y
    conductividad ``lambda_p`` sensiblemente constantes: es exactamente la
    hipótesis del modelo de EN 1993-1-2 §4.2.5.2, que puede integrarse para
    obtener la temperatura del acero.

``certified_test`` — pinturas intumescentes (recubrimientos REACTIVOS). Se
    expanden entre 20 y 50 veces al calentarse y su conductividad efectiva
    cambia con la temperatura, de modo que NO son una capa inerte. El
    ``lambda_p`` de película seca que figura en las fichas de producto no es la
    conductividad de la espuma que realmente aísla: introducirlo en §4.2.5.2 es
    meter la propiedad equivocada en el modelo equivocado (para un IPE 300 con
    Am/V = 200 1/m y 1,8 mm daba 916,7 °C, "la pintura no protege nada").
    Estos productos se especifican por ESPESOR CERTIFICADO DE ENSAYO
    (UL 263 / EN 13381-8) para un factor de sección Am/V y una clasificación
    (R30/R60/R90/R120) dados. Es una tabla de ensayo, no un cálculo.

Por eso ``lambda_p_W_per_mK`` es ``None`` en los productos reactivos: el dato de
película seca no sirve para el modelo y se propaga como ausencia, para que
cualquier uso accidental falle en vez de devolver un número.

DATOS DE ENSAYO
---------------
Este catálogo NO distribuye tablas de ensayo (``certified_ratings`` vacío en
todos los productos reactivos). No se dispone de ninguna tabla UL 263 /
EN 13381-8 de fuente citable, y espesores certificados inventados serían mucho
peor que el defecto que se corrige: aparentarían autoridad de ensayo. Sin dato
certificado, el chequeo se niega (``NO_VERIFICADO``) en vez de responder.

Para usar la vía certificada en un proyecto real, cárguense en
``certified_ratings`` las filas del informe de ensayo / DoP del fabricante, con
su ``source`` citando el documento.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Método de verificación aplicable a un producto.
METHOD_INERT_LAYER = "inert_layer"          # EN 1993-1-2 §4.2.5.2
METHOD_CERTIFIED_TEST = "certified_test"    # UL 263 / EN 13381-8 (tabla)


@dataclass(frozen=True)
class CertifiedRating:
    """Una fila de una tabla de ensayo de un recubrimiento reactivo.

    "Para este producto, hasta este factor de sección y con este espesor seco,
    la clasificación ensayada es ésta."

    Attributes:
        Am_V_max_1_m: factor de sección máximo cubierto por la fila (1/m). Un
            perfil más esbelto que esto NO está cubierto: no se extrapola.
        thickness_mm: espesor seco de película certificado en el ensayo.
        rating: clasificación EN 13501-2 alcanzada ("R60", "R90", ...).
        source: documento del que sale la fila (informe UL, DoP, ETA). Es
            obligatorio: una fila sin procedencia citada no es un dato de ensayo.
    """
    Am_V_max_1_m: float
    thickness_mm: float
    rating: str
    source: str


@dataclass(frozen=True)
class FireProtection:
    code: str
    type: str
    lambda_p_W_per_mK: float | None   # conductividad W/mK; None si no aplica §4.2.5.2
    rho_p_kg_m3: float                # densidad
    c_p_J_per_kgK: float              # calor específico
    typical_thickness_mm: tuple[float, float]   # min, max
    cost_USD_per_m2: float
    rating_minutes: int               # R-rating típico del producto (orientativo)
    design_method: str = METHOD_INERT_LAYER
    certified_ratings: tuple[CertifiedRating, ...] = field(default_factory=tuple)


CATALOG: list[FireProtection] = [
    # Recubrimientos REACTIVOS: sin lambda_p utilizable y sin tabla de ensayo
    # cargada. Ver la nota "DATOS DE ENSAYO" de la cabecera.
    FireProtection("UL 60-INT-acrylic",  "intumescent",  None, 1300,  900,
                    (0.6, 3.0),   45.0, 60,
                    design_method=METHOD_CERTIFIED_TEST),
    FireProtection("UL 120-INT-epoxy",   "intumescent",  None, 1300,  900,
                    (1.2, 6.0),   85.0, 120,
                    design_method=METHOD_CERTIFIED_TEST),
    # Capas INERTES: §4.2.5.2 aplica.
    FireProtection("UL 60-spray-mortar", "spray_mortar", 0.12,  300, 1100,
                    (15.0, 35.0), 35.0, 60),
    FireProtection("EN 90-board-cem",    "board",        0.20,  900, 1000,
                    (12.5, 25.0), 55.0, 90),
    FireProtection("EN 120-board-silic", "board",        0.17,  450, 1100,
                    (20.0, 40.0), 70.0, 120),
    FireProtection("Concrete-R180",      "concrete",     1.40, 2300, 1000,
                    (30.0, 60.0), 25.0, 180),
]


def recommend(target_rating_min: int,
                budget_USD_per_m2: float | None = None
                ) -> list[FireProtection]:
    out = [p for p in CATALOG if p.rating_minutes >= target_rating_min]
    if budget_USD_per_m2 is not None:
        out = [p for p in out if p.cost_USD_per_m2 <= budget_USD_per_m2]
    return sorted(out, key=lambda p: p.cost_USD_per_m2)


def lookup(code: str) -> FireProtection | None:
    for p in CATALOG:
        if p.code == code:
            return p
    return None


def certified_specification(protection: FireProtection,
                            Am_V_1_m: float,
                            required_rating: str) -> CertifiedRating | None:
    """Fila de ensayo que cubre ``required_rating`` para este factor de sección.

    Una fila cubre el caso si (a) el factor de sección del perfil no excede el
    máximo ensayado — fuera del rango ensayado no se extrapola — y (b) la
    clasificación ensayada cubre la requerida (comparación en MINUTOS, no de
    cadenas). De las filas que cubren se devuelve la de menor espesor.

    Devuelve ``None`` si el producto no tiene ninguna fila aplicable: la
    ausencia de ensayo se propaga como ausencia, nunca como un espesor
    sustituto.

    Raises:
        ValueError: si ``required_rating`` no es una clasificación interpretable.
    """
    from .en_steel_temperature import rating_covers

    aplicables = [
        c for c in protection.certified_ratings
        if Am_V_1_m <= c.Am_V_max_1_m and rating_covers(c.rating, required_rating)
    ]
    if not aplicables:
        return None
    return min(aplicables, key=lambda c: c.thickness_mm)


__all__ = [
    "FireProtection",
    "CertifiedRating",
    "CATALOG",
    "METHOD_INERT_LAYER",
    "METHOD_CERTIFIED_TEST",
    "recommend",
    "lookup",
    "certified_specification",
]
