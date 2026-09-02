# -*- coding: utf-8 -*-
"""D5 - los recubrimientos REACTIVOS no se verifican con EN 1993-1-2 §4.2.5.2.

DEFECTO. Arreglado D1 (``is_safe`` salia de la EXISTENCIA de una entrada de
catalogo), el calculo empezo a ejecutarse de verdad y destapo un defecto de
FISICA, no de codigo: para una pintura intumescente acrilica de 1,8 mm sobre un
IPE 300 con Am/V = 200 1/m el modulo devolvia

    theta_protected = 916,7 C   frente a   theta_crit = 540,0 C

es decir, "la pintura no protege nada". El numero no es un resultado: es la
consecuencia de meter la propiedad equivocada en el modelo equivocado.

  - §4.2.5.2 modela una CAPA INERTE de espesor ``dp`` y conductividad
    ``lambda_p`` constantes.
  - Una pintura intumescente es un recubrimiento REACTIVO: se expande entre 20 y
    50 veces al calentarse y su conductividad efectiva cambia con la
    temperatura. El ``lambda_p`` del catalogo es el de la PELICULA SECA, sin
    expandir; no es la conductividad de la espuma que realmente aisla.
  - En la practica las intumescentes no se especifican por conductividad sino
    por ESPESOR CERTIFICADO DE ENSAYO (UL 263 / EN 13381-8) para un factor de
    seccion Am/V y una clasificacion (R30/R60/R90/R120) dados.

Un 916,7 C es tan fabricado como lo seria un 400 C: el veredicto "no cumple"
que se deducia de el no esta mas justificado que un "cumple". La ausencia de un
metodo de verificacion aplicable se propaga como ausencia.

Este fichero fija tres cosas:
  1. Que la temperatura protegida de un recubrimiento reactivo es ``None`` y su
     veredicto ``NO_VERIFICADO`` mientras no haya dato certificado.
  2. Que la comparacion de clasificaciones certificadas (la via correcta) es
     NUMERICA y no lexicografica.
  3. Que los recubrimientos de capa inerte (mortero, placa, hormigon) siguen
     verificandose con §4.2.5.2, con ``is_safe`` True y False alcanzables.
"""
from __future__ import annotations

import pytest

from firesteeljm import protection_catalog
from firesteeljm.en_steel_temperature import (
    STATUS_CON_PROTECCION_CUMPLE,
    STATUS_CON_PROTECCION_NO_CUMPLE,
    STATUS_NO_VERIFICADO,
    check_fire_resistance_from_profile,
    rating_covers,
)
from firesteeljm.protection_catalog import (
    METHOD_CERTIFIED_TEST,
    METHOD_INERT_LAYER,
    CertifiedRating,
    FireProtection,
)


# ---------------------------------------------------------------------------
# 1. El catalogo distingue el metodo de verificacion aplicable
# ---------------------------------------------------------------------------

def test_catalogo_declara_metodo_de_verificacion_por_producto():
    """Cada producto declara con que metodo se puede verificar.

    Reactivo (intumescente) -> ensayo certificado; el resto -> capa inerte
    §4.2.5.2.
    """
    for p in protection_catalog.CATALOG:
        if p.type == "intumescent":
            assert p.design_method == METHOD_CERTIFIED_TEST, p.code
        else:
            assert p.design_method == METHOD_INERT_LAYER, p.code


def test_catalogo_intumescente_no_declara_lambda_p_de_pelicula_seca():
    """Un lambda_p que no sirve para §4.2.5.2 no se publica como si sirviera.

    El dato de pelicula seca existe en las fichas de producto, pero introducido
    en §4.2.5.2 produce el 916,7 C que motiva este fichero. Se propaga como
    ausencia (``None``) para que cualquier uso accidental falle en vez de
    devolver un numero.
    """
    for p in protection_catalog.CATALOG:
        if p.design_method == METHOD_CERTIFIED_TEST:
            assert p.lambda_p_W_per_mK is None, p.code
        else:
            assert isinstance(p.lambda_p_W_per_mK, float), p.code
            assert p.lambda_p_W_per_mK > 0.0, p.code


