"""Tests retention factors multi-código."""
import pytest

from steelfire.retention_multi import retention_factor


def test_20C_es_1_en_todos():
    for c in ("EU", "SG", "US", "CO", "AU"):
        assert retention_factor(20, "E", c) == 1.0
        assert retention_factor(20, "Fy", c) == 1.0


def test_eu_500C():
    assert retention_factor(500, "E", "EU") == pytest.approx(0.60)
    assert retention_factor(500, "Fy", "EU") == pytest.approx(0.78)


def test_us_sigue_la_tabla_A_4_2_1_de_AISC():
    """AISC 360-16/22 Tabla A-4.2.1 (nodos en F): 750 F = 399 C -> k_E = 0.70,
    k_p = 0.420, k_y = 1.00; 1000 F = 538 C -> 0.49 / 0.180 / 0.66;
    1200 F = 649 C -> 0.22 / 0.075 / 0.35. Son los valores de EN 1993-1-2
    Tabla 3.1 adoptados por AISC, de modo que US y EU difieren solo por el
    redondeo y la posicion de los nodos (< 0.02).

    La version anterior usaba una cuadratica sin fuente que daba k_E = 0 a
    400 C (la tabla da 0.70): este test la impide volver.
    """
    assert retention_factor(399, "E", "US") == pytest.approx(0.70, abs=1e-9)
    assert retention_factor(399, "kp", "US") == pytest.approx(0.420, abs=1e-9)
    assert retention_factor(538, "E", "US") == pytest.approx(0.49, abs=1e-9)
    assert retention_factor(538, "Fy", "US") == pytest.approx(0.66, abs=1e-9)
    assert retention_factor(649, "Fy", "US") == pytest.approx(0.35, abs=1e-9)
    # En los nodos de la tabla AISC los valores son los de EN interpolados
    # (redondeados a dos decimales); entre nodos las dos tablas difieren
    # porque sus nodos no coinciden (p. ej. 0.552 frente a 0.600 a 500 C).
    for T in (204, 316, 399, 427, 538, 649, 760):
        for q in ("E", "Fy"):
            assert abs(retention_factor(T, q, "US") - retention_factor(T, q, "EU")) < 0.015, (T, q)
    # k_p: AISC asigna a cada nodo en F el valor EC3 del nodo en C anterior
    # (600 F = 316 C -> 0.613, que EN da a 300 C; 800 F = 427 C -> 0.360, que
    # EN da a 500 C), asi que k_p en US queda por debajo de EU entre 300 y
    # 500 C hasta en 0.044. No se exige cercania: se exigen los literales de
    # la tabla y la monotonia.
    assert retention_factor(316.0, "kp", "US") == pytest.approx(0.613, abs=1e-9)
    assert retention_factor(427.0, "kp", "US") == pytest.approx(0.360, abs=1e-9)
    assert retention_factor(538.0, "kp", "US") == pytest.approx(0.180, abs=1e-9)
    kps = [retention_factor(T, "kp", "US") for T in range(20, 1201, 10)]
    assert all(a >= b for a, b in zip(kps, kps[1:]))
    assert retention_factor(400, "E", "US") > 0.69  # antes: 0.0


def test_T_alto_va_a_cero():
    for c in ("EU", "US", "AU"):
        assert retention_factor(1200, "E", c) <= 0.05


# ---------------------------------------------------------------------------
# GOLDEN — retention_multi.py duplica la Tabla 3.1 de thermal_iter.py en sus
# propios arrays (_EN_ky/_EN_kE). Se replican aqui los mismos anclajes
# interpolados de W01409/W01411 (ver tests/test_thermal_iter.py) para que una
# edicion accidental de ESTA copia de la tabla tambien falle en rojo.
# Oraculo independiente: interpolacion lineal manual de Tabla 3.1 EN 1993-1-2,
# no reimportada del modulo.
# ---------------------------------------------------------------------------

def test_golden_w01409_ky_eu_595_5C():
    """W01409 (viga IPE550/S235): eta_fi=k_y,theta=0.4840 -> Ta=595.5C.

    ky(595.5) = 0.780 - 0.31*(595.5-500)/100 = 0.48395 (Tabla 3.1, EU).
    """
    assert retention_factor(595.5, "Fy", "EU") == pytest.approx(0.48395, abs=1e-4)


def test_golden_w01411_ky_kE_eu_567_8C():
    """W01411 (pilar HEB, pandeo en fuego): Ta_crit=567.8C.

    ky(567.8) = 0.780 - 0.31*(567.8-500)/100 = 0.56982 (coincide con ficha).
    kE(567.8) = 0.600 - 0.29*(567.8-500)/100 = 0.40338 (ficha cita 0.4004,
    ERRATA de ~0.003 -- se ancla el valor recalculado, ver test_thermal_iter.py).
    """
    assert retention_factor(567.8, "Fy", "EU") == pytest.approx(0.56982, abs=1e-4)
    assert retention_factor(567.8, "E", "EU") == pytest.approx(0.40338, abs=1e-4)


