# steelfire — acero estructural en situación de incendio (EN 1993-1-2)

**Español** · [English](README.en.md) · [Português](README.pt.md) · [Italiano](README.it.md)

Temperatura del acero sin proteger y protegido bajo las curvas nominales de fuego (EN 1993-1-2 §4.2.5, ec. 4.25 y 4.27), temperatura crítica por grado de utilización (§4.2.4), factores de reducción k_y, k_E y k_p (Tabla 3.1 y AISC 360 Apéndice 4), comprobación de la clase R exigida con la protección pasiva del catálogo, solvers térmicos 2D y 1D, métodos de la isoterma de 500 °C y de las zonas para hormigón (EN 1992-1-2 Anexo B) y densidad de carga de fuego. Solo depende de `numpy`; las funciones están ancladas a ejercicios resueltos de examen y a la aritmética de la norma.

[![CI](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Qué problema resuelve

Tienes un perfil con su factor de sección Am/V, un grado de utilización en situación de incendio y una clase exigida (R30, R60, R90) y necesitas saber a qué temperatura llega, a cuál falla y si la protección propuesta lo deja por debajo. El paquete hace esa cadena completa y se niega a dar veredicto cuando no puede calcularlo (pinturas intumescentes sin tabla de ensayo). Las solicitaciones en situación de incendio y el grado de utilización los traes tú.

**Úsalo cuando**

- necesites la temperatura del acero bajo ISO 834, hidrocarburos u otra curva para un Am/V dado, con o sin capa inerte de protección;
- quieras la temperatura crítica de un elemento y el instante en que la alcanza (tiempo de colapso) para R30/R60/R90;
- dimensiones el espesor de mortero o placa para una clase, o quieras los factores k_y, k_E, k_p para degradar un modelo de barras paso a paso;
- compares protecciones del catálogo por clase y coste y necesites un chequeo con veredicto trazable;
- hagas un cribado térmico 2D de una sección maciza o un pilar de hormigón por isoterma de 500 °C o zonas.

**No lo uses para**

- obtener solicitaciones ni grados de utilización: no hay análisis estructural;
- verificar pinturas intumescentes sin el informe de ensayo del fabricante: el chequeo responde NO_VERIFICADO, por diseño;
- secciones compuestas acero-hormigón (EN 1994-1-2) o madera: no están;
- fuegos paramétricos de EN 1991-1-2 Anexo A: solo las curvas nominales (la API anuncia «paramétrica» pero sirve ISO 834, hidrocarburos y externa);
- AS 4100: el código AU se enruta a la tabla de EN 1993-1-2 sin ajustes (un test lo documenta).

## Instalación

```bash
pip install git+https://github.com/jmurgass99/steelfire.git
pip install "steelfire[analytic,memos,api] @ git+https://github.com/jmurgass99/steelfire.git"   # curvas simbólicas (sympy), memorias (handcalcs), API REST
```

Para desarrollo: `git clone`, `pip install -e ".[test,api,analytic,memos]"`, `pytest -q` (20 ficheros de tests). En Windows, si la consola no es UTF-8, ejecuta los ejemplos con `python -X utf8 examples/<nombre>.py`.

## Capacidades

| Capacidad | Módulos | Norma o referencia | Casos de uso |
|---|---|---|---|
| Curvas de fuego y temperatura del acero: ISO 834, hidrocarburos, externa, ASTM E119, RWS; método incremental sin proteger (con k_sh) y protegido; calor específico | `en_steel_temperature`, `fire_curves_sympy` | EN 1991-1-2 §3.2; EN 1993-1-2 §3.4.1.2, §4.2.5.1 (ec. 4.25, 4.26a), §4.2.5.2 (ec. 4.27) | [6 casos](#1-curvas-de-fuego-y-temperatura-del-acero) |
| Temperatura crítica, factores de reducción multinorma, historia térmica para modelos de barras, memoria de cálculo | `en_steel_temperature`, `iso834`, `thermal_iter`, `retention_multi`, `memos` | EN 1993-1-2 §4.2.4 (ec. 4.22), §3.2.1 Tabla 3.1; AISC 360-16/22 Ap. 4 Tabla A-4.2.1 | [5 casos](#2-temperatura-crítica-factores-de-reducción-y-tiempo-de-colapso) |
| Comprobación por perfil y protección pasiva: clase exigida, catálogo con método de verificación (capa inerte o ensayo certificado), clasificaciones EN 13501-2 | `en_steel_temperature.check_fire_resistance_from_profile`, `protection_catalog` | EN 1993-1-2 §4.2.5.2; EN 13501-2; UL 263 / EN 13381-8 | [5 casos](#3-comprobación-por-perfil-y-protección-pasiva) |
| Análisis térmico 2D por diferencias finitas y 1D por elementos finitos, servicio tipado | `thermal_fea`, `fem_thermal_1d`, `services.thermal` | Ecuación del calor con flujo convectivo-radiativo (EN 1991-1-2 §3.1) | [5 casos](#4-análisis-térmico-2d-y-1d) |
| Hormigón al fuego y carga de fuego: isoterma de 500 °C, zonas, distancia al eje por clase, k_c y k_s; q_f,d y duración equivalente | `concrete_fire`, `fire_load_density` | EN 1992-1-2 Anexo B.1/B.2, Tablas 3.1, 3.2a, 5.2a, 5.5, 5.8; EN 1991-1-2 Anexo E | [5 casos](#5-hormigón-al-fuego-y-carga-de-fuego) |
| API REST | `api` | — | [1 caso](#6-api-rest) |

Los 27 scripts de `examples/` se ejecutaron en un entorno limpio antes de publicarse; su salida está en `examples/output/` y es la que se reproduce aquí.

## Casos de uso

### 1. Curvas de fuego y temperatura del acero

#### Perfil sin proteger y con vermiculita bajo ISO 834: cuándo se alcanza θ_cr

Am/V = 150 m⁻¹, μ₀ = 0,6. Método incremental de §4.2.5 con Δt = 5 s; la protección de 20 mm lleva el instante crítico de 12 a 90 minutos.

<details><summary>Salida real de <code>python examples/protected_vs_unprotected_steel_iso834_en1993_1_2.py</code></summary>

```text
Temperatura crítica para μ₀ = 0.6: θ_cr = 554 °C

t [min]      gas  sin prot.  vermiculita 20 mm
      0       20         20                 20
      5      576        237                 38
     10      678        491                 73
     15      739        646                112
     20      781        723                150
     30      842        815                223
     45      902        895                324
     60      945        941                412
     90     1006       1003                554
    120     1049       1047                660

sin protección: θ_cr se alcanza a los 11.8 min

con vermiculita: θ_cr se alcanza a los 90.0 min
```

</details>

#### Las cinco curvas nominales con derivada e integral simbólicas

Tabla de temperaturas del gas, gradiente térmico de ISO 834 en los primeros minutos y energía acumulada en una hora (extra `analytic`).

<details><summary>Salida real de <code>python examples/fire_curves_iso834_hydrocarbon_external_astm_rws_comparison.py</code></summary>

```text
t [min] |     ISO 834 | Hydrocarbon |    External |   ASTM E119 | RWS (Rijkswaterstaat)
      0 |          20 |          20 |          20 |          20 |          20
      5 |         576 |         948 |         588 |         568 |        1140
     10 |         678 |        1034 |         662 |         680 |        1200
     15 |         739 |        1071 |         676 |         743 |        1225
     30 |         842 |        1098 |         680 |         839 |        1300
     60 |         945 |        1100 |         680 |         924 |        1350
     90 |        1006 |        1100 |         680 |         972 |        1300
    120 |        1049 |        1100 |         680 |        1007 |        1200

ISO 834: theta_g(t) = 20 + 345*log10(8t + 1)
  LaTeX: \frac{345 \log{\left(8 t + 1 \right)}}{\log{\left(10 \right)}} + 20
  dθ/dt a  1 min =   133.2 °C/min
  dθ/dt a  5 min =    29.2 °C/min
  dθ/dt a 15 min =     9.9 °C/min
  dθ/dt a 30 min =     5.0 °C/min
  dθ/dt a 60 min =     2.5 °C/min
  ∫₀⁶⁰ θ_g dt = 47846 °C·min  (media 797 °C en la primera hora)
Hydrocarbon: ∫₀⁶⁰ θ_g dt = 63607 °C·min  (media 1060 °C)
```

</details>

#### Barrido del factor de sección: de un perfil macizo a una chapa fina

Temperatura a 15, 30 y 60 min y tiempo en alcanzar 500 °C para Am/V de 50 a 300 m⁻¹.

<details><summary>Salida real de <code>python examples/unprotected_steel_heating_section_factor_sweep.py</code></summary>

```text
Gas ISO 834: 15 min → 739 °C, 30 min → 842 °C, 60 min → 945 °C

Am/V [1/m]  θ 15 min  θ 30 min  θ 60 min  t(500 °C)
        50       383       690       923   19.6 min
       100       565       767       938   12.9 min
       150       646       815       941   10.2 min
       200       682       828       942    8.8 min
       300       708       835       943    7.1 min

Por encima de Am/V ≈ 100 m⁻¹ el acero sigue al gas con poco retraso: sin protección no hay R30 salvo con grados de utilización muy bajos.
```

</details>

#### Efecto sombra en perfiles en I (ec. 4.26a)

k_sh a partir del factor de sección encajonado y su efecto en el calentamiento a 30 min. El módulo implementa solo la ec. 4.26a; la 4.26b (otras secciones) no está.

<details><summary>Salida real de <code>python examples/shadow_factor_i_section_boxed_section_factor.py</code></summary>

```text
perfil     Am/V  [Am/V]_b   k_sh |  θ 30 min k_sh=1  θ 30 min con k_sh
IPE 300     200       140  0.630 |              828                798
IPE 500     150       110  0.660 |              815                766
HEB 300     115        85  0.665 |              787                738

k_sh solo depende del cociente [Am/V]_b/[Am/V]; el chequeo por perfil del paquete usa k_sh = 0,90 por defecto.
```

</details>

#### Espesor de placa para R60 y R90 (ec. 4.27)

Placa de silicato cálcico sobre una viga con Am/V = 200 m⁻¹: la primera fila que cumple marca el espesor mínimo a pedir al fabricante.

<details><summary>Salida real de <code>python examples/protected_steel_board_thickness_selection_r60_r90.py</code></summary>

```text
Am/V = 200 m⁻¹, μ₀ = 0.6 → θ_cr = 554 °C; placa λ_p = 0.17 W/mK

d_p [mm]  θ 60 min   R60  θ 90 min   R90
    12.5       698    NO       795    NO
    15.0       652    NO       748    NO
    20.0       566    NO       708    NO
    25.0       492    OK       642    NO
    30.0       428    OK       578    NO
    40.0       327    OK       467    OK

La ec. 4.27 anula el enfriamiento ficticio del término exponencial mientras el gas sube; el espesor final debe tomarse del catálogo del fabricante para ese A_p/V.
```

</details>

#### El pico del calor específico a 735 °C y la meseta de calentamiento

c_a(θ) por tramos (§3.4.1.2) y velocidad de calentamiento medida por franjas: el perfil frena al acercarse a 735 °C.

<details><summary>Salida real de <code>python examples/specific_heat_peak_735c_and_heating_rate.py</code></summary>

```text
 θ [°C]  c_a [J/kgK]
     20        439.8
    200        529.8
    400        605.9
    600        760.2
    700       1008.2
    720       1388.3
    730       2291.2
    734       3916.5
    736       4109.0
    740       2525.0
    760       1159.5
    800        803.3
    900        650.0
   1000        650.0

Velocidad media de calentamiento por franja (Am/V = 150 m⁻¹, ISO 834):
  100–300 °C:   54.5 °C/min  (de 2.5 a 6.2 min)
  300–500 °C:   49.0 °C/min  (de 6.2 a 10.2 min)
  500–650 °C:   30.0 °C/min  (de 10.2 a 15.2 min)
  650–720 °C:   15.6 °C/min  (de 15.2 a 19.8 min)
  720–750 °C:    6.2 °C/min  (de 19.8 a 24.6 min)
  750–800 °C:   12.2 °C/min  (de 24.6 a 28.7 min)
```

</details>

### 2. Temperatura crítica, factores de reducción y tiempo de colapso

#### Temperatura crítica en cinco casos de examen del máster (ficha W01437)

Cada μ₀ fue resuelto a mano por el alumno; la ec. 4.22 los reproduce al décimo de grado. Fuera de dominio la función lanza ValueError.

<details><summary>Salida real de <code>python examples/critical_temperature_exam_cases_w01437.py</code></summary>

```text
    μ₀  θ_cr [°C]    ficha  caso
 0.484      589.9    589.9  GT3 viga IPE 550 / S235
 0.430      608.6    609.0  GT4 viga IPE 270 / S235
 0.280      674.2    674.0  GT4 tirante 2L 40x4
 0.160      758.5    758.5  GT1/GT5 columna HEB 220/240
 0.571      562.8    563.0  GT5 columna HEB 220 (método del pandeo)

Variante simbólica (sympy), μ₀ = 0,16: 758.55 °C

Curva completa:
  μ₀ = 0.1 → θ_cr =  829.2 °C
  μ₀ = 0.2 → θ_cr =  725.0 °C
  μ₀ = 0.3 → θ_cr =  663.8 °C
  μ₀ = 0.4 → θ_cr =  619.8 °C
  μ₀ = 0.5 → θ_cr =  584.7 °C
  μ₀ = 0.6 → θ_cr =  554.3 °C
  μ₀ = 0.7 → θ_cr =  525.8 °C
  μ₀ = 0.8 → θ_cr =  496.1 °C
  μ₀ = 0.9 → θ_cr =  458.4 °C
  μ₀ = 1.0 → θ_cr =  349.1 °C

μ₀ = 1,05 → ValueError: mu_0 fuera del dominio de EN 1993-1-2 §4.2.4: recibido 1.05. El grado de utilizacion debe cumplir 0 < mu_0 <= 1.
```

</details>

#### k_y, k_E y k_p de la Tabla 3.1 y dos casos del máster (fichas W01409 y W01411)

Tabla completa con interpolación y los valores de examen; la ficha W01411 imprime k_E = 0,4004 donde la tabla da 0,4034 (errata documentada, se ancla el valor recalculado).

<details><summary>Salida real de <code>python examples/reduction_factors_ky_ke_kp_table_3_1_w01409_w01411.py</code></summary>

```text
 θ [°C]   k_y,θ   k_p,θ   k_E,θ
     20   1.000   1.000   1.000
    100   1.000   1.000   1.000
    200   1.000   0.807   0.900
    300   1.000   0.613   0.800
    400   1.000   0.420   0.700
    500   0.780   0.360   0.600
    600   0.470   0.180   0.310
    700   0.230   0.075   0.130
    800   0.110   0.050   0.090
    900   0.060   0.037   0.068
   1000   0.040   0.025   0.045
   1100   0.020   0.013   0.022

Casos del máster:
  W01409  θ_a = 595,5 °C → k_y = 0.4839  (ficha 0,4840)
  W01411  θ_a = 567,8 °C → k_y = 0.5698, k_E = 0.4034  (ficha 0,5698 / 0,4004 errata)

ky_from_temperature(650) = 0.350 (misma tabla, módulo iso834)
k_y(1150) = 0.010; k_y(1250) = 0.000 (por encima de 1 200 °C vale 0, no un residuo constante)
```

</details>

#### Factores de retención por norma: EN 1993-1-2 frente a AISC 360 Apéndice 4

AISC adopta los valores del Eurocódigo en nodos de °F: k_E y k_y coinciden en los nodos, k_p queda hasta 0,04 por debajo entre 300 y 500 °C. Hasta esta versión la rama US usaba una cuadrática sin fuente que daba k_E = 0 a 400 °C.

<details><summary>Salida real de <code>python examples/retention_factors_multicode_eu_us_au.py</code></summary>

```text
 θ [°C] |  k_E EU  k_E US |  k_y EU  k_y US |  k_p EU  k_p US
     20 |   1.000   1.000 |   1.000   1.000 |   1.000   1.000
    204 |   0.896   0.900 |   1.000   1.000 |   0.799   0.807
    300 |   0.800   0.797 |   1.000   1.000 |   0.613   0.641
    399 |   0.701   0.700 |   1.000   1.000 |   0.422   0.420
    500 |   0.600   0.552 |   0.780   0.756 |   0.360   0.242
    538 |   0.490   0.490 |   0.662   0.660 |   0.292   0.180
    600 |   0.310   0.339 |   0.470   0.487 |   0.180   0.121
    700 |   0.130   0.169 |   0.230   0.263 |   0.075   0.064
    800 |   0.090   0.096 |   0.110   0.128 |   0.050   0.045

AU sigue la tabla EN: k_y(600, AU) = 0.470
retention_factor(400, 'fy', 'EU') → ValueError: magnitud 'fy' no soportada; use uno de ['E', 'Fy', 'kp'] (distingue mayúsculas)
retention_factor(400, 'Fy', 'BR') → ValueError: código 'BR' no soportado
```

</details>

#### Historia térmica para un modelo de barras: modificadores de E y f_y y tiempo de colapso

k_E y k_y por paso de tiempo a partir de la temperatura del acero, listos para reasignar como «Property Modifiers», y el instante en que k_y cae por debajo de μ₀.

<details><summary>Salida real de <code>python examples/thermal_history_property_modifiers_and_collapse_time.py</code></summary>

```text
t [min]  θ_a [°C]    k_E    k_y  modificadores
      0        20  1.000  1.000  E×1.000, Fy×1.000 → ['IPE300_fire']
      5       220  0.880  1.000  E×0.880, Fy×1.000 → ['IPE300_fire']
     10       466  0.634  0.856  E×0.634, Fy×0.856 → ['IPE300_fire']
     15       628  0.260  0.403  E×0.260, Fy×0.403 → ['IPE300_fire']
     20       715  0.124  0.212  E×0.124, Fy×0.212 → ['IPE300_fire']
     25       746  0.112  0.175  E×0.112, Fy×0.175 → ['IPE300_fire']
     30       806  0.089  0.107  E×0.089, Fy×0.107 → ['IPE300_fire']
     35       848  0.079  0.086  E×0.079, Fy×0.086 → ['IPE300_fire']
     40       874  0.073  0.073  E×0.073, Fy×0.073 → ['IPE300_fire']
     45       894  0.069  0.063  E×0.069, Fy×0.063 → ['IPE300_fire']
     50       911  0.065  0.058  E×0.065, Fy×0.058 → ['IPE300_fire']
     55       926  0.062  0.055  E×0.062, Fy×0.055 → ['IPE300_fire']
     60       940  0.058  0.052  E×0.058, Fy×0.052 → ['IPE300_fire']

μ₀ = 0.3: k_y cae por debajo de μ₀ a los 20 min (malla de 5 min)

μ₀ = 0.5: k_y cae por debajo de μ₀ a los 15 min (malla de 5 min)

μ₀ = 0.7: k_y cae por debajo de μ₀ a los 15 min (malla de 5 min)
```

</details>

#### Memoria de temperatura crítica y tiempo de colapso (extra `memos`)

Viga IPE 300 sin proteger (R30) y con placa de 20 mm (R60): θ_cr, t_cr, veredicto y la memoria en Markdown.

<details><summary>Salida real de <code>python examples/critical_temperature_memo_markdown_collapse_time.py</code></summary>

```text
Sin proteger: μ₀ = 0.55, θ_cr = 569.1 °C, t_cr = 11.0 min → R30 NO CUMPLE
Con placa 20 mm: θ_cr = 569.1 °C, t_cr = 58.8 min → R60 NO CUMPLE

--- Markdown (primeras líneas, caso sin proteger) ---
# Memoria -- Temperatura critica del acero (EN 1993-1-2)

**Elemento:** beam
**Seccion:** IPE 300 (sin proteger)
**Factor de seccion:** Am/V = 200 m^-1
**Factor de sombra:** ksh = 0.90

## Nivel de carga

$$\mu_0 = \frac{E_{fi}}{R_{fi,20°C}} = 0.5500$$

## Temperatura critica

$$\theta_{cr} = 39.19 \cdot \ln\!\left(\frac{1}{0.9674 \cdot \mu_0^{3.833}} - 1\right) + 482 = 569.1\;°C$$

## Tiempo de colapso (ISO 834)

$$\theta_a(t_{cr}) = \theta_{cr} \Rightarrow t_{cr} = 11.0\;\text{min}$$

## Verificacion

Resistencia requerida: R = 30 min

LaTeX: 242 caracteres
```

</details>

### 3. Comprobación por perfil y protección pasiva

#### Chequeo de clase exigida por perfil con mortero, placa e intumescente

Con capa inerte el paquete aplica el espesor medio del producto, integra la ec. 4.27 y compara con θ_cr; con pintura intumescente y sin tabla de ensayo no hay veredicto.

<details><summary>Salida real de <code>python examples/fire_rating_check_by_profile_r30_r60_r90.py</code></summary>

```text
IPE 300 (viga de forjado) — Am/V = 200 m⁻¹, μ₀ = 0.55, exigido R30 (30 min), protección spray
  θ_cr = 569 °C | θ sin protección a 30 min = 825 °C
  ¿requiere protección? sí
  protección propuesta: {'code': 'UL 60-spray-mortar', 'type': 'spray_mortar', 'verification_method': 'inert_layer', 'thickness_mm': 25.0, 'thickness_range_mm': (15.0, 35.0), 'cost_USD_per_m2': 35.0, 'rating_minutes': 60}
  θ con protección = 223 °C
  estado: CON_PROTECCION_CUMPLE | seguro: True
  nota: Temperatura protegida calculada con Ap/V = Am/V (proteccion siguiendo el contorno) y espesor 25.00 mm (medio del rango tipico).

IPE 300 (viga de forjado) — Am/V = 200 m⁻¹, μ₀ = 0.55, exigido R60 (60 min), protección board
  θ_cr = 569 °C | θ sin protección a 60 min = 941 °C
  ¿requiere protección? sí
  protección propuesta: {'code': 'EN 90-board-cem', 'type': 'board', 'verification_method': 'inert_layer', 'thickness_mm': 18.75, 'thickness_range_mm': (12.5, 25.0), 'cost_USD_per_m2': 55.0, 'rating_minutes': 90}
  θ con protección = 599 °C
  estado: CON_PROTECCION_NO_CUMPLE | seguro: False
  nota: Temperatura protegida calculada con Ap/V = Am/V (proteccion siguiendo el contorno) y espesor 18.75 mm (medio del rango tipico).
  nota: El espesor propuesto (18.75 mm) no basta: theta = 599.0 C > theta_crit = 569.1 C.

HEB 300 (pilar) — Am/V = 115 m⁻¹, μ₀ = 0.65, exigido R60 (60 min), protección spray
  θ_cr = 540 °C | θ sin protección a 60 min = 938 °C
  ¿requiere protección? sí
  protección propuesta: {'code': 'UL 60-spray-mortar', 'type': 'spray_mortar', 'verification_method': 'inert_layer', 'thickness_mm': 25.0, 'thickness_range_mm': (15.0, 35.0), 'cost_USD_per_m2': 35.0, 'rating_minutes': 60}
  θ con protección = 300 °C
  estado: CON_PROTECCION_CUMPLE | seguro: True
  nota: Temperatura protegida calculada con Ap/V = Am/V (proteccion siguiendo el contorno) y espesor 25.00 mm (medio del rango tipico).

HEB 300 (pilar) — Am/V = 115 m⁻¹, μ₀ = 0.65, exigido R90 (90 min), protección board
  θ_cr = 540 °C | θ sin protección a 90 min = 1002 °C
  ¿requiere protección? sí
  protección propuesta: {'code': 'EN 90-board-cem', 'type': 'board', 'verification_method': 'inert_layer', 'thickness_mm': 18.75, 'thickness_range_mm': (12.5, 25.0), 'cost_USD_per_m2': 55.0, 'rating_minutes': 90}
  θ con protección = 624 °C
  estado: CON_PROTECCION_NO_CUMPLE | seguro: False
  nota: Temperatura protegida calculada con Ap/V = Am/V (proteccion siguiendo el contorno) y espesor 18.75 mm (medio del rango tipico).
  nota: El espesor propuesto (18.75 mm) no basta: theta = 623.9 C > theta_crit = 540.0 C.

HEB 300 (pilar) — Am/V = 115 m⁻¹, μ₀ = 0.65, exigido R60 (60 min), protección intumescent
  θ_cr = 540 °C | θ sin protección a 60 min = 938 °C
  ¿requiere protección? sí
  estado: NO_VERIFICADO | seguro: None
  nota: UL 60-INT-acrylic es un recubrimiento reactivo: EN 1993-1-2 4.2.5.2 (capa inerte) no le aplica y su lambda_p de pelicula seca no representa la espuma expandida. Se verifica por espesor certificado de ensayo (UL 263 / EN 13381-8) y el catalogo no tiene ninguna fila que cubra R60 hasta Am/V = 115 1/m. Sin dato certificado no hay veredicto: se requiere el informe de ensayo del fabricante.
```

</details>

#### Pilar HEB 300: R60 y R90 con mortero o placa, y espesor mínimo que cumple

Cuando el espesor medio del catálogo no basta, el estado es CON_PROTECCION_NO_CUMPLE y se busca el espesor mínimo milímetro a milímetro.

<details><summary>Salida real de <code>python examples/spray_mortar_protection_check_heb300_column_r60_r90.py</code></summary>

```text
R60 con spray: θ_cr = 540 °C, θ sin proteger = 938 °C; UL 60-spray-mortar 25.0 mm → θ_prot = 300 °C; estado CON_PROTECCION_CUMPLE
R90 con spray: θ_cr = 540 °C, θ sin proteger = 1002 °C; sin producto evaluado; estado NO_VERIFICADO
R90 con board: θ_cr = 540 °C, θ sin proteger = 1002 °C; EN 90-board-cem 18.8 mm → θ_prot = 624 °C; estado CON_PROTECCION_NO_CUMPLE
R120 con board: θ_cr = 540 °C, θ sin proteger = 1046 °C; EN 120-board-silic 30.0 mm → θ_prot = 552 °C; estado CON_PROTECCION_NO_CUMPLE

Espesor mínimo de EN 90-board-cem para R90 (θ_cr = 540 °C):
  d_p =  8 mm → θ(90 min) =   818 °C 
  d_p = 10 mm → θ(90 min) =   755 °C 
  d_p = 12 mm → θ(90 min) =   733 °C 
  d_p = 14 mm → θ(90 min) =   709 °C 
  d_p = 16 mm → θ(90 min) =   673 °C 
  d_p = 18 mm → θ(90 min) =   637 °C 
  d_p = 20 mm → θ(90 min) =   603 °C 
  d_p = 22 mm → θ(90 min) =   570 °C 
  d_p = 24 mm → θ(90 min) =   540 °C OK
```

</details>

#### Pintura intumescente: sin tabla de ensayo no hay veredicto; con ella, verificación certificada

Se carga una fila ILUSTRATIVA (no es un dato real) para mostrar el camino por clasificación certificada y que fuera del Am/V ensayado no se extrapola.

<details><summary>Salida real de <code>python examples/intumescent_coating_certified_test_data_required.py</code></summary>

```text
Catálogo tal cual: estado = NO_VERIFICADO, is_safe = None
  nota: UL 60-INT-acrylic es un recubrimiento reactivo: EN 1993-1-2 4.2.5.2 (capa inerte) no le aplica y su lambda_p de pelicula seca no representa la espuma expandida. Se verifica por espesor certificado de ensayo (UL 263 / EN 13381-8) y el catalogo no tiene ninguna fila que cubra R60 hasta Am/V = 200 1/m. Sin dato certificado no hay veredicto: se requiere el informe de ensayo del fabricante.

Producto UL 60-INT-acrylic con una fila de ensayo cargada (certified_test):
  Am/V = 150 m⁻¹ → R60 con 1.20 mm (hasta 220 m⁻¹); fuente: fila ILUSTRATIVA de este ejemplo; sustituir por el DoP / informe UL del fabricante
  Am/V = 200 m⁻¹ → R60 con 1.20 mm (hasta 220 m⁻¹); fuente: fila ILUSTRATIVA de este ejemplo; sustituir por el DoP / informe UL del fabricante
  Am/V = 250 m⁻¹ → sin fila aplicable (no se extrapola fuera del Am/V ensayado)
  requisito R90 con la misma fila → None
```

</details>

#### Catálogo de protecciones: recomendar por clase y presupuesto

<details><summary>Salida real de <code>python examples/protection_catalog_recommend_by_rating_and_budget.py</code></summary>

```text
Catálogo completo (6 productos):
  UL 60-INT-acrylic    intumescent   R60      45 USD/m²  d = 0.6–3.0 mm  λ_p = —     certified_test
  UL 120-INT-epoxy     intumescent   R120     85 USD/m²  d = 1.2–6.0 mm  λ_p = —     certified_test
  UL 60-spray-mortar   spray_mortar  R60      35 USD/m²  d = 15.0–35.0 mm  λ_p = 0.12  inert_layer
  EN 90-board-cem      board         R90      55 USD/m²  d = 12.5–25.0 mm  λ_p = 0.20  inert_layer
  EN 120-board-silic   board         R120     70 USD/m²  d = 20.0–40.0 mm  λ_p = 0.17  inert_layer
  Concrete-R180        concrete      R180     25 USD/m²  d = 30.0–60.0 mm  λ_p = 1.40  inert_layer

Candidatos para R60, por coste:
  Concrete-R180        concrete      R180     25 USD/m²  d = 30.0–60.0 mm  λ_p = 1.40  inert_layer
  UL 60-spray-mortar   spray_mortar  R60      35 USD/m²  d = 15.0–35.0 mm  λ_p = 0.12  inert_layer
  UL 60-INT-acrylic    intumescent   R60      45 USD/m²  d = 0.6–3.0 mm  λ_p = —     certified_test
  EN 90-board-cem      board         R90      55 USD/m²  d = 12.5–25.0 mm  λ_p = 0.20  inert_layer
  EN 120-board-silic   board         R120     70 USD/m²  d = 20.0–40.0 mm  λ_p = 0.17  inert_layer
  UL 120-INT-epoxy     intumescent   R120     85 USD/m²  d = 1.2–6.0 mm  λ_p = —     certified_test

Candidatos para R90 con presupuesto ≤ 60 USD/m²:
  Concrete-R180        concrete      R180     25 USD/m²  d = 30.0–60.0 mm  λ_p = 1.40  inert_layer
  EN 90-board-cem      board         R90      55 USD/m²  d = 12.5–25.0 mm  λ_p = 0.20  inert_layer

Candidatos para R180:
  Concrete-R180        concrete      R180     25 USD/m²  d = 30.0–60.0 mm  λ_p = 1.40  inert_layer

lookup('EN 120-board-silic') → ρ_p = 450 kg/m³, c_p = 1100 J/kgK, filas certificadas: 0
```

</details>

#### Clasificaciones EN 13501-2: minutos y prestaciones (R, E, I)

«R120» cubre «R90» aunque como texto '1' < '9'; «R120» no cubre «EI90»; una cadena ininteligible lanza ValueError.

<details><summary>Salida real de <code>python examples/fire_rating_string_parsing_and_coverage_rules.py</code></summary>

```text
parse_fire_rating_minutes(     'R60') =    60 min
parse_fire_rating_minutes(    'R 90') =    90 min
parse_fire_rating_minutes(   'REI90') =    90 min
parse_fire_rating_minutes(  'REI-90') =    90 min
parse_fire_rating_minutes(    'EI30') =    30 min
parse_fire_rating_minutes( 'rei 120') =   120 min

¿cubre la certificación al requisito?
  REI120  → R90   : True
  R120    → EI90  : False
  R90     → R120  : False
  REI60   → REI60 : True
  REI90   → EI60  : True
  R120    → R90   : True

'R-abc' → ValueError: requisito de resistencia al fuego no interpretable: 'R-abc'. Formatos aceptados: letras de…

'60' → ValueError: requisito de resistencia al fuego no interpretable: '60'. Formatos aceptados: letras de cl…

'RX60' → ValueError: requisito de resistencia al fuego no interpretable: 'RX60'. Formatos aceptados: letras de …

'R0' → ValueError: requisito de resistencia al fuego no positivo: 'R0'. Formatos aceptados: letras de clase E…
```

</details>

### 4. Análisis térmico 2D y 1D

#### Sección rectangular 200×400 por diferencias finitas: cuatro caras, tres caras y con protección

<details><summary>Salida real de <code>python examples/thermal_fea_2d_rectangular_section_iso834.py</code></summary>

```text
Sección 200 x 400 mm, curva ISO 834

4 caras expuestas, sin protección          15 min: máx    232 / media    151 °C | 30 min: máx    444 / media    339 °C
3 caras expuestas (cara superior protegida) 15 min: máx    233 / media    131 °C | 30 min: máx    444 / media    295 °C
4 caras, 15 mm de protección (k = 0,12 W/mK) 15 min: máx     77 / media     55 °C | 30 min: máx    146 / media    114 °C
```

</details>

#### Barra maciza: solver 2D frente al modelo de masa concentrada de EN 1993-1-2

Con el mismo flujo neto, la media de la sección sigue la ec. 4.25 con diferencias de pocos °C. Hasta esta versión el solver calentaba casi el doble porque las celdas de borde no conducían hacia dentro.

<details><summary>Salida real de <code>python examples/thermal_2d_vs_lumped_en1993_1_2_massive_bar.py</code></summary>

```text
Barra 60×60 mm, Am/V = 66.7 m⁻¹, ISO 834

t [min]  2D media  2D máx  masa concentrada  dif. media
      5       131     141               130          +1
     10       297     310               297          -0
     15       458     470               460          -2
     20       585     596               589          -3
     25       677     686               681          -4
     30       730     738               732          -2
```

</details>

#### Refinamiento de malla y paso de tiempo por CFL

La media converge con la malla (±2 %); un Δt mayor que el límite lanza ValueError.

<details><summary>Salida real de <code>python examples/thermal_2d_mesh_refinement_and_cfl_time_step.py</code></summary>

```text
  n  Δx [mm]  Δt_max [s]   pasos  T_max 10 min  T_media
  5       40      29.656      60           148      119
 10       20       7.414     210           162      118
 20       10       1.853     810           169      117

Δt = 5·Δt_max → ValueError: dt=37.0694s viola CFL (dt_max=7.4139s). Reduce dt o aumenta resolución.

Diferencia de la media respecto a la malla de 20: n = 5 → +1.9%, n = 10 → +0.5%. La máxima (celda de esquina) sí depende del tamaño de celda.
```

</details>

#### Servicio tipado: viga bajo forjado (tres caras) frente a pilar (cuatro)

<details><summary>Salida real de <code>python examples/thermal_service_typed_api_three_sides_exposed.py</code></summary>

```text
viga 300x500, 3 caras (superior cubierta)    15 min: máx   217 / media    98 °C | 30 min: máx   402 / media   218 °C  (39 instantes guardados)
pilar 300x300, 4 caras                       15 min: máx   217 / media   136 °C | 30 min: máx   411 / media   306 °C  (39 instantes guardados)
pilar 300x300, 4 caras, 20 mm protección     15 min: máx    62 / media    45 °C | 30 min: máx   112 / media    87 °C  (39 instantes guardados)

n_x = 1 → ConfigurationError: n_x y n_y deben ser >= 2
```

</details>

#### Placa de protección y chapa de acero en 1D (elementos finitos, Crank-Nicolson)

<details><summary>Salida real de <code>python examples/thermal_1d_board_protected_steel_plate_crank_nicolson.py</code></summary>

```text
13 nodos; nodo de la interfaz placa-acero ≈ 6

t [min]    gas  cara expuesta  interfaz  cara fría
      0     20             20        20         20
      5    576            366        24         24
     10    678            480        39         38
     15    739            543        58         58
     20    781            586        79         79
     30    842            647       121        120
     40    885            691       160        159
     50    918            726       195        195
     60    945            756       227        227

La chapa queda casi isoterma (conductividad alta frente a la placa): el salto térmico lo absorbe la placa.
```

</details>

### 5. Hormigón al fuego y carga de fuego

#### Pilar de hormigón: isoterma de 500 °C y método de las zonas (EN 1992-1-2 Anexo B)

El perfil de temperaturas en el hormigón es un modelo semiempírico del paquete, no los perfiles del Anexo A: dimensionado previo.

<details><summary>Salida real de <code>python examples/concrete_column_isotherm_500_and_zone_method_en1992_1_2.py</code></summary>

```text
Isoterma 500 °C (Anexo B.1), pilar 300×300:
  R30   T_sup =   842 °C, a_500 =  17.2 mm → sección reducida 266 × 266 mm
  R60   T_sup =   945 °C, a_500 =  29.1 mm → sección reducida 242 × 242 mm
  R90   T_sup =  1006 °C, a_500 =  38.5 mm → sección reducida 223 × 223 mm
  R120  T_sup =  1049 °C, a_500 =  46.6 mm → sección reducida 207 × 207 mm

Método de las zonas (Anexo B.2), pilar 300×300, f_ck = 30 MPa:
  R30   a_z =   9.3 mm, k_c,m = 0.938, k_c(θ_M) = 1.000, N: 2700 → 2376 kN (88%)
  R60   a_z =  18.3 mm, k_c,m = 0.878, k_c(θ_M) = 1.000, N: 2700 → 2082 kN (77%)
  R90   a_z =  26.9 mm, k_c,m = 0.821, k_c(θ_M) = 1.000, N: 2700 → 1820 kN (67%)
  R120  a_z =  34.8 mm, k_c,m = 0.768, k_c(θ_M) = 1.000, N: 2700 → 1594 kN (59%)

Pilar 400×400 a R90: a_z = 23.6 mm, capacidad residual 78%
```

</details>

#### Distancia al eje de la armadura por clase R (método tabulado)

<details><summary>Salida real de <code>python examples/concrete_cover_axis_distance_for_r_rating_en1992_1_2.py</code></summary>

```text
column: dimensión disponible 300 mm
      R  b_min  a [mm]  cumple b_min
  R30      200      25  sí
  R60      250      46  sí
  R90      350      53  NO
  R120     350      57  NO
  R180     450      70  NO
  R240     450      75  NO
beam: dimensión disponible 250 mm
      R  b_min  a [mm]  cumple b_min
  R30       80      25  sí
  R60      120      40  sí
  R90      150      55  sí
  R120     200      65  sí
  R180     240      80  sí
  R240     280      90  NO
slab: dimensión disponible 150 mm
      R  b_min  a [mm]  cumple b_min
  R30       60      10  sí
  R60       80      20  sí
  R90      100      30  sí
  R120     120      40  sí
  R180     150      55  sí
  R240     175      65  NO

R100 (no tabulado) → se evalúa como R120: a = 57 mm
```

</details>

#### k_c del hormigón y k_s de la armadura frente a la temperatura

<details><summary>Salida real de <code>python examples/concrete_and_rebar_strength_reduction_tables.py</code></summary>

```text
 θ [°C]  k_c hormigón  k_s laminado  k_s estirado  k_y,θ EN 1993-1-2
     20          1.00          1.00          1.00               1.00
    100          1.00          1.00          1.00               1.00
    200          0.95          1.00          1.00               1.00
    300          0.85          1.00          1.00               1.00
    400          0.75          1.00          0.94               1.00
    500          0.60          0.78          0.67               0.78
    600          0.45          0.47          0.40               0.47
    700          0.30          0.23          0.12               0.23
    800          0.15          0.11          0.11               0.11
    900          0.08          0.06          0.08               0.06
   1000          0.04          0.04          0.05               0.04
   1100          0.01          0.02          0.03               0.02
   1200          0.00          0.00          0.00               0.00

Interpolación: k_c(450) = 0.675, k_s(650, estirado) = 0.260
```

</details>

#### Densidad de carga de fuego por uso y norma, valor de cálculo y duración equivalente

<details><summary>Salida real de <code>python examples/fire_load_density_by_occupancy_multicode.py</code></summary>

```text
q_f,k [MJ/m²] por uso y norma:
uso          |    EU |   USA |    AU |    SG |   NSR
vivienda     |   780 |   790 |   800 |   780 |   800
oficina      |   420 |   415 |   400 |   420 |   430
hospital     |   230 |   240 |   250 |   230 |   250
hotel        |   310 |   305 |   320 |   310 |   320
comercial    |   600 |   580 |   590 |   600 |   620
biblioteca   |  1500 |  1450 |  1480 |  1500 |  1480
industria    |  1180 |  1100 |  1200 |  1180 |  1200

Oficina EU de 600 m², con rociadores (δ_n = 0,61):
  q_f,k = 420 MJ/m², q_f,d = 246 MJ/m², energía total 148 GJ
  t_eq = 0,07·q_f,d = 17 min

Uso no tabulado → ValueError: Uso desconocido: aparcamiento
```

</details>

#### Del local a la viga: duración equivalente y temperatura del acero

<details><summary>Salida real de <code>python examples/compartment_equivalent_fire_duration_vs_steel_heating.py</code></summary>

```text
Viga Am/V = 200 m⁻¹, μ₀ = 0.6 → θ_cr = 554 °C

local                         q_f,d   t_eq | θ sin prot.     θ placa 20    
biblioteca sin rociadores      1440    101 |        1021  NO        737  NO
oficina con rociadores          246     17 |         705  NO        190  OK
vivienda                        624     44 |         892  NO        459  OK
```

</details>

### 6. API REST

#### Curvas, temperatura crítica y chequeo de perfil por HTTP, sin servidor

<details><summary>Salida real de <code>python examples/rest_api_fire_curves_critical_temperature_check_profile.py</code></summary>

```text
GET /api/thermal/health → {'status': 'ok'}

POST /fire/curve (hydrocarbon) → 200 {"curve_name": "Hydrocarbon", "expression": "theta_g(t) = 20 + 1080*(1 - 0.325*exp(-0.167t) - 0.675*exp(-2.5t))", "latex": "1100 - 729 e^{- \\frac{5 t}{2}} - 351 e^{- \\frac{167 t}{1000}}", "t_minutes": [0.0, 5.0, 30.0, 60.0], "theta_g_C": [20.0, 947.7073402868576, 1097.6585129395044, 1099.984380166

POST /fire/critical_temperature (μ = 0,16, caso W01437) → 200 {"utilization": 0.16, "critical_temperature_C": 758.5468453884962, "formula": "theta_a,cr = 39.19 * ln(1/(0.9674*mu^3.833) - 1) + 482  [EN 1993-1-2 §4.2.4]"}

POST /api/fire/check-profile (HEB 300, R90, placa) → 200
{"theta_crit_C": 540.0, "theta_unprotected_C": 1002.0, "theta_protected_C": 623.9, "verification_status": "CON_PROTECCION_NO_CUMPLE", "is_safe": false}

POST /api/thermal/iso834 → 200 {"time_minutes": 30.0, "gas_temperature_C": 841.8, "steel_temperature_C": 759.6, "yield_reduction_factor_ky": 0.158, "status": "DANGER"}
  (estimador simplificado FireEvaluator: la temperatura del acero NO sale de la ec. 4.25; usa check-profile)

μ = 1,5 → 422 (validación de entrada)
```

</details>

## Verificación

- La temperatura crítica reproduce los cinco casos resueltos a mano de la ficha W01437 (exámenes UPC) y los factores de reducción, los de las fichas W01409 y W01411 (con la errata de k_E documentada).
- El primer paso de la ec. 4.25 está derivado a mano para gas constante (600 °C y 400 °C con k_sh = 0,7), igual que c_a(θ) en sus cuatro tramos y k_sh de la ec. 4.26a.
- El chequeo por perfil tiene tests de defectos corregidos: veredicto por comparación térmica real, requisito ininteligible que aborta, sin sustitución del tipo de protección pedido, recubrimientos reactivos sin cálculo de capa inerte.
- Correcciones de esta revisión (1.2.0): el solver térmico 2D no conducía desde las celdas de borde (media mesh-dependiente y casi doble que la masa concentrada); la rama US de `retention_multi` usaba una cuadrática sin fuente (k_E = 0 a 400 °C) en lugar de la Tabla A-4.2.1 de AISC 360.

## Limitaciones

- `iso834.FireEvaluator` (y el endpoint `/api/thermal/iso834`) es un estimador simplificado de la temperatura del acero, no el método de §4.2.5; se mantiene por compatibilidad. Para veredictos usa `en_steel_temperature` o `/api/fire/check-profile`.
- La temperatura de referencia T_Ed, los fuegos paramétricos del Anexo A de EN 1991-1-2 y los perfiles de temperatura del Anexo A de EN 1992-1-2 no están implementados.
- `protection_catalog` tiene seis productos genéricos sin tablas de ensayo cargadas; los intumescentes solo se verifican tras cargar filas del informe del fabricante.
- `check_fire_resistance_from_profile` usa k_sh = 0,90, A_p/V = Am/V y el espesor medio del rango del producto; afina con `ProtectedSteel` directamente.
- `thermal_fea` usa k = 45 W/mK constante y c_a evaluado a la temperatura media de la sección; la protección se modela como una resistencia térmica en el flujo, no como capa mallada. `fem_thermal_1d` usa h = 25 W/m²K combinado en la cara expuesta y propiedades constantes.
- `concrete_fire` emplea un perfil de temperaturas semiempírico (difusividad dependiente de T y meseta a 100 °C); las tablas 5.2a/5.5/5.8 están resumidas.
- `fire_load_density`: valores característicos y factores δ por defecto; k_c = 0,07 min·m²/MJ es una simplificación de EN 1991-1-2 Anexo F.
- El código AU se enruta a la tabla EN sin los ajustes de AS 4100.

## Normas y referencias

- EN 1993-1-2:2005, Eurocódigo 3, Parte 1-2: Proyecto de estructuras sometidas al fuego. §3.2.1 (Tabla 3.1), §3.4.1.2, §4.2.4 (ec. 4.22), §4.2.5.1 (ec. 4.25, 4.26a), §4.2.5.2 (ec. 4.27).
- EN 1991-1-2:2002, Parte 1-2: Acciones en estructuras expuestas al fuego. §3.1, §3.2 (curvas nominales), Anexo E (carga de fuego), Anexo F (duración equivalente).
- EN 1992-1-2:2004, Eurocódigo 2, Parte 1-2. Tablas 3.1, 3.2a, 5.2a, 5.5, 5.8; Anexo B.1 (isoterma de 500 °C) y B.2 (zonas).
- EN 13501-2 (clasificación R/E/I); EN 13381-8 y UL 263 (ensayos de protección).
- AISC 360-16/22, Appendix 4, Table A-4.2.1.
- ASTM E119 (ajuste de Lie, 1992); Rijkswaterstaat (curva RWS).
- Fichas del máster de Ingeniería Estructural y de la Construcción (UPC) citadas por WorkID en los docstrings de `tests/`.

## Licencia

MIT. Consulta [LICENSE](LICENSE).

---

Parte de **Loadpath**, la colección de librerías estructurales de código abierto de [Jesús Murgas](https://github.com/jmurgass99).
