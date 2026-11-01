import van, { type State } from "vanjs-core";

export function getThermalGraphs({
  timesMin,
  gasTempC,
  webTempC,
  flangeTempC,
  kyWeb,
}: {
  timesMin: State<number[]>;
  gasTempC: State<number[]>;
  webTempC: State<number[]>;
  flangeTempC: State<number[]>;
  kyWeb: State<number[]>;
}): HTMLElement {
  const wrap = document.createElement("div");
  wrap.style.display = "flex";
  wrap.style.flexDirection = "column";
  wrap.style.gap = "12px";

  const cTemp = document.createElement("canvas");
  cTemp.className = "sf-chart";
  const cKy = document.createElement("canvas");
  cKy.className = "sf-chart";

  const makeCard = (t: string, c: HTMLCanvasElement) => {
    const d = document.createElement("div");
    d.className = "sf-card";
    const h = document.createElement("h3");
    h.textContent = t;
    d.append(h, c);
    return d;
  };

  wrap.append(
    makeCard("Evolución Térmica θg(t), θalma(t), θala(t) [°C]", cTemp),
    makeCard("Factor de Retención de Fluencia ky,θ (EN 1993-1-2)", cKy),
  );

  van.derive(() => {
    const ts = timesMin.val;
    const tg = gasTempC.val;
    const tw = webTempC.val;
    const tf = flangeTempC.val;
    const ky = kyWeb.val;

    const ctx1 = cTemp.getContext("2d");
    if (ctx1 && ts.length > 1) {
      const w = (cTemp.width = cTemp.clientWidth || 320);
      const h = (cTemp.height = cTemp.clientHeight || 160);
      ctx1.clearRect(0, 0, w, h);
      const maxT = ts[ts.length - 1] || 1;
      const maxTemp = 1150;

      const plot = (vals: number[], color: string) => {
        ctx1.strokeStyle = color;
        ctx1.lineWidth = 1.8;
        ctx1.beginPath();
        ts.forEach((t, i) => {
          const px = 28 + (t / maxT) * (w - 38);
          const py = h - 20 - (vals[i] / maxTemp) * (h - 32);
          if (i === 0) ctx1.moveTo(px, py);
          else ctx1.lineTo(px, py);
        });
        ctx1.stroke();
      };
      plot(tg, "#f43f5e");
      plot(tw, "#f97316");
      plot(tf, "#38bdf8");
    }

    const ctx2 = cKy.getContext("2d");
    if (ctx2 && ts.length > 1) {
      const w = (cKy.width = cKy.clientWidth || 320);
      const h = (cKy.height = cKy.clientHeight || 160);
      ctx2.clearRect(0, 0, w, h);
      const maxT = ts[ts.length - 1] || 1;
      ctx2.strokeStyle = "#10b981";
      ctx2.lineWidth = 2;
      ctx2.beginPath();
      ts.forEach((t, i) => {
        const px = 28 + (t / maxT) * (w - 38);
        const py = h - 20 - ky[i] * (h - 32);
        if (i === 0) ctx2.moveTo(px, py);
        else ctx2.lineTo(px, py);
      });
      ctx2.stroke();
    }
  });

  return wrap;
}
