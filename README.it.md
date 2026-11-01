# steelfire — acciaio strutturale in caso di incendio (EN 1993-1-2)

[Español](README.md) · [English](README.en.md) · [Português](README.pt.md) · **Italiano**

Temperatura dell'acciaio non protetto e protetto sotto le curve nominali di incendio (EN 1993-1-2 §4.2.5, eq. 4.25 e 4.27), temperatura critica in funzione del grado di utilizzo (§4.2.4), fattori di riduzione k_y, k_E e k_p (Tabella 3.1 e AISC 360 Appendice 4), verifica della classe R richiesta con la protezione passiva del catalogo, solutori termici 2D e 1D, metodi dell'isoterma a 500 °C e delle zone per il calcestruzzo (EN 1992-1-2 Allegato B) e densità di carico di incendio. Dipende solo da `numpy`; le funzioni sono ancorate a esercizi d'esame risolti e all'aritmetica della norma.

[![CI](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Quale problema risolve

Hai un profilo con il suo fattore di sezione Am/V, un grado di utilizzo nella situazione di incendio e una classe richiesta (R30, R60, R90) e devi sapere quale temperatura raggiunge, a quale cede e se la protezione proposta lo mantiene al di sotto. Il pacchetto esegue tutta la catena e si rifiuta di dare un giudizio quando non può calcolarlo (vernici intumescenti senza tabella di prova). Le azioni nella situazione di incendio e il grado di utilizzo li porti tu.

**Usalo quando**

- ti serve la temperatura dell'acciaio sotto ISO 834, curva degli idrocarburi o un'altra curva per un Am/V dato, con o senza strato protettivo inerte;
- vuoi la temperatura critica di un elemento e l'istante in cui la raggiunge (tempo al collasso) per R30/R60/R90;
- dimensioni lo spessore di intonaco o di lastra per una classe, o vuoi i fattori k_y, k_E, k_p per degradare passo dopo passo un modello ad aste;
- confronti le protezioni del catalogo per classe e costo e ti serve una verifica con giudizio tracciabile;
- fai uno screening termico 2D di una sezione piena o di un pilastro in calcestruzzo con l'isoterma a 500 °C o con le zone.

**Non usarlo per**

- ottenere sollecitazioni o gradi di utilizzo: non c'è analisi strutturale;
- verificare vernici intumescenti senza il rapporto di prova del produttore: la verifica risponde NO_VERIFICADO, per scelta progettuale;
- sezioni composte acciaio-calcestruzzo (EN 1994-1-2) o legno: non sono incluse;
- incendi parametrici della EN 1991-1-2 Allegato A: solo le curve nominali (l'API annuncia «parametrica» ma serve ISO 834, idrocarburi ed esterna);
- AS 4100: il codice AU viene instradato sulla tabella della EN 1993-1-2 senza adattamenti (un test lo documenta).

## Installazione

```bash
pip install git+https://github.com/jmurgass99/steelfire.git
pip install "steelfire[analytic,memos,api] @ git+https://github.com/jmurgass99/steelfire.git"   # curve simboliche (sympy), relazioni (handcalcs), API REST
```

Per lo sviluppo: `git clone`, `pip install -e ".[test,api,analytic,memos]"`, `pytest -q` (20 file di test). Su Windows, se la console non è UTF-8, esegui gli esempi con `python -X utf8 examples/<nome>.py`.

## Funzionalità

| Funzionalità | Moduli | Norma o riferimento | Casi d'uso |
|---|---|---|---|
| Curve di incendio e temperatura dell'acciaio: ISO 834, idrocarburi, esterna, ASTM E119, RWS; metodo incrementale non protetto (con k_sh) e protetto; calore specifico | `en_steel_temperature`, `fire_curves_sympy` | EN 1991-1-2 §3.2; EN 1993-1-2 §3.4.1.2, §4.2.5.1 (eq. 4.25, 4.26a), §4.2.5.2 (eq. 4.27) | [6 casi](#1-curve-di-incendio-e-temperatura-dellacciaio) |
| Temperatura critica, fattori di riduzione per norma, storia termica per modelli ad aste, relazione di calcolo | `en_steel_temperature`, `iso834`, `thermal_iter`, `retention_multi`, `memos` | EN 1993-1-2 §4.2.4 (eq. 4.22), §3.2.1 Tabella 3.1; AISC 360-16/22 App. 4 Tabella A-4.2.1 | [5 casi](#2-temperatura-critica-fattori-di-riduzione-e-tempo-al-collasso) |
| Verifica per profilo e protezione passiva: classe richiesta, catalogo con metodo di verifica (strato inerte o prova certificata), classificazioni EN 13501-2 | `en_steel_temperature.check_fire_resistance_from_profile`, `protection_catalog` | EN 1993-1-2 §4.2.5.2; EN 13501-2; UL 263 / EN 13381-8 | [5 casi](#3-verifica-per-profilo-e-protezione-passiva) |
| Analisi termica 2D alle differenze finite e 1D agli elementi finiti, servizio tipizzato | `thermal_fea`, `fem_thermal_1d`, `services.thermal` | Equazione del calore con flusso convettivo-radiativo (EN 1991-1-2 §3.1) | [5 casi](#4-analisi-termica-2d-e-1d) |
| Calcestruzzo in caso di incendio e carico di incendio: isoterma a 500 °C, zone, distanza dall'asse per classe, k_c e k_s; q_f,d e durata equivalente | `concrete_fire`, `fire_load_density` | EN 1992-1-2 Allegato B.1/B.2, Tabelle 3.1, 3.2a, 5.2a, 5.5, 5.8; EN 1991-1-2 Allegato E | [5 casi](#5-calcestruzzo-in-caso-di-incendio-e-carico-di-incendio) |
| API REST | `api` | — | [1 caso](#6-api-rest) |

I 27 script di `examples/` sono stati eseguiti in un ambiente pulito prima della pubblicazione; il loro output è in `examples/output/` ed è quello riprodotto qui.

## Casi d'uso

Gli output sono riportati esattamente come li stampano gli script, in spagnolo.

### 1. Curve di incendio e temperatura dell'acciaio

#### Profilo non protetto e con vermiculite sotto ISO 834: quando si raggiunge θ_cr

Am/V = 150 m⁻¹, μ₀ = 0,6. Metodo incrementale del §4.2.5 con Δt = 5 s; la protezione da 20 mm porta l'istante critico da 12 a 90 minuti.

<details><summary>Output reale di <code>python examples/protected_vs_unprotected_steel_iso834_en1993_1_2.py</code></summary>

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

#### Le cinque curve nominali con derivata e integrale simbolici

Tabella delle temperature dei gas, gradiente termico della ISO 834 nei primi minuti ed energia accumulata in un'ora (extra `analytic`).

<details><summary>Output reale di <code>python examples/fire_curves_iso834_hydrocarbon_external_astm_rws_comparison.py</code></summary>

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

#### Scansione del fattore di sezione: da un profilo tozzo a una lamiera sottile

Temperatura a 15, 30 e 60 min e tempo per raggiungere 500 °C per Am/V da 50 a 300 m⁻¹.

<details><summary>Output reale di <code>python examples/unprotected_steel_heating_section_factor_sweep.py</code></summary>

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

#### Effetto ombra nei profili a I (eq. 4.26a)

k_sh dal fattore di sezione scatolare e il suo effetto sul riscaldamento a 30 min. Il modulo implementa solo l'eq. 4.26a; la 4.26b (altre sezioni) non è inclusa.

<details><summary>Output reale di <code>python examples/shadow_factor_i_section_boxed_section_factor.py</code></summary>

```text
perfil     Am/V  [Am/V]_b   k_sh |  θ 30 min k_sh=1  θ 30 min con k_sh
IPE 300     200       140  0.630 |              828                798
IPE 500     150       110  0.660 |              815                766
HEB 300     115        85  0.665 |              787                738

k_sh solo depende del cociente [Am/V]_b/[Am/V]; el chequeo por perfil del paquete usa k_sh = 0,90 por defecto.
```

</details>

#### Spessore della lastra per R60 e R90 (eq. 4.27)

Lastra di silicato di calcio su una trave con Am/V = 200 m⁻¹: la prima riga verificata indica lo spessore minimo da chiedere al produttore.

<details><summary>Output reale di <code>python examples/protected_steel_board_thickness_selection_r60_r90.py</code></summary>

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

#### Il picco del calore specifico a 735 °C e il plateau di riscaldamento

c_a(θ) a tratti (§3.4.1.2) e velocità di riscaldamento misurata per fasce: il profilo rallenta avvicinandosi a 735 °C.

<details><summary>Output reale di <code>python examples/specific_heat_peak_735c_and_heating_rate.py</code></summary>

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

### 2. Temperatura critica, fattori di riduzione e tempo al collasso

#### Temperatura critica in cinque casi d'esame del master (scheda W01437)

Ogni μ₀ è stato risolto a mano dallo studente; l'eq. 4.22 li riproduce al decimo di grado. Fuori dominio la funzione solleva ValueError.

<details><summary>Output reale di <code>python examples/critical_temperature_exam_cases_w01437.py</code></summary>

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

#### k_y, k_E e k_p della Tabella 3.1 e due casi del master (schede W01409 e W01411)

Tabella completa con interpolazione e i valori d'esame; la scheda W01411 stampa k_E = 0,4004 dove la tabella dà 0,4034 (errata documentato, si ancora il valore ricalcolato).

<details><summary>Output reale di <code>python examples/reduction_factors_ky_ke_kp_table_3_1_w01409_w01411.py</code></summary>

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

#### Fattori di ritenzione per norma: EN 1993-1-2 contro AISC 360 Appendice 4

AISC adotta i valori dell'Eurocodice nei nodi in °F: k_E e k_y coincidono nei nodi, k_p resta fino a 0,04 più basso tra 300 e 500 °C. Fino a questa versione il ramo US usava una quadratica senza fonte che dava k_E = 0 a 400 °C.

<details><summary>Output reale di <code>python examples/retention_factors_multicode_eu_us_au.py</code></summary>

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

#### Storia termica per un modello ad aste: modificatori di E e f_y e tempo al collasso

k_E e k_y per passo temporale a partire dalla temperatura dell'acciaio, pronti da riassegnare come «Property Modifiers», e l'istante in cui k_y scende sotto μ₀.

<details><summary>Output reale di <code>python examples/thermal_history_property_modifiers_and_collapse_time.py</code></summary>

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

#### Relazione su temperatura critica e tempo al collasso (extra `memos`)

Trave IPE 300 non protetta (R30) e con lastra da 20 mm (R60): θ_cr, t_cr, giudizio e la relazione in Markdown.

<details><summary>Output reale di <code>python examples/critical_temperature_memo_markdown_collapse_time.py</code></summary>

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

### 3. Verifica per profilo e protezione passiva

#### Verifica della classe richiesta per profilo con intonaco, lastra e intumescente

Con uno strato inerte il pacchetto applica lo spessore medio del prodotto, integra l'eq. 4.27 e confronta con θ_cr; con vernice intumescente e senza tabella di prova non c'è giudizio.

<details><summary>Output reale di <code>python examples/fire_rating_check_by_profile_r30_r60_r90.py</code></summary>

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

#### Pilastro HEB 300: R60 e R90 con intonaco o lastra, e spessore minimo che verifica

Quando lo spessore medio del catalogo non basta, lo stato è CON_PROTECCION_NO_CUMPLE e si cerca lo spessore minimo millimetro per millimetro.

<details><summary>Output reale di <code>python examples/spray_mortar_protection_check_heb300_column_r60_r90.py</code></summary>

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

#### Vernice intumescente: senza tabella di prova nessun giudizio; con essa, verifica certificata

Si carica una riga ILLUSTRATIVA (non è un dato reale) per mostrare il percorso per classificazione certificata e che fuori dall'Am/V provato non si estrapola.

<details><summary>Output reale di <code>python examples/intumescent_coating_certified_test_data_required.py</code></summary>

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

#### Catalogo delle protezioni: raccomandare per classe e budget

<details><summary>Output reale di <code>python examples/protection_catalog_recommend_by_rating_and_budget.py</code></summary>

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

#### Classificazioni EN 13501-2: minuti e prestazioni (R, E, I)

«R120» copre «R90» anche se come testo '1' < '9'; «R120» non copre «EI90»; una stringa incomprensibile solleva ValueError.

<details><summary>Output reale di <code>python examples/fire_rating_string_parsing_and_coverage_rules.py</code></summary>

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

### 4. Analisi termica 2D e 1D

#### Sezione rettangolare 200×400 alle differenze finite: quattro facce, tre facce e con protezione

<details><summary>Output reale di <code>python examples/thermal_fea_2d_rectangular_section_iso834.py</code></summary>

```text
Sección 200 x 400 mm, curva ISO 834

4 caras expuestas, sin protección          15 min: máx    232 / media    151 °C | 30 min: máx    444 / media    339 °C
3 caras expuestas (cara superior protegida) 15 min: máx    233 / media    131 °C | 30 min: máx    444 / media    295 °C
4 caras, 15 mm de protección (k = 0,12 W/mK) 15 min: máx     77 / media     55 °C | 30 min: máx    146 / media    114 °C
```

</details>

#### Barra piena: solutore 2D contro il modello a massa concentrata della EN 1993-1-2

A parità di flusso netto, la media della sezione segue l'eq. 4.25 con differenze di pochi °C. Fino a questa versione il solutore riscaldava quasi il doppio perché le celle di bordo non conducevano verso l'interno.

<details><summary>Output reale di <code>python examples/thermal_2d_vs_lumped_en1993_1_2_massive_bar.py</code></summary>

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

#### Raffinamento della mesh e passo temporale per la CFL

La media converge con la mesh (±2 %); un Δt superiore al limite solleva ValueError.

<details><summary>Output reale di <code>python examples/thermal_2d_mesh_refinement_and_cfl_time_step.py</code></summary>

```text
  n  Δx [mm]  Δt_max [s]   pasos  T_max 10 min  T_media
  5       40      29.656      60           148      119
 10       20       7.414     210           162      118
 20       10       1.853     810           169      117

Δt = 5·Δt_max → ValueError: dt=37.0694s viola CFL (dt_max=7.4139s). Reduce dt o aumenta resolución.

Diferencia de la media respecto a la malla de 20: n = 5 → +1.9%, n = 10 → +0.5%. La máxima (celda de esquina) sí depende del tamaño de celda.
```

</details>

#### Servizio tipizzato: trave sotto solaio (tre facce) contro pilastro (quattro)

<details><summary>Output reale di <code>python examples/thermal_service_typed_api_three_sides_exposed.py</code></summary>

```text
viga 300x500, 3 caras (superior cubierta)    15 min: máx   217 / media    98 °C | 30 min: máx   402 / media   218 °C  (39 instantes guardados)
pilar 300x300, 4 caras                       15 min: máx   217 / media   136 °C | 30 min: máx   411 / media   306 °C  (39 instantes guardados)
pilar 300x300, 4 caras, 20 mm protección     15 min: máx    62 / media    45 °C | 30 min: máx   112 / media    87 °C  (39 instantes guardados)

n_x = 1 → ConfigurationError: n_x y n_y deben ser >= 2
```

</details>

#### Lastra protettiva e lamiera d'acciaio in 1D (elementi finiti, Crank-Nicolson)

<details><summary>Output reale di <code>python examples/thermal_1d_board_protected_steel_plate_crank_nicolson.py</code></summary>

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

### 5. Calcestruzzo in caso di incendio e carico di incendio

#### Pilastro in calcestruzzo: isoterma a 500 °C e metodo delle zone (EN 1992-1-2 Allegato B)

Il profilo di temperatura nel calcestruzzo è un modello semiempirico del pacchetto, non i profili dell'Allegato A: predimensionamento.

<details><summary>Output reale di <code>python examples/concrete_column_isotherm_500_and_zone_method_en1992_1_2.py</code></summary>

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

#### Distanza dall'asse dell'armatura per classe R (metodo tabellare)

<details><summary>Output reale di <code>python examples/concrete_cover_axis_distance_for_r_rating_en1992_1_2.py</code></summary>

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

#### k_c del calcestruzzo e k_s dell'armatura in funzione della temperatura

<details><summary>Output reale di <code>python examples/concrete_and_rebar_strength_reduction_tables.py</code></summary>

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

#### Densità di carico di incendio per destinazione d'uso e norma, valore di progetto e durata equivalente

<details><summary>Output reale di <code>python examples/fire_load_density_by_occupancy_multicode.py</code></summary>

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

#### Dal compartimento alla trave: durata equivalente e temperatura dell'acciaio

<details><summary>Output reale di <code>python examples/compartment_equivalent_fire_duration_vs_steel_heating.py</code></summary>

```text
Viga Am/V = 200 m⁻¹, μ₀ = 0.6 → θ_cr = 554 °C

local                         q_f,d   t_eq | θ sin prot.     θ placa 20    
biblioteca sin rociadores      1440    101 |        1021  NO        737  NO
oficina con rociadores          246     17 |         705  NO        190  OK
vivienda                        624     44 |         892  NO        459  OK
```

</details>

### 6. API REST

#### Curve, temperatura critica e verifica del profilo via HTTP, senza server

<details><summary>Output reale di <code>python examples/rest_api_fire_curves_critical_temperature_check_profile.py</code></summary>

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

## Verifica

- La temperatura critica riproduce i cinque casi risolti a mano della scheda W01437 (esami UPC) e i fattori di riduzione quelli delle schede W01409 e W01411 (con l'errata di k_E documentato).
- Il primo passo dell'eq. 4.25 è ricavato a mano per gas a temperatura costante (600 °C e 400 °C con k_sh = 0,7), così come c_a(θ) nei suoi quattro tratti e k_sh dell'eq. 4.26a.
- La verifica per profilo ha test sui difetti corretti: giudizio per confronto termico reale, requisito incomprensibile che interrompe, nessuna sostituzione del tipo di protezione richiesto, rivestimenti reattivi senza calcolo a strato inerte.
- Correzioni di questa revisione (1.2.0): il solutore termico 2D non conduceva dalle celle di bordo (media dipendente dalla mesh e quasi doppia rispetto alla massa concentrata); il ramo US di `retention_multi` usava una quadratica senza fonte (k_E = 0 a 400 °C) invece della Tabella A-4.2.1 della AISC 360.

## Limitazioni

- `iso834.FireEvaluator` (e l'endpoint `/api/thermal/iso834`) è uno stimatore semplificato della temperatura dell'acciaio, non il metodo del §4.2.5; si mantiene per compatibilità. Per i giudizi usa `en_steel_temperature` o `/api/fire/check-profile`.
- La temperatura di riferimento T_Ed, gli incendi parametrici dell'Allegato A della EN 1991-1-2 e i profili di temperatura dell'Allegato A della EN 1992-1-2 non sono implementati.
- `protection_catalog` contiene sei prodotti generici senza tabelle di prova caricate; gli intumescenti si verificano solo dopo aver caricato righe del rapporto del produttore.
- `check_fire_resistance_from_profile` usa k_sh = 0,90, A_p/V = Am/V e lo spessore medio della gamma del prodotto; affina con `ProtectedSteel` direttamente.
- `thermal_fea` usa k = 45 W/mK costante e c_a valutato alla temperatura media della sezione; la protezione è modellata come una resistenza termica nel flusso, non come uno strato meshato. `fem_thermal_1d` usa h = 25 W/m²K combinato sulla faccia esposta e proprietà costanti.
- `concrete_fire` usa un profilo di temperatura semiempirico (diffusività dipendente da T e plateau a 100 °C); le tabelle 5.2a/5.5/5.8 sono riassunte.
- `fire_load_density`: valori caratteristici e fattori δ predefiniti; k_c = 0,07 min·m²/MJ è una semplificazione della EN 1991-1-2 Allegato F.
- Il codice AU viene instradato sulla tabella EN senza gli adattamenti della AS 4100.

## Norme e riferimenti

- EN 1993-1-2:2005, Eurocodice 3, Parte 1-2: Progettazione strutturale contro l'incendio. §3.2.1 (Tabella 3.1), §3.4.1.2, §4.2.4 (eq. 4.22), §4.2.5.1 (eq. 4.25, 4.26a), §4.2.5.2 (eq. 4.27).
- EN 1991-1-2:2002, Parte 1-2: Azioni sulle strutture esposte al fuoco. §3.1, §3.2 (curve nominali), Allegato E (carico di incendio), Allegato F (durata equivalente).
- EN 1992-1-2:2004, Eurocodice 2, Parte 1-2. Tabelle 3.1, 3.2a, 5.2a, 5.5, 5.8; Allegato B.1 (isoterma a 500 °C) e B.2 (zone).
- EN 13501-2 (classificazione R/E/I); EN 13381-8 e UL 263 (prove sulle protezioni).
- AISC 360-16/22, Appendix 4, Table A-4.2.1.
- ASTM E119 (adattamento di Lie, 1992); Rijkswaterstaat (curva RWS).
- Schede del Master in Ingegneria Strutturale e delle Costruzioni (UPC) citate per WorkID nelle docstring di `tests/`.

## Licenza

MIT. Vedi [LICENSE](LICENSE).

---

Parte di **Loadpath**, la raccolta di librerie strutturali open source di [Jesús Murgas](https://github.com/jmurgass99).
