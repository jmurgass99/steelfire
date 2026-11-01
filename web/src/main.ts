import van from "vanjs-core";
import type { ThermalSectionMapping } from "./data-model";
import { getThermalMesh } from "./mesh/getMesh";
import { runHybridSteelFire } from "./solver/apiClient";
import { initThermalWasm } from "./solver/wasmSolver";
import { getThermalGraphs } from "./ui/getThermalGraphs";
import { getViewer3D } from "./viewer/getViewer3D";

const { div, h2, h3, input, label, option, select, span } = van.tags;

await initThermalWasm();

const hMm = van.state(300);
const bMm = van.state(150);
const tfMm = van.state(10.7);
const twMm = van.state(7.1);
const divisionsPerRegion = van.state(6);
const fireCurve = van.state<"iso834" | "hydrocarbon" | "parametric">("iso834");
const durationMin = van.state(60);
const stepIdx = van.state(10);
const solverMode = van.state<"wasm-local" | "fastapi-python">("wasm-local");

const mapping = van.state<ThermalSectionMapping>(
  getThermalMesh(hMm.val, bMm.val, tfMm.val, twMm.val, divisionsPerRegion.val),
);
const timesMin = van.state<number[]>([]);
const gasTempC = van.state<number[]>([]);
const webTempC = van.state<number[]>([]);
const flangeTempC = van.state<number[]>([]);
const kyWeb = van.state<number[]>([]);
const kEnd = van.state(27.3);

van.derive(() => {
  mapping.val = getThermalMesh(
    hMm.val,
    bMm.val,
    tfMm.val,
    twMm.val,
    divisionsPerRegion.val,
  );
});

van.derive(() => {
  runHybridSteelFire({
    mode: solverMode.val,
    apiUrl: "http://127.0.0.1:8000",
    mapping: mapping.val,
    fireCurve: fireCurve.val,
    durationMin: durationMin.val,
  }).then((res) => {
    timesMin.val = res.timesMin;
    gasTempC.val = res.gasTempC;
    webTempC.val = res.webTempC;
    flangeTempC.val = res.flangeTempC;
    kyWeb.val = res.kyWeb;
    kEnd.val = res.conductivityAtEndWmk;
    stepIdx.val = Math.max(0, res.timesMin.length - 1);
  });
});

const currentWebTempC = van.derive(() => webTempC.val[stepIdx.val] ?? 20);
const currentFlangeTempC = van.derive(() => flangeTempC.val[stepIdx.val] ?? 20);

const left = div(
  { class: "sf-panel" },
  h2({ style: "font-size: 1.05rem;" }, "SteelFire 3D — Termofluencia EN 1993-1-2"),
  div(
    { class: "sf-card" },
    h3("Malla Térmica (regionToCells)"),
    div(
      { class: "sf-row" },
      label("Espesor ala tf [mm]:"),
      input({
        type: "number",
        step: "0.5",
        value: () => String(tfMm.val),
        oninput: (e: Event) => (tfMm.val = Math.max(3, Number((e.target as HTMLInputElement).value) || 10.7)),
      }),
    ),
    div(
      { class: "sf-row" },
      label("Espesor alma tw [mm]:"),
      input({
        type: "number",
        step: "0.5",
        value: () => String(twMm.val),
        oninput: (e: Event) => (twMm.val = Math.max(2, Number((e.target as HTMLInputElement).value) || 7.1)),
      }),
    ),
    div(
      { class: "sf-row" },
      label("Celdas / región:"),
      input({
        type: "number",
        min: "1",
        max: "12",
        value: () => String(divisionsPerRegion.val),
        oninput: (e: Event) =>
          (divisionsPerRegion.val = Math.max(1, Number((e.target as HTMLInputElement).value) || 5)),
      }),
    ),
    div(
      { class: "sf-row" },
      label("Total Celdas 3D:"),
      span(() => `${mapping.val.cells.length} celdas`),
    ),
  ),
  div(
    { class: "sf-card" },
    h3("Curva de Fuego y Tiempo"),
    div(
      { class: "sf-row" },
      label("Curva:"),
      select(
        {
          onchange: (e: Event) =>
            (fireCurve.val = (e.target as HTMLSelectElement).value as "iso834" | "hydrocarbon" | "parametric"),
        },
        option({ value: "iso834" }, "ISO 834 Estándar"),
        option({ value: "hydrocarbon" }, "Hidrocarburos"),
        option({ value: "parametric" }, "Paramétrica Anexo A"),
      ),
    ),
    div(
      { class: "sf-row" },
      label("Paso de Tiempo:"),
      input({
        type: "range",
        min: "0",
        max: () => String(Math.max(0, timesMin.val.length - 1)),
        value: () => String(stepIdx.val),
        oninput: (e: Event) => (stepIdx.val = Number((e.target as HTMLInputElement).value)),
      }),
    ),
    div(
      { class: "sf-row" },
      label("θalma / θala actual:"),
      span(() => `${currentWebTempC.val.toFixed(0)}°C / ${currentFlangeTempC.val.toFixed(0)}°C`),
    ),
    div(
      { class: "sf-row" },
      label("Conductividad ka:"),
      span(() => `${kEnd.val} W/mK`),
    ),
  ),
);

const right = div(
  { class: "sf-panel right" },
  getThermalGraphs({
    timesMin,
    gasTempC,
    webTempC,
    flangeTempC,
    kyWeb,
  }),
);

document.body.appendChild(
  div(
    { class: "sf-layout" },
    left,
    getViewer3D({
      mapping,
      currentWebTempC,
      currentFlangeTempC,
    }),
    right,
  ),
);