def test_catalogo_no_trae_datos_de_ensayo_certificados():
    """El catalogo distribuido NO incluye tablas de ensayo.

    No se dispone de ninguna tabla UL 263 / EN 13381-8 de fuente citable. Poner
    espesores certificados inventados seria peor que el defecto que se corrige:
    aparentaria autoridad de ensayo. Se distribuye vacio y el chequeo se niega.
    """
    for p in protection_catalog.CATALOG:
        if p.design_method == METHOD_CERTIFIED_TEST:
            assert p.certified_ratings == (), p.code


# ---------------------------------------------------------------------------
# 2. El caso que destapo todo
# ---------------------------------------------------------------------------

def test_intumescente_sin_dato_certificado_no_devuelve_temperatura():
    """CASO ORIGEN: IPE 300, Am/V = 200 1/m, mu_0 = 0,65, R60, intumescente.

    Sin dato certificado no hay metodo de verificacion aplicable: la temperatura
    protegida es ``None``, ``is_safe`` es ``None`` y el estado NO_VERIFICADO.
    En particular NO puede aparecer el 916,7 C de §4.2.5.2, que no es aplicable
    a un recubrimiento reactivo.
    """
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        load_ratio_mu0=0.65,
        required_rating="R60",
        preferred_protection_type="intumescent",
    )
    assert res.requires_protection is True
    assert res.theta_unprotected_C > res.theta_crit_C
    assert res.theta_protected_C is None
    assert res.is_safe is None
    assert res.verification_status == STATUS_NO_VERIFICADO
    assert res.recommended_protection is None
    texto = " ".join(res.notes).lower()
    assert "certificado" in texto
    assert "4.2.5.2" in texto


def test_intumescente_to_dict_no_publica_temperatura_protegida():
    d = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        required_rating="R60",
        preferred_protection_type="intumescent",
    ).to_dict()
    assert d["theta_protected_C"] is None
    assert d["is_safe"] is None
    assert d["verification_status"] == "NO_VERIFICADO"


# ---------------------------------------------------------------------------
# 3. Orden de las clasificaciones EN 13501-2 (comparacion NUMERICA)
# ---------------------------------------------------------------------------

def test_golden_orden_clasificaciones_r90_r120_no_es_lexicografico():
    """GOLDEN. El par que discrimina orden numerico de orden de cadenas.

    EN 13501-2: el numero de la clase ES la duracion normalizada en minutos, de
    modo que R120 (120 min) cubre estrictamente mas que R90 (90 min).
    Como CADENAS, en cambio, ``"R120" < "R90"`` porque ``'1' < '9'``: una
    comparacion lexicografica invierte exactamente este par y solo este orden de
    magnitud (R30/R60/R90 si ordenan bien como texto).

    Valores aseverados, derivados de la definicion de la norma:
      cubre("R120", "R90")  -> True   (120 >= 90)
      cubre("R90",  "R120") -> False  ( 90 <  120)
    """
    assert rating_covers("R120", "R90") is True
    assert rating_covers("R90", "R120") is False
    # El fallo lexicografico que este par caza:
    assert ("R120" >= "R90") is False


@pytest.mark.parametrize(
    "certificada, requerida, cubre",
    [
        ("R60", "R60", True),     # igualdad: 60 >= 60
        ("R90", "R60", True),     # 90 >= 60
        ("R60", "R90", False),    # 60 < 90
        ("R120", "R30", True),    # 120 >= 30
        ("R30", "R120", False),   # 30 < 120
        ("R120", "R120", True),   # igualdad en el extremo
        ("REI120", "R90", True),  # {R,E,I} incluye {R} y 120 >= 90
        ("R120", "EI90", False),  # {R} NO incluye {E,I}: 120 >= 90 no basta
        ("REI90", "EI90", True),  # {R,E,I} incluye {E,I} y 90 >= 90
        ("EI120", "REI30", False),  # {E,I} no acredita capacidad portante R
    ],
)
def test_golden_cobertura_de_clasificaciones(certificada, requerida, cubre):
    """GOLDEN. cubre(c, r) <=> letras(c) ⊇ letras(r) Y minutos(c) >= minutos(r).

    EN 13501-2: el numero de la clasificacion es la duracion normalizada en
    minutos (de ahi ``parse_fire_rating_minutes``, ya verificado), y las letras
    son prestaciones distintas que se ensayan por separado -- R (capacidad
    portante), E (integridad), I (aislamiento). Cubrir exige las dos cosas.
    Cada caso de la tabla lleva su comparacion escrita al lado.
    """
    assert rating_covers(certificada, requerida) is cubre