# ---------------------------------------------------------------------------
# GOLDEN — EN 1993-1-2:2005 §3.2.1, TABLA 3.1
# "Reduction factors for stress-strain relationship of carbon steel at
#  elevated temperatures", columnas ky,theta / kp,theta / kE,theta.
#
# Es una tabla PUBLICADA: los valores son EXACTOS en los nodos de 100 C, no
# aproximaciones. Se anclan como literales transcritos de la norma (no leidos
# de los arrays del modulo) en las cinco temperaturas 400/500/600/700/800.
#
#   theta [C]   ky,theta   kp,theta   kE,theta
#      400        1.000      0.420      0.700
#      500        0.780      0.360      0.600
#      600        0.470      0.180      0.310
#      700        0.230      0.075      0.130
#      800        0.110      0.050      0.090
#
# kp,theta NO ES ACCESIBLE desde ``retention_factor``: el parametro
# ``quantity`` solo admite "E" o "Fy". Ver
# ``test_defecto_kp_no_implementado_fallback_silencioso`` mas abajo.
# La cobertura golden de kp,theta (los 13 nodos de la Tabla 3.1) vive sobre
# ``steelfire.thermal_iter.k_p`` en tests/test_thermal_iter.py
# (``test_golden_tabla_3_1_kp``); aqui solo se documenta la ausencia.
# ---------------------------------------------------------------------------

_TABLA_3_1_EN1993_1_2 = [
    # (theta_C, ky_theta, kp_theta, kE_theta)
    (400.0, 1.000, 0.420, 0.700),
    (500.0, 0.780, 0.360, 0.600),
    (600.0, 0.470, 0.180, 0.310),
    (700.0, 0.230, 0.075, 0.130),
    (800.0, 0.110, 0.050, 0.090),
]


@pytest.mark.parametrize("theta_C, ky_ref, kp_ref, kE_ref",
                          _TABLA_3_1_EN1993_1_2)
def test_golden_tabla_3_1_ky_kE_400_500_600_700_800(theta_C, ky_ref, kp_ref,
                                                     kE_ref):
    """EN 1993-1-2 §3.2.1 Tabla 3.1 — ky,theta y kE,theta EXACTOS en los nodos
    400 / 500 / 600 / 700 / 800 C, via ``retention_factor(..., code="EU")``.

    Exactitud BIT-A-BIT verificada (no solo dentro de tolerancia): el modulo
    devuelve 1.0 / 0.78 / 0.47 / 0.23 / 0.11 para ky,theta y
    0.7 / 0.6 / 0.31 / 0.13 / 0.09 para kE,theta, identicos al literal de la
    norma bajo ``==`` exacto. La tolerancia abs=1e-9 solo cubre el ruido de
    np.interp en los extremos del array.

    kp_ref viaja en la parametrizacion (valor normativo de la misma fila de la
    tabla) pero NO se asevera aqui contra ningun valor calculado, porque
    ``retention_factor`` no expone kp,theta: ese hueco se documenta en
    ``test_defecto_kp_no_implementado_fallback_silencioso``, y la cobertura
    golden de kp,theta vive sobre ``thermal_iter.k_p``.
    """
    # Igualdad EXACTA, no aproximada: son nodos tabulados de la norma.
    assert retention_factor(theta_C, "Fy", "EU") == ky_ref
    assert retention_factor(theta_C, "E", "EU") == kE_ref


@pytest.mark.parametrize("theta_C, ky_ref, kp_ref, kE_ref",
                          _TABLA_3_1_EN1993_1_2)
def test_golden_tabla_3_1_codigo_SG_identico_a_EU(theta_C, ky_ref, kp_ref,
                                                   kE_ref):
    """El codigo "SG" (Singapur) adopta EN 1993-1-2 sin cambios en la Tabla
    3.1, y el modulo lo enruta a la misma tabla. Mismos valores normativos.
    """
    assert retention_factor(theta_C, "Fy", "SG") == pytest.approx(ky_ref,
                                                                  abs=1e-9)
    assert retention_factor(theta_C, "E", "SG") == pytest.approx(kE_ref,
                                                                 abs=1e-9)


