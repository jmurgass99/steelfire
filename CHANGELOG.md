# Changelog

## 1.2.1 — 2026-11-02

- `en_steel_temperature.parametric_fire_gas` (curva paramétrica de EN 1991-1-2 Anexo A, añadida en aa269db): en los fuegos controlados por el combustible (t_max = t_lim) la fase de enfriamiento tomaba Θ_max y t*_max con Γ·t_lim. Según A.10–A.12, Θ_max es la temperatura al final del calentamiento con Γ_lim, y t*_max = (0,2·10⁻³·q_t,d/O)·Γ. Con O = 0,10 y q_t,d = 150 MJ/m², Θ_g saltaba de 818 a 1052 °C en t = 20 min; ahora es continua (`tests/test_parametric_fire_annex_a.py`, con el enfriamiento rehecho a mano).

## 1.2.0 — 2026-10-31

Correcciones encontradas al ejecutar los casos de uso del README.

- `thermal_fea.solve_thermal`: la conducción se aplica ahora a toda la malla con nodos fantasma de gradiente nulo. Antes el laplaciano solo actualizaba el interior y las celdas de borde recibían el flujo del gas sin cederlo hacia dentro: la temperatura media de una sección 200x200 a 10 min daba 132/208/324 °C con 5/10/20 divisiones y una barra de 60 mm calentaba casi el doble que el modelo de masa concentrada de EN 1993-1-2 §4.2.5.1. Ahora la media converge con la malla (±2 %) y coincide con la masa concentrada en pocos °C (`tests/test_thermal_fea_energy_consistency.py`). Los resultados de `services.thermal` y de la API cambian en consecuencia.
- `retention_multi.retention_factor`: la rama US/CO usa AISC 360-16/22 Apéndice 4, Tabla A-4.2.1 (k_E, k_p, k_y en nodos de °F, valores adoptados del Eurocódigo). La versión anterior usaba una «aproximación cuadrática» sin fuente que daba k_E = 0 a 400 °C y rechazaba k_p alegando que AISC no lo define, cuando la tabla lo tabula.
- 27 casos de uso ejecutados en `examples/` con su salida en `examples/output/`; README reescrito; metadatos del paquete alineados.

## 1.1.0

Chequeo por perfil con veredicto por comparación térmica real, recubrimientos reactivos verificados solo por tabla de ensayo, clasificaciones EN 13501-2 comparadas en minutos y por prestación.

## 1.0.0

Publicación inicial como repositorio independiente (origen: FireSteelJm del monorepo Structural JM).
