# steelfire

Acero estructural en situación de incendio: curvas de fuego (ISO 834, hidrocarburos, exterior, ASTM E119, RWS), temperatura del acero protegido y sin proteger según EN 1993-1-2, temperatura crítica, factores de reducción k_y, comprobación de resistencia al fuego por perfil y análisis térmico 2D por diferencias finitas.

[![CI](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Paquete independiente. Única dependencia obligatoria: `numpy`.

## Instalación

```bash
pip install git+https://github.com/jmurgass99/steelfire.git
```

Extras: `analytic` (curvas de fuego simbólicas con sympy), `memos` (memorias de cálculo con handcalcs), `api` (REST con FastAPI), `test`.

```bash
git clone https://github.com/jmurgass99/steelfire.git
cd steelfire
pip install -e ".[test,api,analytic,memos]"
pytest -q
```

## Inicio rápido

### Temperatura del gas ISO 834 y del acero (EN 1993-1-2)

```python
from steelfire.en_steel_temperature import iso834_gas, UnprotectedSteel, steel_temperature_at

iso834_gas(30.0)                                   # °C a los 30 min: 20 + 345·log10(8·30 + 1) ≈ 842 °C
sec = UnprotectedSteel(Am_V_1_m=150.0)                 # factor de sección Am/V en 1/m
steel_temperature_at(sec, duration_min=30.0)       # °C del acero tras 30 min de ISO 834
```

### Temperatura crítica y factor de reducción k_y

```python
from steelfire.en_steel_temperature import critical_temperature
from steelfire.iso834 import ky_from_temperature

critical_temperature(mu_0=0.65)   # θ_cr para un grado de utilización 0,65 (EN 1993-1-2 §4.2.4)
ky_from_temperature(600.0)        # k_y,θ a 600 °C (tabla 3.1)
```

### Análisis térmico 2D de una sección rectangular

```python
from steelfire import ThermalSection, solve_thermal

sec = ThermalSection(b=0.20, h=0.40, n_x=20, n_y=40, protection_thickness=0.0)
res = solve_thermal(sec, t_total=1800.0)   # 30 min de ISO 834, paso de tiempo por CFL
print(res.T_max_history[-1])                       # temperatura máxima final en la sección
```

## Módulos

| Módulo | Contenido |
|---|---|
| `en_steel_temperature` | Curva ISO 834, calor específico, acero protegido y sin proteger, temperatura crítica, comprobación por perfil y por clase de resistencia (R30, R60, …) |
| `iso834` | Evaluador simplificado y factor k_y,θ |
| `fire_curves_sympy` | Curvas de fuego nominales y paramétricas en forma simbólica (extra `analytic`) |
| `thermal_fea`, `fem_thermal_1d`, `thermal_iter` | Diferencias finitas 2D y 1D, iteración térmica |
| `protection_catalog` | Catálogo de materiales de protección |
| `fire_load_density`, `retention_multi`, `concrete_fire` | Densidad de carga de fuego, retención de resistencia multinorma, hormigón al fuego |
| `memos/` | Memorias de cálculo paso a paso (extra `memos`) |
| `api/` | REST API con FastAPI (extra `api`) |

## Validación

Las temperaturas del gas y del acero se comprueban contra la expresión de EN 1991-1-2 §3.2.1 y el método incremental de EN 1993-1-2 §4.2.5; los tests marcados `characterization` capturan el estado actual de la implementación y se declaran como tales, no como valores normativos.

## Licencia

MIT. Consulta [LICENSE](LICENSE).

---

Parte del toolkit estructural de código abierto **Loadpath**, de [Jesús Murgas](https://github.com/jmurgass99).
