"""API REST (extra `api`) sin servidor: curvas de fuego, temperatura crítica y chequeo de perfil por HTTP.

POST /fire/curve (ISO 834, hidrocarburos, externa; requiere sympy, si falta responde 503 y
dice qué instalar), POST /fire/critical_temperature, POST /api/fire/check-profile y
POST /api/thermal/iso834. Este último usa el estimador simplificado `FireEvaluator`, que
no es el método de EN 1993-1-2 §4.2.5: se mantiene por compatibilidad y aquí se muestra con
esa advertencia. La aplicación se sirve con `uvicorn steelfire.api.app:app`.

Ejecutar:  python examples/rest_api_fire_curves_critical_temperature_check_profile.py
"""
import json
import warnings

warnings.filterwarnings("ignore")
from fastapi.testclient import TestClient  # noqa: E402

from steelfire.api.app import create_app  # noqa: E402


def main() -> None:
    c = TestClient(create_app())
    print("GET /api/thermal/health →", c.get("/api/thermal/health").json())

    r = c.post("/fire/curve", json={"curve": "hydrocarbon", "t_minutes": [0, 5, 30, 60]})
    print("\nPOST /fire/curve (hydrocarbon) →", r.status_code, json.dumps(r.json(), ensure_ascii=False)[:300])

    r = c.post("/fire/critical_temperature", json={"utilization": 0.16})
    print("\nPOST /fire/critical_temperature (μ = 0,16, caso W01437) →", r.status_code, json.dumps(r.json(), ensure_ascii=False))

    r = c.post("/api/fire/check-profile", json={"section_name": "HEB 300", "Am_V_m_inv": 115.0, "load_ratio_mu0": 0.65,
                                                "required_rating": "R90", "preferred_protection_type": "board"})
    body = r.json()
    print("\nPOST /api/fire/check-profile (HEB 300, R90, placa) →", r.status_code)
    print(json.dumps({k: body[k] for k in ("theta_crit_C", "theta_unprotected_C", "theta_protected_C",
                                           "verification_status", "is_safe")}, ensure_ascii=False))

    r = c.post("/api/thermal/iso834", json={"time_minutes": 30, "section_factor_amv": 150.0})
    print("\nPOST /api/thermal/iso834 →", r.status_code, json.dumps(r.json(), ensure_ascii=False))
    print("  (estimador simplificado FireEvaluator: la temperatura del acero NO sale de la ec. 4.25; usa check-profile)")

    r = c.post("/fire/critical_temperature", json={"utilization": 1.5})
    print("\nμ = 1,5 →", r.status_code, "(validación de entrada)")


if __name__ == "__main__":
    main()
