export interface ThermalCell {
  xMm: number;
  yMm: number;
  dxMm: number;
  dyMm: number;
  amvMInv: number;
}

export interface ThermalSectionMapping {
  regionToCells: Map<string, number[]>;
  cells: ThermalCell[];
}

export interface FireThermalResult {
  engine: "wasm-local" | "fastapi-python";
  timesMin: number[];
  gasTempC: number[];
  webTempC: number[];
  flangeTempC: number[];
  kyWeb: number[];
  conductivityAtEndWmk: number;
}