def test_golden_r_no_acredita_integridad_ni_aislamiento():
    """GOLDEN. R120 NO cubre EI90 aunque 120 >= 90.

    R, E e I son prestaciones separadas de EN 13501-2 y se ensayan por separado:
    una clasificacion R120 acredita capacidad portante durante 120 min y no dice
    nada de integridad ni de aislamiento. Comparar solo los minutos daria aqui
    un "cumple" fabricado.

    Valores aseverados:
      cubre("R120", "EI90")   -> False  ({R} no incluye {E,I})
      cubre("REI90", "EI90")  -> True   ({R,E,I} incluye {E,I} y 90 >= 90)
    """
    assert rating_covers("R120", "EI90") is False
    assert rating_covers("REI90", "EI90") is True
    # Lo que el guardian de letras caza: la comparacion de minutos por si sola
    # diria que si.
    from firesteeljm.en_steel_temperature import parse_fire_rating_minutes
    assert parse_fire_rating_minutes("R120") >= parse_fire_rating_minutes("EI90")


def test_rating_covers_rechaza_cadenas_ininteligibles():
    """Una clasificacion no interpretable ABORTA; no se degrada a un default."""
    with pytest.raises(ValueError):
        rating_covers("sesenta", "R60")
    with pytest.raises(ValueError):
        rating_covers("R60", "noventa")


# ---------------------------------------------------------------------------
# 4. La via certificada, ejercitada con un producto de PRUEBA
# ---------------------------------------------------------------------------
#
# Los datos de ensayo de abajo NO son datos de producto: son un fixture de test
# con valores redondos elegidos a mano. No estan en el catalogo distribuido y no
# valen para proyecto. Su unico proposito es ejercitar la logica de cobertura.

_FIXTURE_R60 = FireProtection(
    code="TEST-FIXTURE-INT",
    type="intumescent",
    lambda_p_W_per_mK=None,
    rho_p_kg_m3=1300.0,
    c_p_J_per_kgK=900.0,
    typical_thickness_mm=(0.6, 3.0),
    cost_USD_per_m2=45.0,
    rating_minutes=60,
    design_method=METHOD_CERTIFIED_TEST,
    certified_ratings=(
        CertifiedRating(
            Am_V_max_1_m=250.0,
            thickness_mm=1.8,
            rating="R60",
            source="FIXTURE DE TEST - NO son datos de ensayo, no valen para proyecto",
        ),
    ),
)


@pytest.fixture()
def catalogo_con_fixture(monkeypatch):
    # Se sustituyen los intumescentes del catalogo por el fixture para que la
    # seleccion sea determinista (``recommend`` ordena por coste).
    monkeypatch.setattr(
        protection_catalog, "CATALOG",
        [p for p in protection_catalog.CATALOG if p.type != "intumescent"]
        + [_FIXTURE_R60],
    )
    return _FIXTURE_R60


