"""Tests de regresion para defectos reales de ``steelfire.en_steel_temperature``.

Cubre cuatro defectos localizados y reproducidos:

D1 - ``is_safe`` se derivaba de la EXISTENCIA de una entrada de catalogo
     (``not requires_prot or prot_info is not None``), no de una comparacion
     termica. Devolvia ``True`` con theta_unprot = 941 C y theta_crit = 540 C.
D2 - el requisito de fuego caia a 60 min por defecto cuando la cadena no se
     podia parsear ("REI90" -> 60 min, del lado inseguro y en silencio).
D3 - ``max(term, 1e-9)`` producia temperaturas criticas negativas fuera del
     dominio de mu_0.
D4 - ``... or candidates`` devolvia una proteccion de OTRO tipo cuando no habia
     ninguna del tipo solicitado.

Todos los valores aseverados se derivan de EN 1993-1-2 en forma cerrada (D3) o
por construccion desde el propio integrador §4.2.5.2 del modulo con las
propiedades declaradas en ``protection_catalog`` (D1). No hay ningun valor
capturado de la implementacion.
"""
from __future__ import annotations

import math

import pytest

from steelfire import protection_catalog
from steelfire.en_steel_temperature import (
    ProtectedSteel,
    UnprotectedSteel,
    check_fire_resistance_from_profile,
    critical_temperature,
    steel_temperature_at,
)


# ---------------------------------------------------------------------------
# D3 - dominio de mu_0 y temperatura critica negativa
# ---------------------------------------------------------------------------

def test_d3_critical_temperature_fuera_de_dominio_aborta():
    """mu_0 > 1 esta fuera del dominio de EN 1993-1-2 §4.2.4 y debe abortar.

    Eq. 4.22: theta_cr = 39.19 * ln(1/(0.9674 * mu_0^3.833) - 1) + 482.
    El argumento del logaritmo, 1/(0.9674 * mu_0^3.833) - 1, se anula en
    mu_0 = 0.9674^(-1/3.833) = 1.00874 y es NEGATIVO por encima. Para
    mu_0 = 1.03 el argumento vale -0.0770: no existe theta_cr real.
    El grado de utilizacion es un cociente E_fi,d / R_fi,d,0 y no puede exceder
    1.0 (§4.2.4), asi que 1.03 debe rechazarse indicando el valor recibido.
    """
    with pytest.raises(ValueError) as exc:
        critical_temperature(1.03)
    assert "1.03" in str(exc.value)


def test_d3_critical_temperature_en_el_borde_mu0_igual_1():
    """mu_0 = 1.0 es el borde superior del dominio y tiene solucion cerrada.

    theta_cr = 39.19 * ln(1/0.9674 - 1) + 482
             = 39.19 * ln(0.03369857...) + 482
             = 39.19 * (-3.389766...) + 482 = 349.134 C
    """
    esperado = 39.19 * math.log(1.0 / 0.9674 - 1.0) + 482.0
    assert esperado == pytest.approx(349.134, abs=1e-3)
    assert critical_temperature(1.0) == pytest.approx(esperado, rel=1e-12)


def test_d3_critical_temperature_nunca_negativa_en_el_dominio():
    """En todo el dominio (0, 1] la temperatura critica es positiva y decreciente."""
    mus = [0.05, 0.2, 0.4, 0.65, 0.8, 1.0]
    temps = [critical_temperature(m) for m in mus]
    assert all(t > 0.0 for t in temps), temps
    assert temps == sorted(temps, reverse=True)


# ---------------------------------------------------------------------------
# D2 - parseo del requisito de fuego
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rating, minutos",
    [
        ("R60", 60.0),
        ("R 90", 90.0),
        ("REI90", 90.0),
        ("REI 90", 90.0),
        ("REI-90", 90.0),
        ("rei120", 120.0),
        ("EI30", 30.0),
        ("RE 45", 45.0),
        ("R15", 15.0),
        ("EI 240", 240.0),
    ],
)
def test_d2_parse_fire_rating(rating: str, minutos: float):
    """Clasificacion EN 13501-2: letras de prestacion (R/E/I/W/M/C/S) + minutos.

    El numero de la clase ES la duracion en minutos por definicion de la norma,
    de modo que "REI90" son 90 minutos, no 60.
    """
    from steelfire.en_steel_temperature import parse_fire_rating_minutes

    assert parse_fire_rating_minutes(rating) == minutos


@pytest.mark.parametrize("rating", ["", "R", "sesenta", "R60X", "R-0", "60R", "XY90"])
def test_d2_parse_fire_rating_invalido_aborta(rating: str):
    """Una cadena no interpretable ABORTA; nunca cae a un valor por defecto."""
    from steelfire.en_steel_temperature import parse_fire_rating_minutes

    with pytest.raises(ValueError) as exc:
        parse_fire_rating_minutes(rating)
    msg = str(exc.value)
    assert repr(rating) in msg or rating in msg
    assert "REI" in msg  # el mensaje enumera los formatos aceptados


def test_d2_rei90_se_evalua_a_90_minutos():
    """DEFECTO: 'REI90' se comprobaba a 60 min (requisito degradado en silencio)."""
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        load_ratio_mu0=0.65,
        required_rating="REI90",
        preferred_protection_type="spray_mortar",
    )
    assert res.duration_min == 90.0


def test_d2_requisito_ininteligible_aborta_el_chequeo():
    """Un requisito que no se entiende no puede convertirse en 60 min."""
    with pytest.raises(ValueError):
        check_fire_resistance_from_profile(
            section_name="IPE 300",
            Am_V_m_inv=200.0,
            required_rating="sesenta minutos",
        )


# ---------------------------------------------------------------------------
# D1 - veredicto de seguridad por comparacion termica real
# ---------------------------------------------------------------------------

