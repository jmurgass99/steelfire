import { describe, expect, it } from "vitest";
import { getThermalMesh } from "../mesh/getMesh";
import { initThermalWasm, solveFireHeatingWasm } from "../solver/wasmSolver";

describe("SteelFire Web — ThermalSectionMapping + thermalKernel.wasm", () => {
  it("maps bottom_flange, web, and top_flange cells across divisions", () => {
    const m = getThermalMesh(300, 150, 10.7, 7.1, 6);
    expect(m.cells.length).toBe(18);
    expect(m.regionToCells.get("web")?.length).toBe(6);
  });

  it("computes ISO 834 steel heating and retention factor via WebAssembly", async () => {
    await initThermalWasm();
    const m = getThermalMesh(300, 150, 10.7, 7.1, 4);
    const res = solveFireHeatingWasm({
      mapping: m,
      fireCurve: "iso834",
      durationMin: 45,
    });
    expect(res.webTempC[res.webTempC.length - 1]).toBeGreaterThan(600);
    expect(res.kyWeb[res.kyWeb.length - 1]).toBeLessThan(0.5);
  });
});
