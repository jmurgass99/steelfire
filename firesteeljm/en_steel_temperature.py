# -*- coding: utf-8 -*-
"""Modelo de calculo simple de temperatura del acero (EN 1993-1-2 §4.2.5).

Evolucion incremental de la temperatura de una seccion de acero bajo fuego, por
el factor de seccion Am/V (1/m):
  - §4.2.5.1 elemento sin proteger (con efecto sombra ksh).
  - §4.2.5.2 elemento protegido (material de proteccion dp, lambda_p, cp, rho_p).

Calor especifico del acero ca(θ) segun §3.4.1.2 (piecewise). Curva de gas por
defecto ISO 834.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Callable, List, Tuple

_RHO_A = 7850.0      # kg/m3
_SIGMA = 5.67e-8     # W/m2K4
_ALPHA_C = 25.0      # W/m2K (fuego nominal estandar)
_EMISS = 0.7         # emisividad resultante (εm·εf)


def specific_heat_steel(theta_C: float) -> float:
    """Calor especifico del acero ca(θ) en J/kgK (EN 1993-1-2 §3.4.1.2)."""
    t = theta_C
    if t < 600.0:
        return 425.0 + 0.773 * t - 1.69e-3 * t ** 2 + 2.22e-6 * t ** 3
    if t < 735.0:
        return 666.0 + 13002.0 / (738.0 - t)
    if t < 900.0:
        return 545.0 + 17820.0 / (t - 731.0)
    return 650.0


def iso834_gas(t_min: float) -> float:
    """Curva de gas ISO 834 (°C)."""
    return 20.0 + 345.0 * math.log10(8.0 * t_min + 1.0)


@dataclass(frozen=True)
class UnprotectedSteel:
    Am_V_1_m: float          # factor de seccion Am/V (1/m)
    ksh: float = 1.0         # factor de sombra (I-sections < 1)


@dataclass(frozen=True)
class ProtectedSteel:
    Am_V_1_m: float          # Ap/V del material de proteccion
    dp_m: float              # espesor de la proteccion
    lambda_p: float          # conductividad W/mK
    cp: float                # calor especifico J/kgK
    rho_p: float             # densidad kg/m3


def steel_temperature_history(
    section,
    duration_min: float = 60.0,
    dt_s: float = 5.0,
    gas_curve: Callable[[float], float] = iso834_gas,
) -> List[Tuple[float, float]]:
    """Historia (t_min, θ_a) de la temperatura del acero.

    ``section`` es UnprotectedSteel o ProtectedSteel. Integra por Euler con paso
    dt_s. Devuelve lista de (tiempo_min, temperatura_°C).
    """
    theta_a = 20.0
    t = 0.0
    out = [(0.0, theta_a)]
    n = int(duration_min * 60.0 / dt_s)
    protected = isinstance(section, ProtectedSteel)
    for _ in range(n):
        t_min = t / 60.0
        theta_g = gas_curve(t_min)
        theta_g_next = gas_curve((t + dt_s) / 60.0)
        ca = specific_heat_steel(theta_a)
        if not protected:
            # §4.2.5.1: hnet = conveccion + radiacion.
            hnet_c = _ALPHA_C * (theta_g - theta_a)
            hnet_r = _EMISS * _SIGMA * ((theta_g + 273.0) ** 4 - (theta_a + 273.0) ** 4)
            dtheta = section.ksh * (section.Am_V_1_m / (ca * _RHO_A)) * (hnet_c + hnet_r) * dt_s
        else:
            # §4.2.5.2: con phi del material de proteccion.
            phi = (section.cp * section.rho_p / (ca * _RHO_A)) * section.dp_m * section.Am_V_1_m
            term = (section.lambda_p * section.Am_V_1_m / (section.dp_m * ca * _RHO_A))
            dtheta = term * (theta_g - theta_a) / (1.0 + phi / 3.0) * dt_s
            dtheta -= (math.exp(phi / 10.0) - 1.0) * (theta_g_next - theta_g)
            dtheta = max(dtheta, 0.0)  # no enfriamiento mientras el gas sube
        theta_a += dtheta
        t += dt_s
        out.append((t / 60.0, theta_a))
    return out


def steel_temperature_at(section, duration_min: float, dt_s: float = 5.0,
                         gas_curve: Callable[[float], float] = iso834_gas) -> float:
    """Temperatura del acero al cabo de ``duration_min`` (°C)."""
    return steel_temperature_history(section, duration_min, dt_s, gas_curve)[-1][1]


def critical_temperature(mu_0: float = 0.65) -> float:
    """Temperatura critica del acero segun EN 1993-1-2 §4.2.4 (Eq. 4.22).

    theta_crit = 39.19 * ln(1 / (0.9674 * mu_0^3.833) - 1) + 482

    Dominio: 0 < mu_0 <= 1. El grado de utilizacion es el cociente
    E_fi,d / R_fi,d,0 (§4.2.4): por encima de 1 el elemento ya no resiste a
    tiempo cero y no existe temperatura critica. Ademas el argumento del
    logaritmo se anula en mu_0 = 0.9674^(-1/3.833) = 1.00874 y es negativo por
    encima, de modo que fuera del dominio la ecuacion no tiene solucion real.

    Raises:
        ValueError: si mu_0 esta fuera de (0, 1].
    """
    if not (0.0 < mu_0 <= 1.0):
        raise ValueError(
            f"mu_0 fuera del dominio de EN 1993-1-2 §4.2.4: recibido {mu_0!r}. "
            "El grado de utilizacion debe cumplir 0 < mu_0 <= 1."
        )
    # Sin clamp: dentro del dominio el argumento es siempre estrictamente
    # positivo (minimo 1/0.9674 - 1 = 0.03370 en mu_0 = 1). Un clamp aqui
    # devolveria temperaturas negativas en vez de senalar el error.
    term = 1.0 / (0.9674 * (mu_0 ** 3.833)) - 1.0
    return 39.19 * math.log(term) + 482.0


# Clases de prestacion EN 13501-2: R (capacidad portante), E (integridad),
# I (aislamiento), W (radiacion), M (impacto), C (cierre automatico),
# S (estanqueidad al humo).
_RATING_RE = re.compile(r"^\s*([REIWMCS]+)\s*[-\s]?\s*(\d+)\s*$", re.IGNORECASE)

_RATING_FORMATS = (
    "letras de clase EN 13501-2 (R, E, I, W, M, C, S) seguidas de los minutos: "
    "'R60', 'R 90', 'REI90', 'REI 90', 'REI-90', 'EI30'"
)


def parse_fire_rating_minutes(required_rating: str) -> float:
    """Minutos de un requisito de resistencia al fuego EN 13501-2.

    El numero de la clasificacion ES la duracion normalizada en minutos, de modo
    que 'REI90' son 90 minutos. Una cadena que no se pueda interpretar ABORTA:
    degradarla a un valor por defecto evaluaria el elemento por debajo de su
    requisito y del lado inseguro.

    Raises:
        ValueError: si la cadena no corresponde a una clasificacion valida.
    """
    m = _RATING_RE.match(required_rating or "")
    if m is None:
        raise ValueError(
            f"requisito de resistencia al fuego no interpretable: {required_rating!r}. "
            f"Formatos aceptados: {_RATING_FORMATS}."
        )
    minutos = float(m.group(2))
    if minutos <= 0.0:
        raise ValueError(
            f"requisito de resistencia al fuego no positivo: {required_rating!r}. "
            f"Formatos aceptados: {_RATING_FORMATS}."
        )
    return minutos


# Estados de verificacion posibles del chequeo de resistencia al fuego.
STATUS_SIN_PROTECCION_CUMPLE = "SIN_PROTECCION_CUMPLE"
STATUS_CON_PROTECCION_CUMPLE = "CON_PROTECCION_CUMPLE"
STATUS_CON_PROTECCION_NO_CUMPLE = "CON_PROTECCION_NO_CUMPLE"
STATUS_NO_VERIFICADO = "NO_VERIFICADO"


@dataclass(frozen=True)
class FireDesignCheckResult:
    """Resultado del chequeo de resistencia al fuego de un perfil estructural.

    ``is_safe`` sale SIEMPRE de una comparacion termica real
    (theta_alcanzada <= theta_crit). Cuando esa comparacion no se puede hacer
    -- por ejemplo porque no hay proteccion del tipo solicitado en el catalogo --
    ``is_safe`` es ``None`` y ``verification_status`` vale ``"NO_VERIFICADO"``.
    Nunca ``True`` por ausencia de datos.
    """
    section_name: str
    Am_V_m_inv: float
    required_rating: str
    duration_min: float
    load_ratio_mu0: float
    theta_crit_C: float
    theta_unprotected_C: float
    requires_protection: bool
    recommended_protection: dict | None
    is_safe: bool | None
    verification_status: str
    theta_protected_C: float | None = None
    available_protection_types: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "section_name": self.section_name,
            "Am_V_m_inv": self.Am_V_m_inv,
            "required_rating": self.required_rating,
            "duration_min": self.duration_min,
            "load_ratio_mu0": self.load_ratio_mu0,
            "theta_crit_C": round(self.theta_crit_C, 1),
            "theta_unprotected_C": round(self.theta_unprotected_C, 1),
            "theta_protected_C": (
                None if self.theta_protected_C is None
                else round(self.theta_protected_C, 1)
            ),
            "requires_protection": self.requires_protection,
            "recommended_protection": self.recommended_protection,
            "available_protection_types": list(self.available_protection_types),
            "is_safe": self.is_safe,
            "verification_status": self.verification_status,
            "notes": list(self.notes),
        }


def check_fire_resistance_from_profile(
    section_name: str,
    Am_V_m_inv: float,
    load_ratio_mu0: float = 0.65,
    required_rating: str = "R60",
    preferred_protection_type: str = "intumescent",
) -> FireDesignCheckResult:
    """Evalúa la resistencia al fuego de un perfil y verifica la protección propuesta.

    El veredicto ``is_safe`` se obtiene comparando la temperatura ALCANZADA con
    la critica: sin proteger si no hace falta protegerlo, y con la temperatura
    calculada segun §4.2.5.2 para el espesor propuesto si hace falta. Si no se
    puede calcular esa temperatura protegida, ``is_safe`` es ``None`` y el
    estado es ``"NO_VERIFICADO"``.

    Raises:
        ValueError: si ``required_rating`` no es una clasificacion interpretable
            o si ``load_ratio_mu0`` esta fuera del dominio de §4.2.4.
    """
    from . import protection_catalog

    # D2: un requisito ininteligible ABORTA; no cae a 60 min por defecto.
    duration_min = parse_fire_rating_minutes(required_rating)

    theta_crit = critical_temperature(load_ratio_mu0)

    # Temperatura alcanzada sin proteger
    unprotected = UnprotectedSteel(Am_V_1_m=Am_V_m_inv, ksh=0.90)
    theta_unprot = steel_temperature_at(unprotected, duration_min=duration_min)

    requires_prot = theta_unprot > theta_crit
    prot_info: dict | None = None
    theta_prot: float | None = None
    notes: list[str] = []

    if not requires_prot:
        # Veredicto por comparacion directa del elemento sin proteger.
        return FireDesignCheckResult(
            section_name=section_name,
            Am_V_m_inv=Am_V_m_inv,
            required_rating=required_rating,
            duration_min=duration_min,
            load_ratio_mu0=load_ratio_mu0,
            theta_crit_C=theta_crit,
            theta_unprotected_C=theta_unprot,
            requires_protection=False,
            recommended_protection=None,
            is_safe=True,
            verification_status=STATUS_SIN_PROTECCION_CUMPLE,
            theta_protected_C=None,
            available_protection_types=(),
            notes=(),
        )

    candidates = protection_catalog.recommend(target_rating_min=int(duration_min))
    available_types = tuple(sorted({p.type for p in candidates}))
    # D4: sin candidatos del tipo pedido NO se sustituye por otro material.
    matching = [p for p in candidates if preferred_protection_type in p.type]

    if not matching:
        notes.append(
            f"No hay proteccion de tipo {preferred_protection_type!r} en el catalogo "
            f"para {required_rating} ({duration_min:.0f} min). Tipos disponibles: "
            f"{', '.join(available_types) if available_types else 'ninguno'}. "
            "No se sustituye por otro material: sin proteccion evaluada no hay veredicto."
        )
        return FireDesignCheckResult(
            section_name=section_name,
            Am_V_m_inv=Am_V_m_inv,
            required_rating=required_rating,
            duration_min=duration_min,
            load_ratio_mu0=load_ratio_mu0,
            theta_crit_C=theta_crit,
            theta_unprotected_C=theta_unprot,
            requires_protection=True,
            recommended_protection=None,
            is_safe=None,
            verification_status=STATUS_NO_VERIFICADO,
            theta_protected_C=None,
            available_protection_types=available_types,
            notes=tuple(notes),
        )

    best_prot = matching[0]
    # Espesor típico medio recomendado
    t_min_mm, t_max_mm = best_prot.typical_thickness_mm
    chosen_t_mm = (t_min_mm + t_max_mm) / 2.0
    prot_info = {
        "code": best_prot.code,
        "type": best_prot.type,
        "thickness_mm": chosen_t_mm,
        "thickness_range_mm": best_prot.typical_thickness_mm,
        "cost_USD_per_m2": best_prot.cost_USD_per_m2,
        "rating_minutes": best_prot.rating_minutes,
    }

    # D1: se APLICA el espesor propuesto y se compara de verdad (§4.2.5.2).
    # Se asume Ap/V = Am/V (proteccion que sigue el contorno del perfil).
    protected = ProtectedSteel(
        Am_V_1_m=Am_V_m_inv,
        dp_m=chosen_t_mm / 1000.0,
        lambda_p=best_prot.lambda_p_W_per_mK,
        cp=best_prot.c_p_J_per_kgK,
        rho_p=best_prot.rho_p_kg_m3,
    )
    theta_prot = steel_temperature_at(protected, duration_min=duration_min)
    notes.append(
        "Temperatura protegida calculada con Ap/V = Am/V (proteccion siguiendo el "
        f"contorno) y espesor {chosen_t_mm:.2f} mm (medio del rango tipico)."
    )
    if best_prot.type == "intumescent":
        notes.append(
            "CAVEAT: lambda_p del catalogo es un valor de pelicula SECA. El modelo "
            "de capa inerte de EN 1993-1-2 4.2.5.2 no representa el hinchamiento de una pintura "
            "intumescente; usar el espesor certificado del ensayo UL/EN, no este calculo."
        )

    is_safe = theta_prot <= theta_crit
    status = (
        STATUS_CON_PROTECCION_CUMPLE if is_safe else STATUS_CON_PROTECCION_NO_CUMPLE
    )
    if not is_safe:
        notes.append(
            f"El espesor propuesto ({chosen_t_mm:.2f} mm) no basta: "
            f"theta = {theta_prot:.1f} C > theta_crit = {theta_crit:.1f} C."
        )

    return FireDesignCheckResult(
        section_name=section_name,
        Am_V_m_inv=Am_V_m_inv,
        required_rating=required_rating,
        duration_min=duration_min,
        load_ratio_mu0=load_ratio_mu0,
        theta_crit_C=theta_crit,
        theta_unprotected_C=theta_unprot,
        requires_protection=True,
        recommended_protection=prot_info,
        is_safe=is_safe,
        verification_status=status,
        theta_protected_C=theta_prot,
        available_protection_types=available_types,
        notes=tuple(notes),
    )


def shadow_factor_I(Am_V_1_m: float, Am_V_box_1_m: float) -> float:
    """Efecto sombra para perfiles I (§4.2.5.1): ksh = 0.9·(Am/V)_box/(Am/V)."""
    return 0.9 * Am_V_box_1_m / Am_V_1_m


__all__ = [
    "UnprotectedSteel",
    "ProtectedSteel",
    "FireDesignCheckResult",
    "specific_heat_steel",
    "iso834_gas",
    "steel_temperature_history",
    "steel_temperature_at",
    "critical_temperature",
    "parse_fire_rating_minutes",
    "check_fire_resistance_from_profile",
    "STATUS_SIN_PROTECCION_CUMPLE",
    "STATUS_CON_PROTECCION_CUMPLE",
    "STATUS_CON_PROTECCION_NO_CUMPLE",
    "STATUS_NO_VERIFICADO",
    "shadow_factor_I",
]
