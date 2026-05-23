"""
iso834.py - Fire modelling and temperature calculations for steel.
"""
import math

class FireEvaluator:
    def __init__(self, time_minutes: float, section_factor_amv: float, is_protected: bool = False):
        """
        :param time_minutes: Time of fire exposure in minutes.
        :param section_factor_amv: Massivity factor Am/V in m^-1 (e.g. 150).
        :param is_protected: True if section is protected with fire-resistant materials.
        """
        self.time_minutes = time_minutes
        self.section_factor = section_factor_amv
        self.is_protected = is_protected
        
    def gas_temperature(self) -> float:
        """
        Calculates the gas temperature (Theta_g) using standard ISO 834 curve.
        Theta_g = 20 + 345 * log10(8 * t_minutes + 1)
        """
        return 20.0 + 345.0 * math.log10(8.0 * self.time_minutes + 1.0)
        
    def steel_temperature(self) -> float:
        """
        Simplified steel temperature (Theta_a) calculation.
        For demonstration, assuming an incremental simplified model based on Am/V.
        """
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
        """
        t_s = self.steel_temperature()
        
        # Simplified EC3 Table 3.1 reduction factors
        if t_s <= 400:
            return 1.0
        elif t_s <= 500:
            return 1.0 - 0.22 * ((t_s - 400)/100) # Drops to 0.78
        elif t_s <= 600:
            return 0.78 - 0.31 * ((t_s - 500)/100) # Drops to 0.47
        elif t_s <= 700:
            return 0.47 - 0.24 * ((t_s - 600)/100) # Drops to 0.23
        elif t_s <= 800:
            return 0.23 - 0.12 * ((t_s - 700)/100) # Drops to 0.11
        else:
            return 0.05 # Almost no strength

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
