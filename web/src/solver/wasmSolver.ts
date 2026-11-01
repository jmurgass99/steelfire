import type { FireThermalResult, ThermalSectionMapping } from "../data-model";

const THERMAL_WASM_BASE64 =
  "AGFzbQEAAAABDgJgAXwBfGAEfHx8fAF8AwMCAAEHMAIXc3RlZWxDb25kdWN0aXZpdHlMaW5lYXIAABJzdGVlbFRlbXBJbmNyZW1lbnQAAQoyAhgARAAAAAAAAEtARLHh6ZWyDKE/IACioQsXACAAIAGiIAOiRAAAAAAAqr5AIAKiows=";

export interface ThermalWasmExports {
  steelConductivityLinear: (thetaC: number) => number;
  steelTempIncrement: (amV: number, hNet: number, cA: number, dtS: number) => number;
}

let cached: ThermalWasmExports | null = null;

function decode(b64: string): Uint8Array {
  if (typeof Buffer !== "undefined") return new Uint8Array(Buffer.from(b64, "base64"));
  const s = atob(b64);
  const out = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i);
  return out;
}

export async function initThermalWasm(): Promise<ThermalWasmExports> {
  if (cached) return cached;
  const bytes = decode(THERMAL_WASM_BASE64);
  const { instance } = await WebAssembly.instantiate(bytes.buffer as ArrayBuffer);
  cached = instance.exports as unknown as ThermalWasmExports;
  return cached;
}

export function getThermalWasmSync(): ThermalWasmExports {
  if (cached) return cached;
  const bytes = decode(THERMAL_WASM_BASE64);
  const mod = new WebAssembly.Module(bytes.buffer as ArrayBuffer);
  const instance = new WebAssembly.Instance(mod);
  cached = instance.exports as unknown as ThermalWasmExports;
  return cached;
}

function yieldReductionKy(thetaC: number): number {
  if (thetaC <= 400) return 1.0;
  if (thetaC <= 500) return 1.0 - ((thetaC - 400) / 100) * 0.22;
  if (thetaC <= 600) return 0.78 - ((thetaC - 500) / 100) * 0.31;
  if (thetaC <= 700) return 0.47 - ((thetaC - 600) / 100) * 0.24;
  if (thetaC <= 800) return 0.23 - ((thetaC - 700) / 100) * 0.12;
  if (thetaC <= 1200) return Math.max(0, 0.11 * (1 - (thetaC - 800) / 400));
  return 0;
}

export function solveFireHeatingWasm({
  mapping,
  fireCurve,
  durationMin,
}: {
  mapping: ThermalSectionMapping;
  fireCurve: "iso834" | "hydrocarbon" | "parametric";
  durationMin: number;
}): FireThermalResult {
  const wasm = getThermalWasmSync();
  const webIdx = mapping.regionToCells.get("web")?.[0] ?? 0;
  const flangeIdx = mapping.regionToCells.get("bottom_flange")?.[0] ?? 0;
  const amvWeb = mapping.cells[webIdx]?.amvMInv ?? 280;
  const amvFlange = mapping.cells[flangeIdx]?.amvMInv ?? 180;

  const dtS = 5.0;
  const nSteps = Math.floor((durationMin * 60) / dtS);
  let tWeb = 20.0;
  let tFlange = 20.0;

  const timesMin: number[] = [0];
  const gasTempC: number[] = [20];
  const webTempC: number[] = [20];
  const flangeTempC: number[] = [20];
  const kyWeb: number[] = [1.0];

  const sigma = 5.67e-8;
  const eps = 0.7;
  const alphaC = fireCurve === "hydrocarbon" ? 50.0 : 25.0;

  for (let step = 1; step <= nSteps; step++) {
    const tMin = (step * dtS) / 60.0;
    let tg = 20 + 345 * Math.log10(8 * tMin + 1);
    if (fireCurve === "hydrocarbon") {
      tg = 20 + 1080 * (1 - 0.325 * Math.exp(-0.167 * tMin) - 0.675 * Math.exp(-2.5 * tMin));
    } else if (fireCurve === "parametric" && tMin > 35) {
      const tMax = 20 + 345 * Math.log10(8 * 35 + 1);
      tg = Math.max(20, tMax - 12.5 * (tMin - 35));
    }

    const hNetW =
      alphaC * (tg - tWeb) +
      sigma * eps * (Math.pow(tg + 273.15, 4) - Math.pow(tWeb + 273.15, 4));
    const hNetF =
      alphaC * (tg - tFlange) +
      sigma * eps * (Math.pow(tg + 273.15, 4) - Math.pow(tFlange + 273.15, 4));

    const cA = 425 + 0.773 * tWeb;
    tWeb += wasm.steelTempIncrement(amvWeb, hNetW, cA, dtS);
    tFlange += wasm.steelTempIncrement(amvFlange, hNetF, cA, dtS);

    if (step % 6 === 0 || step === nSteps) {
      timesMin.push(Number(tMin.toFixed(2)));
      gasTempC.push(Number(tg.toFixed(1)));
      webTempC.push(Number(tWeb.toFixed(1)));
      flangeTempC.push(Number(tFlange.toFixed(1)));
      kyWeb.push(Number(yieldReductionKy(tWeb).toFixed(4)));
    }
  }

  const kEnd = Math.max(27.3, wasm.steelConductivityLinear(tWeb));

  return {
    engine: "wasm-local",
    timesMin,
    gasTempC,
    webTempC,
    flangeTempC,
    kyWeb,
    conductivityAtEndWmk: Number(kEnd.toFixed(2)),
  };
}
