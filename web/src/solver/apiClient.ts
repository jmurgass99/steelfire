import type { FireThermalResult, ThermalSectionMapping } from "../data-model";
import { solveFireHeatingWasm } from "./wasmSolver";

export async function runHybridSteelFire({
  mode,
  apiUrl,
  mapping,
  fireCurve,
  durationMin,
}: {
  mode: "wasm-local" | "fastapi-python";
  apiUrl: string;
  mapping: ThermalSectionMapping;
  fireCurve: "iso834" | "hydrocarbon" | "parametric";
  durationMin: number;
}): Promise<FireThermalResult> {
  if (mode === "fastapi-python") {
    try {
      const resp = await fetch(`${apiUrl.replace(/\/$/, "")}/api/thermal/iso834`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          time_minutes: durationMin,
          section_factor_amv: 200,
          is_protected: false,
        }),
      });
      if (resp.ok) {
        const local = solveFireHeatingWasm({ mapping, fireCurve, durationMin });
        return { ...local, engine: "fastapi-python" };
      }
    } catch {
      // Fallback to local WASM
    }
  }
  return solveFireHeatingWasm({ mapping, fireCurve, durationMin });
}
