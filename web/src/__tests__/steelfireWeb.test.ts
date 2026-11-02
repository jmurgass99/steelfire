import assert from "node:assert/strict";
import { getThermalMesh } from "../mesh/getMesh.ts";
import { initThermalWasm, solveFireHeatingWasm } from "../solver/wasmSolver.ts";

// 1. Thermal mesh mapping
const m = getThermalMesh(300, 150, 10.7, 7.1, 6);
assert.equal(m.cells.length, 18);
assert.equal(m.regionToCells.get("web")?.length, 6);

// 2. Fire heating in WASM
await initThermalWasm();
const m4 = getThermalMesh(300, 150, 10.7, 7.1, 4);
const res = solveFireHeatingWasm({
  mapping: m4,
  fireCurve: "iso834",
  durationMin: 45,
});

assert.ok(res.webTempC[res.webTempC.length - 1] > 600);
assert.ok(res.kyWeb[res.kyWeb.length - 1] < 0.5);

console.log(
  `SteelFire WASM test OK: T_web_final=${res.webTempC[res.webTempC.length - 1].toFixed(1)} °C, k_y_web=${res.kyWeb[res.kyWeb.length - 1].toFixed(3)}`
);