def test_d1_veredicto_invertido_reproduccion_minima():
    """DEFECTO EXACTO: is_safe=True con theta_unprot=941 C frente a theta_crit=540 C.

    Reproduccion sin depender de campos nuevos: ningun veredicto de seguridad
    puede ser True si el unico calculo termico realizado (sin proteger) supera la
    temperatura critica y no se ha evaluado ninguna proteccion.
    """
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        load_ratio_mu0=0.65,
        required_rating="R60",
        preferred_protection_type="intumescent",
    )
    assert res.theta_unprotected_C > res.theta_crit_C
    assert res.is_safe is not True


def test_d1_is_safe_no_puede_ser_true_con_proteccion_insuficiente():
    """DEFECTO: devolvia is_safe=True con theta_unprot=941 C y theta_crit=540 C.

    Comprobacion cerrada: la temperatura protegida se recalcula aqui con el
    integrador §4.2.5.2 del propio modulo, alimentado con las propiedades
    declaradas en ``protection_catalog`` y con el espesor que el resultado dice
    haber propuesto. El veredicto debe ser exactamente
    theta_protegida <= theta_crit.

    El caso se plantea sobre una PLACA (capa inerte), no sobre una pintura
    intumescente: §4.2.5.2 solo aplica a un aislante de espesor y conductividad
    constantes. Para el recubrimiento reactivo, que ya no produce ninguna
    temperatura, ver D5 en ``test_reactive_coating_certified.py``.
    """
    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        load_ratio_mu0=0.65,
        required_rating="R90",
        preferred_protection_type="board",
    )

    # Punto de partida del defecto: sin proteger se superan con creces los 540 C.
    assert res.theta_unprotected_C > 900.0
    assert res.theta_crit_C == pytest.approx(539.96, abs=0.05)
    assert res.requires_protection is True

    # La proteccion propuesta se EVALUA, no se presupone.
    assert res.recommended_protection is not None
    prot = protection_catalog.lookup(res.recommended_protection["code"])
    assert prot is not None
    esperada = steel_temperature_at(
        ProtectedSteel(
            Am_V_1_m=200.0,
            dp_m=res.recommended_protection["thickness_mm"] / 1000.0,
            lambda_p=prot.lambda_p_W_per_mK,
            cp=prot.c_p_J_per_kgK,
            rho_p=prot.rho_p_kg_m3,
        ),
        duration_min=90.0,
    )
    assert res.theta_protected_C == pytest.approx(esperada, rel=1e-9)

    # La placa al espesor medio de su rango tipico no baja de 540 C a 90 min:
    # el veredicto honesto es NO seguro, y sale de la comparacion termica.
    assert esperada > res.theta_crit_C
    assert res.is_safe is False


def test_d1_is_safe_true_solo_cuando_la_proteccion_enfria_por_debajo_de_theta_crit():
    """Contraparte positiva: mortero proyectado 25 mm SI cumple a 60 min.

    Verificado por la misma comparacion cerrada theta_protegida <= theta_crit.
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


def test_d1_sin_proteccion_necesaria_is_safe_sale_de_la_comparacion():
    """Perfil masivo (Am/V bajo): no requiere proteccion y is_safe sale de theta_unprot."""
    res = check_fire_resistance_from_profile(
        section_name="masivo",
        Am_V_m_inv=10.0,
        load_ratio_mu0=0.65,
        required_rating="R30",
    )
    assert res.requires_protection is False
    assert res.theta_unprotected_C < res.theta_crit_C
    assert res.is_safe is True


def test_d1_to_dict_expone_el_estado_de_verificacion():
    """El lector de ``to_dict`` debe ver el veredicto y su estado, no solo un bool."""
    d = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        required_rating="R90",
        preferred_protection_type="board",
    ).to_dict()
    assert d["is_safe"] is False
    assert d["theta_protected_C"] is not None
    assert d["verification_status"] in {
        "SIN_PROTECCION_CUMPLE",
        "CON_PROTECCION_CUMPLE",
        "CON_PROTECCION_NO_CUMPLE",
        "NO_VERIFICADO",
    }


# ---------------------------------------------------------------------------
# D4 - el tipo de proteccion solicitado no puede sustituirse en silencio
# ---------------------------------------------------------------------------

def test_d4_no_sustituye_el_tipo_de_proteccion_pedido():
    """DEFECTO: sin candidatos del tipo pedido devolvia otro material como si lo fuera.

    ``recommend(90)`` filtra ``rating_minutes >= 90``, lo que deja fuera el unico
    ``spray_mortar`` del catalogo (rating 60). El ``or candidates`` devolvia
    entonces "Concrete-R180" (type="concrete"), el mas barato, presentado como la
    proteccion recomendada aunque se pidio mortero proyectado.
    """
    assert not [
        p for p in protection_catalog.recommend(90) if "spray_mortar" in p.type
    ]

    res = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        required_rating="R90",
        preferred_protection_type="spray_mortar",
    )

    if res.recommended_protection is not None:
        assert res.recommended_protection["type"] == "spray_mortar"
    else:
        # Ausencia propagada como ausencia: sin veredicto y con estado explicito.
        assert res.is_safe is None
        assert res.verification_status == "NO_VERIFICADO"
        assert "concrete" in res.available_protection_types


def test_d4_to_dict_declara_que_no_hay_proteccion_del_tipo_pedido():
    d = check_fire_resistance_from_profile(
        section_name="IPE 300",
        Am_V_m_inv=200.0,
        required_rating="R90",
        preferred_protection_type="spray_mortar",
    ).to_dict()
    assert d["is_safe"] is None
    assert d["verification_status"] == "NO_VERIFICADO"
    assert d["recommended_protection"] is None
    assert d["available_protection_types"]