def test_certificado_que_cubre_el_requisito_da_veredicto_sin_temperatura(
    catalogo_con_fixture,
):
    """Con dato certificado que cubre R60 a Am/V = 200 <= 250: CUMPLE.

    El veredicto sale de la comparacion de clasificaciones (R60 certificada
    cubre R60 requerida), no de una temperatura: ``theta_protected_C`` sigue
    siendo ``None`` porque no se calcula ninguna.
    """
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        load_ratio_mu0=0.65,
        required_rating="R60",
        preferred_protection_type="intumescent",
    )
    assert res.is_safe is True
    assert res.verification_status == STATUS_CON_PROTECCION_CUMPLE
    assert res.theta_protected_C is None
    assert res.recommended_protection is not None
    assert res.recommended_protection["thickness_mm"] == 1.8
    assert res.recommended_protection["certified_rating"] == "R60"
    assert "FIXTURE" in res.recommended_protection["certified_source"]


def test_certificado_que_no_alcanza_el_requisito_no_verifica(catalogo_con_fixture):
    """R90 requerido contra un producto certificado solo a R60: sin veredicto.

    No se degrada a "no cumple" por calculo: simplemente no hay ensayo que
    cubra R90 para este producto.
    """
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        required_rating="R90",
        preferred_protection_type="intumescent",
    )
    assert res.is_safe is None
    assert res.verification_status == STATUS_NO_VERIFICADO
    assert res.theta_protected_C is None


def test_certificado_fuera_del_rango_de_factor_de_seccion_no_verifica(
    catalogo_con_fixture,
):
    """El ensayo cubre hasta Am/V = 250 1/m; a 300 1/m no es extrapolable."""
    res = check_fire_resistance_from_profile(
        section_name="perfil esbelto",
        Am_V_m_inv=300.0,
        required_rating="R60",
        preferred_protection_type="intumescent",
    )
    assert res.is_safe is None
    assert res.verification_status == STATUS_NO_VERIFICADO


# ---------------------------------------------------------------------------
# 5. La capa inerte NO se toca
# ---------------------------------------------------------------------------

def test_capa_inerte_mortero_sigue_cumpliendo_por_calculo():
    """REGRESION. El mortero proyectado a 25 mm sigue verificandose por §4.2.5.2.

    Es un aislante de espesor y conductividad constantes: el modelo aplica. El
    veredicto sale de theta_protegida <= theta_crit y debe seguir siendo
    alcanzable ``True``. (El valor concreto de theta esta caracterizado en
    ``test_caracterizacion_mortero_25mm_60min``.)
    """
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        load_ratio_mu0=0.65,
        required_rating="R60",
        preferred_protection_type="spray_mortar",
    )
    assert res.recommended_protection["type"] == "spray_mortar"
    assert res.theta_protected_C is not None
    assert res.theta_protected_C < res.theta_crit_C
    assert res.is_safe is True
    assert res.verification_status == STATUS_CON_PROTECCION_CUMPLE


def test_caracterizacion_mortero_25mm_60min():
    """CARACTERIZACION (no golden): valor capturado del integrador del modulo.

    UL 60-spray-mortar, espesor medio (15+35)/2 = 25 mm, Am/V = 200 1/m,
    60 min ISO 834, dt = 5 s -> 416,3 C. No procede de fuente citada: fija el
    integrador §4.2.5.2 frente a cambios accidentales.
    """
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        load_ratio_mu0=0.65,
        required_rating="R60",
        preferred_protection_type="spray_mortar",
    )
    assert res.recommended_protection["thickness_mm"] == 25.0
    assert res.theta_protected_C == pytest.approx(416.3, abs=0.1)


def test_capa_inerte_placa_insuficiente_sigue_dando_no_cumple():
    """``is_safe=False`` sigue siendo alcanzable por calculo de capa inerte.

    EN 90-board-cem a espesor medio (12,5+25)/2 = 18,75 mm sobre Am/V = 200 1/m
    a 90 min no baja de la temperatura critica. El veredicto negativo por
    §4.2.5.2 sigue existiendo: el cambio no convierte todo en NO_VERIFICADO.
    """
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        load_ratio_mu0=0.65,
        required_rating="R90",
        preferred_protection_type="board",
    )
    assert res.theta_protected_C is not None
    assert res.theta_protected_C > res.theta_crit_C
    assert res.is_safe is False
    assert res.verification_status == STATUS_CON_PROTECCION_NO_CUMPLE
