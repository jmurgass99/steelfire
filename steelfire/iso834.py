"""
iso834.py - Fire modelling and temperature calculations for steel.
"""
import math

class FireEvaluator:
    def __init__(
        self,
        time_minutes: float,
        section_factor_amv: float,
        is_protected: bool = False,
        use_en1993_exact_c_a: bool = False,
    ):
        """
        :param time_minutes: Time of fire exposure in minutes.
        :param section_factor_amv: Massivity factor Am/V in m^-1 (e.g. 150).
        :param is_protected: True if section is protected with fire-resistant materials.
        :param use_en1993_exact_c_a: If True, integrates EN 1993-1-2 §4.2.5 with exact c_a(θ_a).
        """
        self.time_minutes = time_minutes
        self.section_factor = section_factor_amv
        self.is_protected = is_protected
        self.use_en1993_exact_c_a = use_en1993_exact_c_a
        
    def gas_temperature(self) -> float:
        """
        Calculates the gas temperature (Theta_g) using standard ISO 834 curve.
        Theta_g = 20 + 345 * log10(8 * t_minutes + 1)
        """
        return 20.0 + 345.0 * math.log10(8.0 * self.time_minutes + 1.0)
        
    def steel_temperature(self) -> float:
        """
        Steel temperature (Theta_a) calculation.
        If ``use_en1993_exact_c_a=True``, delegates to EN 1993-1-2 §4.2.5 incremental solver.
        """
        if self.use_en1993_exact_c_a:
            from .en_steel_temperature import ProtectedSteel, UnprotectedSteel, steel_temperature_at
            if self.is_protected:
                sec = ProtectedSteel(
                    Am_V_1_m=self.section_factor,
                    dp_m=0.015,
                    lambda_p=0.12,
                    cp=1100.0,
                    rho_p=400.0,
                )
            else:
                sec = UnprotectedSteel(Am_V_1_m=self.section_factor, ksh=1.0)
            return float(steel_temperature_at(sec, duration_min=self.time_minutes))

        t_g = self.gas_temperature()
        if self.is_protected:
            # Protected steel heats up much slower
            reduction = 0.2
            return 20.0 + (t_g - 20.0) * reduction * (self.section_factor / 200.0)
        else:
            # Unprotected steel closely follows gas temp after a while for high Am/V
            efficiency = min(1.0, self.section_factor / 100.0)
            return 20.0 + (t_g - 20.0) * efficiency * 0.9

    def yield_reduction_factor(self) -> float:
        """
        Reduction factor for effective yield strength k_{y,theta} based on EN 1993-1-2.
        Delegates to :func:`ky_from_temperature` (full Table 3.1, 20-1200 C).
        """
        return ky_from_temperature(self.steel_temperature())

    def evaluation_report(self) -> dict:
        t_g = self.gas_temperature()
        t_s = self.steel_temperature()
        ky = self.yield_reduction_factor()
        
        return {
            "time_minutes": self.time_minutes,
            "gas_temperature_C": round(t_g, 1),
            "steel_temperature_C": round(t_s, 1),
            "yield_reduction_factor_ky": round(ky, 3),
            "status": "DANGER" if ky < 0.5 else "OK"
        }


# EN 1993-1-2 Tabla 3.1 — k_y,theta (nodos oficiales, interpolacion lineal).
# La version anterior de este mapeo devolvia una CONSTANTE 0.05 por encima de
# 800 C: discontinua en 800 C (0.11 -> 0.05 por un epsilon) y del lado INSEGURO
# en 1100-1200 C, donde la tabla real da 0.02 y 0.00. Cazado por la campana de
# goldens (que ya habia vendorizado la tabla completa en test_thermal_iter.py)
# y corregido con test dedicado (tests/test_iso834_ky_table.py).
_KY_TABLE_31 = (
    (20.0, 1.00), (400.0, 1.00), (500.0, 0.78), (600.0, 0.47), (700.0, 0.23),
    (800.0, 0.11), (900.0, 0.06), (1000.0, 0.04), (1100.0, 0.02), (1200.0, 0.00),
)


def ky_from_temperature(t_C: float) -> float:
    """k_y,theta de EN 1993-1-2 Tabla 3.1 por interpolacion lineal (20-1200 C).

    Por debajo de 20 C devuelve 1.0; a partir de 1200 C devuelve 0.0.
    """
    t = float(t_C)
    if t <= _KY_TABLE_31[0][0]:
        return _KY_TABLE_31[0][1]
    for (t0, k0), (t1, k1) in zip(_KY_TABLE_31, _KY_TABLE_31[1:]):
        if t <= t1:
            return k0 + (k1 - k0) * (t - t0) / (t1 - t0)
    return 0.0