def test_golden_tabla_3_1_kp_theta():
    """GOLDEN - kp,theta (limite de proporcionalidad) de EN 1993-1-2 Tabla 3.1.

    Fuente: EN 1993-1-2:2005 §3.2.1, Tabla 3.1, columna kp,theta.
    Valores tabulados (exactos, no aproximados): 400 C -> 0.420,
    500 C -> 0.360, 600 C -> 0.180, 700 C -> 0.075, 800 C -> 0.050.

    Historia de este test: documentaba un DEFECTO. `retention_factor` hacia
    `table = _EN_kE if quantity == "E" else _EN_ky`, asi que cualquier
    quantity distinta de "E" caia en k_y sin avisar: pedir "kp" a 400 C
    devolvia 1.000 en vez de 0.420, un factor 2.38 de sobreestimacion del
    limite de proporcionalidad. Corregido: la tabla kp se reutiliza de
    `thermal_iter._K_P` (fuente unica) y el mapa de magnitudes es explicito.
    """
    kp_norma = {400.0: 0.420, 500.0: 0.360, 600.0: 0.180, 700.0: 0.075,
                800.0: 0.050}
    for theta_C, kp_ref in kp_norma.items():
        # Igualdad EXACTA: son nodos tabulados de la norma, no aproximaciones.
        assert retention_factor(theta_C, "kp", "EU") == kp_ref, \
            f"kp,theta a {theta_C} C"


def test_magnitud_desconocida_lanza_en_vez_de_devolver_otra():
    """Un factor de seguridad de material no puede salir de un `else` por defecto.

    Antes, un typo de mayusculas devolvia la magnitud EQUIVOCADA en silencio:
    `retention_factor(500, "e")` daba 0.78 (k_y) en vez de 0.60 (k_E). Ahora
    cada magnitud no soportada aborta, que es la unica respuesta segura.
    """
    for magnitud in ("e", "ky", "kP", "Fu", ""):
        with pytest.raises(ValueError, match="no soportada"):
            retention_factor(500.0, magnitud, "EU")  # type: ignore[arg-type]

    # Y las magnitudes validas siguen devolviendo lo suyo, no la de al lado.
    assert retention_factor(500.0, "E", "EU") == pytest.approx(0.60, abs=1e-9)
    assert retention_factor(500.0, "Fy", "EU") == pytest.approx(0.78, abs=1e-9)


def test_kp_en_US_es_el_de_la_tabla_A_4_2_1_no_k_y_disfrazado():
    """AISC 360 Tabla A-4.2.1 SI tabula k_p = F_p(T)/F_y. Un k_p que coincidiera
    con k_y seria la sustitucion silenciosa que esta campana persigue; aqui se
    exige que k_p difiera de k_y donde la tabla lo hace (300-500 C) y que
    coincida con el valor tabulado.
    """
    assert retention_factor(316.0, "kp", "US") == pytest.approx(0.613, abs=1e-9)
    assert retention_factor(316.0, "kp", "US") < retention_factor(316.0, "Fy", "US")
    assert retention_factor(427.0, "kp", "US") == pytest.approx(0.360, abs=1e-9)


def test_defecto_AU_enrutado_a_tabla_EN_sin_ajustes():
    """DEFECTO VIVO - "AU" es hoy un alias exacto de "EU", sin AS 4100.

    El docstring del modulo anuncia:

        AU:     AS 4100 Tabla 12.1 (basado en EN con ajustes)

    pero el codigo hace `if code in ("EU", "SG", "AU")` y enruta las tres a la
    MISMA tabla EN, sin ajuste alguno. AS 4100 Tabla 12.1 difiere de EN
    1993-1-2 Tabla 3.1 justamente por debajo de 400 C, que es donde este test
    demuestra que no hay diferencia: no hay implementacion de AS 4100.

    Este test se conserva DELIBERADAMENTE en rojo-conceptual (pasa, pero lo que
    asevera es la ausencia): si alguien implementa AS 4100 de verdad, empezara
    a fallar y habra que reescribirlo como golden de esa norma. Es la unica
    constancia por escrito de la discrepancia entre el docstring y el codigo.

    CLASIFICACION: caracterizacion. Compara la implementacion consigo misma
    para dejar constancia de una equivalencia que la documentacion niega.
    """
    for theta_C in (100.0, 200.0, 300.0, 350.0, 400.0, 500.0, 600.0):
        for magnitud in ("Fy", "E", "kp"):
            assert retention_factor(theta_C, magnitud, "AU") == (
                retention_factor(theta_C, magnitud, "EU")
            ), f"AU deberia diferir de EU a {theta_C} C para {magnitud}"


# Marcado tras el cuerpo para no repetir el import de pytest en la cabecera.
test_defecto_AU_enrutado_a_tabla_EN_sin_ajustes = pytest.mark.characterization(
    test_defecto_AU_enrutado_a_tabla_EN_sin_ajustes
)
