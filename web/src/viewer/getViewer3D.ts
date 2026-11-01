import * as THREE from "three";
import van, { type State } from "vanjs-core";
import type { ThermalSectionMapping } from "../data-model";

export function getViewer3D({
  mapping,
  currentWebTempC,
  currentFlangeTempC,
}: {
  mapping: State<ThermalSectionMapping>;
  currentWebTempC: State<number>;
  currentFlangeTempC: State<number>;
}): HTMLElement {
  const container = document.createElement("div");
  container.className = "sf-viewer";

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 1, 5000);
  camera.position.set(320, -520, 260);
  camera.up.set(0, 0, 1);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  container.appendChild(renderer.domElement);

  const group = new THREE.Group();
  scene.add(group);

  function tempToColor(tempC: number): THREE.Color {
    const t = Math.min(Math.max((tempC - 20) / 1000, 0), 1);
    return new THREE.Color().setHSL(0.62 - t * 0.6, 0.92, 0.45 + 0.18 * t);
  }

  van.derive(() => {
    while (group.children.length > 0) group.remove(group.children[0]);
    const m = mapping.val;
    const tW = currentWebTempC.val;
    const tF = currentFlangeTempC.val;

    for (const [region, cellIndices] of m.regionToCells.entries()) {
      const temp = region === "web" ? tW : tF;
      const col = tempToColor(temp);
      for (const idx of cellIndices) {
        const c = m.cells[idx];
        const geom = new THREE.BoxGeometry(c.dxMm * 0.94, 380, c.dyMm * 0.94);
        const mat = new THREE.MeshBasicMaterial({ color: col });
        const box = new THREE.Mesh(geom, mat);
        box.position.set(c.xMm, 0, c.yMm);
        group.add(box);
      }
    }

    renderer.render(scene, camera);
  });

  const ro = new ResizeObserver(() => {
    const w = container.clientWidth || 700;
    const h = container.clientHeight || 500;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    renderer.render(scene, camera);
  });
  ro.observe(container);

  return container;
}
