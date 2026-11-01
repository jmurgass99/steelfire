import type { ThermalCell, ThermalSectionMapping } from "../data-model";

export function getThermalMesh(
  hMm: number,
  bMm: number,
  tfMm: number,
  twMm: number,
  divisionsPerRegion: number,
): ThermalSectionMapping {
  const nDiv = Math.max(1, Math.floor(divisionsPerRegion));
  const regionToCells = new Map<string, number[]>([
    ["bottom_flange", []],
    ["web", []],
    ["top_flange", []],
  ]);
  const cells: ThermalCell[] = [];

  const halfH = 0.5 * hMm;
  const halfB = 0.5 * bMm;
  const amvFlange = 2000 / Math.max(tfMm, 1);
  const amvWeb = 2000 / Math.max(twMm, 1);

  const dxF = bMm / nDiv;
  for (let k = 0; k < nDiv; k++) {
    regionToCells.get("bottom_flange")!.push(cells.length);
    cells.push({
      xMm: -halfB + (k + 0.5) * dxF,
      yMm: -halfH + 0.5 * tfMm,
      dxMm: dxF,
      dyMm: tfMm,
      amvMInv: amvFlange,
    });
  }

  const hWeb = Math.max(hMm - 2 * tfMm, 10);
  const dyW = hWeb / nDiv;
  for (let k = 0; k < nDiv; k++) {
    regionToCells.get("web")!.push(cells.length);
    cells.push({
      xMm: 0,
      yMm: -0.5 * hWeb + (k + 0.5) * dyW,
      dxMm: twMm,
      dyMm: dyW,
      amvMInv: amvWeb,
    });
  }

  for (let k = 0; k < nDiv; k++) {
    regionToCells.get("top_flange")!.push(cells.length);
    cells.push({
      xMm: -halfB + (k + 0.5) * dxF,
      yMm: halfH - 0.5 * tfMm,
      dxMm: dxF,
      dyMm: tfMm,
      amvMInv: amvFlange,
    });
  }

  return { regionToCells, cells };
}
