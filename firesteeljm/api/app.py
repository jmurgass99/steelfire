"""FastAPI app para FireSteelJm.

Instalar con::

    pip install firesteeljm[api]
"""
from ..exceptions import DependencyError


def create_router():
    """Devuelve el APIRouter con los endpoints térmicos. Mountable en gateway.

    Raises:
        DependencyError: si FastAPI no está instalado.
    """
    try:
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel, Field
    except ImportError as exc:  # pragma: no cover
        raise DependencyError(
            "FastAPI no está instalado. Instale: pip install firesteeljm[api]"
        ) from exc

    from typing import Literal

    from ..exceptions import ConfigurationError, ConvergenceError
    from ..services.iso834 import ISO834Input, evaluate_iso834
    from ..services.thermal import ThermalAnalysisInput, run_thermal_analysis

    router = APIRouter()

    @router.get("/")
    def root() -> dict:
        return {"app": "FireSteelJm", "status": "OK"}

    @router.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    class FireCurveBody(BaseModel):
        curve: Literal["iso834", "hydrocarbon", "external"] = "iso834"
        t_minutes: list[float] = Field(
            default_factory=lambda: [0, 5, 10, 15, 30, 60, 90, 120]
        )

    class CriticalTempBody(BaseModel):
        utilization: float = Field(gt=0.013, le=1.0, description="mu = R_fi/R_d")

    @router.post("/fire/curve")
    def post_fire_curve(body: FireCurveBody) -> dict:
        try:
            from ..fire_curves_sympy import (
                iso_834 as _iso, hydrocarbon as _hc, external as _ext,
            )
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"sympy requerido (instalar firesteeljm[analytic]): {exc}",
            ) from exc

        if body.curve == "iso834":
            spec = _iso()
        elif body.curve == "hydrocarbon":
            spec = _hc()
        elif body.curve == "external":
            spec = _ext()
        else:  # pragma: no cover - validado por Literal
            raise HTTPException(status_code=400, detail=f"curve invalida: {body.curve}")

        theta = [float(spec.lambda_t_min(t)) for t in body.t_minutes]
        dtheta = [float(spec.derivative_callable(t)) for t in body.t_minutes]
        return {
            "curve_name": spec.name,
            "expression": spec.expression_str,
            "latex": spec.latex,
            "t_minutes": list(body.t_minutes),
            "theta_g_C": theta,
            "dtheta_dt_C_per_min": dtheta,
        }

    @router.post("/fire/critical_temperature")
    def post_critical_temperature(body: CriticalTempBody) -> dict:
        try:
            from ..fire_curves_sympy import critical_temperature_steel
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"sympy requerido (instalar firesteeljm[analytic]): {exc}",
            ) from exc
        try:
            Tcr = critical_temperature_steel(body.utilization)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {
            "utilization": body.utilization,
            "critical_temperature_C": Tcr,
            "formula": (
                "theta_a,cr = 39.19 * ln(1/(0.9674*mu^3.833) - 1) + 482  "
                "[EN 1993-1-2 §4.2.4]"
            ),
        }

    class ISO834Body(BaseModel):
        time_minutes: float = Field(..., ge=0)
        section_factor_amv: float = Field(150.0, gt=0)
        is_protected: bool = False

    class ThermalBody(BaseModel):
        b: float = Field(..., gt=0)
        h: float = Field(..., gt=0)
        n_x: int = 12
        n_y: int = 12
        exposed_faces: tuple[bool, bool, bool, bool] = (True, True, True, True)
        protection_thickness: float = 0.0
        protection_k: float = 0.12
        t_total: float = Field(600.0, gt=0)
        dt: float | None = None
        t_save_every: int = 10

    @router.post("/api/thermal/iso834")
    def post_iso834(body: ISO834Body) -> dict:
        try:
            res = evaluate_iso834(ISO834Input(**body.model_dump()))
        except ConfigurationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {
            "time_minutes": res.time_minutes,
            "gas_temperature_C": res.gas_temperature_C,
            "steel_temperature_C": res.steel_temperature_C,
            "yield_reduction_factor_ky": res.yield_reduction_factor_ky,
            "status": res.status,
        }

    @router.post("/api/thermal/section")
    def post_section(body: ThermalBody) -> dict:
        try:
            res = run_thermal_analysis(ThermalAnalysisInput(**body.model_dump()))
        except ConfigurationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ConvergenceError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return {
            "T_final_max": res.T_final_max,
            "T_final_mean": res.T_final_mean,
            "n_steps_saved": res.n_steps_saved,
            "times": res.times,
            "T_max_history": res.T_max_history,
            "T_mean_history": res.T_mean_history,
        }

    class ThermalIterPayload(BaseModel):
        time_minutes: list[float] = Field(..., min_length=1)
        T_celsius_at_each_t: list[float] = Field(..., min_length=1)
        utilization_at_t0: float = Field(0.6, gt=0, le=1.0)

    @router.post("/api/fire/thermal-iter")
    def thermal_iter(payload: ThermalIterPayload):
        from ..thermal_iter import critical_time_to_failure, thermal_history
        if len(payload.time_minutes) != len(payload.T_celsius_at_each_t):
            raise HTTPException(422, "time_minutes y T_celsius con misma longitud")
        ts = payload.time_minutes
        Ts = payload.T_celsius_at_each_t
        idx = {t: T for t, T in zip(ts, Ts)}
        steps = thermal_history(ts, lambda t: idx.get(t, Ts[0]))
        t_crit = critical_time_to_failure(steps, payload.utilization_at_t0)
        return {
            "t_critical_min": t_crit,
            "history": [
                {"t_min": s.t_min, "T_C": s.T_celsius,
                 "k_E": s.k_E, "k_y": s.k_y}
                for s in steps
            ],
        }

    return router


def create_app():
    """Crea la app FastAPI standalone con CORS.

    Returns:
        Instancia ``fastapi.FastAPI``.

    Raises:
        DependencyError: si FastAPI no está instalado.
    """
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError as exc:  # pragma: no cover
        raise DependencyError(
            "FastAPI no está instalado. Instale: pip install firesteeljm[api]"
        ) from exc

    app = FastAPI(title="FireSteelJm API", version="1.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(create_router())
    return app


__all__ = ["create_app", "create_router"]
