# steelfire — aço estrutural em situação de incêndio (EN 1993-1-2)

[Español](README.md) · [English](README.en.md) · **Português** · [Italiano](README.it.md)

Temperatura do aço não protegido e protegido sob as curvas nominais de incêndio (EN 1993-1-2 §4.2.5, eq. 4.25 e 4.27), temperatura crítica por grau de utilização (§4.2.4), fatores de redução k_y, k_E e k_p (Tabela 3.1 e AISC 360 Apêndice 4), verificação da classe R exigida com a proteção passiva do catálogo, solvers térmicos 2D e 1D, métodos da isotérmica de 500 °C e das zonas para o betão (EN 1992-1-2 Anexo B) e densidade de carga de incêndio. Depende apenas de `numpy`; as funções estão ancoradas em exercícios de exame resolvidos e na aritmética da norma.

[![CI](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Que problema resolve

Tem um perfil com o seu fator de massividade Am/V, um grau de utilização em situação de incêndio e uma classe exigida (R30, R60, R90) e precisa de saber que temperatura atinge, a que temperatura falha e se a proteção proposta o mantém abaixo dela. O pacote faz essa cadeia completa e recusa dar veredito quando não o pode calcular (tintas intumescentes sem tabela de ensaio). As ações em situação de incêndio e o grau de utilização são seus.

**Use quando**

- precisar da temperatura do aço sob a ISO 834, a curva de hidrocarbonetos ou outra curva para um Am/V dado, com ou sem camada inerte de proteção;
- quiser a temperatura crítica de um elemento e o instante em que a atinge (tempo até ao colapso) para R30/R60/R90;
- dimensionar a espessura de argamassa projetada ou de placa para uma classe, ou quiser os fatores k_y, k_E, k_p para degradar um modelo de barras passo a passo;
- comparar proteções do catálogo por classe e custo e precisar de uma verificação com veredito rastreável;
- fizer uma triagem térmica 2D de uma secção maciça ou de um pilar de betão pela isotérmica de 500 °C ou pelas zonas.

**Não use para**

- obter esforços ou graus de utilização: não há análise estrutural;
- verificar tintas intumescentes sem o relatório de ensaio do fabricante: a verificação responde NO_VERIFICADO, por conceção;
- secções mistas aço-betão (EN 1994-1-2) ou madeira: não estão incluídas;
- servir incêndios paramétricos pela API: a curva do Anexo A da EN 1991-1-2 está em `en_steel_temperature.parametric_fire_gas` (corrigida na 1.2.1, ver Limitações), mas a API anuncia «paramétrica» e serve ISO 834, hidrocarbonetos e exterior;
- AS 4100: o código AU é encaminhado para a tabela da EN 1993-1-2 sem ajustes (um teste documenta-o).

## Instalação

```bash
pip install git+https://github.com/jmurgass99/steelfire.git
pip install "steelfire[analytic,memos,api] @ git+https://github.com/jmurgass99/steelfire.git"   # curvas simbólicas (sympy), memórias (handcalcs), API REST
```

Para desenvolvimento: `git clone`, `pip install -e ".[test,api,analytic,memos]"`, `pytest -q` (23 ficheiros de testes). No Windows, se a consola não for UTF-8, execute os exemplos com `python -X utf8 examples/<nome>.py`.

## Capacidades

| Capacidade | Módulos | Norma ou referência | Casos de uso |
|---|---|---|---|
| Curvas de incêndio e temperatura do aço: ISO 834, hidrocarbonetos, exterior, ASTM E119, RWS, paramétrica do Anexo A da EN 1991-1-2; método incremental não protegido (com k_sh) e protegido; calor específico | `en_steel_temperature`, `fire_curves_sympy` | EN 1991-1-2 §3.2; EN 1993-1-2 §3.4.1.2, §4.2.5.1 (eq. 4.25, 4.26a), §4.2.5.2 (eq. 4.27) | [7 casos](#1-curvas-de-incêndio-e-temperatura-do-aço) |
| Temperatura crítica, fatores de redução por norma, histórico térmico para modelos de barras, memória de cálculo | `en_steel_temperature`, `iso834`, `thermal_iter`, `retention_multi`, `memos` | EN 1993-1-2 §4.2.4 (eq. 4.22), §3.2.1 Tabela 3.1; AISC 360-16/22 Ap. 4 Tabela A-4.2.1 | [5 casos](#2-temperatura-crítica-fatores-de-redução-e-tempo-até-ao-colapso) |
| Verificação por perfil e proteção passiva: classe exigida, catálogo com método de verificação (camada inerte ou ensaio certificado), classificações EN 13501-2 | `en_steel_temperature.check_fire_resistance_from_profile`, `protection_catalog` | EN 1993-1-2 §4.2.5.2; EN 13501-2; UL 263 / EN 13381-8 | [5 casos](#3-verificação-por-perfil-e-proteção-passiva) |
| Análise térmica 2D por diferenças finitas e 1D por elementos finitos, serviço tipado | `thermal_fea`, `fem_thermal_1d`, `services.thermal` | Equação do calor com fluxo convectivo-radiativo (EN 1991-1-2 §3.1) | [5 casos](#4-análise-térmica-2d-e-1d) |
| Betão em incêndio e carga de incêndio: isotérmica de 500 °C, zonas, distância ao eixo por classe, k_c e k_s; q_f,d e duração equivalente | `concrete_fire`, `fire_load_density` | EN 1992-1-2 Anexo B.1/B.2, Tabelas 3.1, 3.2a, 5.2a, 5.5, 5.8; EN 1991-1-2 Anexo E | [5 casos](#5-betão-em-incêndio-e-carga-de-incêndio) |
| API REST | `api` | — | [1 caso](#6-api-rest) |

Os 28 scripts de `examples/` foram executados num ambiente limpo antes de serem publicados; a saída está em `examples/output/` e é a que se reproduz aqui.

## Casos de uso

As saídas reproduzem-se exatamente como os scripts as imprimem, em espanhol.

### 1. Curvas de incêndio e temperatura do aço

#### Perfil não protegido e com vermiculite sob a ISO 834: quando se atinge θ_cr

Am/V = 150 m⁻¹, μ₀ = 0,6. Método incremental do §4.2.5 com Δt = 5 s; a proteção de 20 mm leva o instante crítico de 12 para 90 minutos.

<details><summary>Saída real de <code>python examples/protected_vs_unprotected_steel_iso834_en1993_1_2.py</code></summary>

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

#### As cinco curvas nominais com derivada e integral simbólicas

Tabela de temperaturas dos gases, gradiente térmico da ISO 834 nos primeiros minutos e energia acumulada numa hora (extra `analytic`).

<details><summary>Saída real de <code>python examples/fire_curves_iso834_hydrocarbon_external_astm_rws_comparison.py</code></summary>

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

#### Curva paramétrica do Anexo A da EN 1991-1-2: ventilação face a combustível

<details><summary>Saída real de <code>python examples/parametric_fire_annex_a_ventilation_vs_fuel_controlled_steel_temperature.py</code></summary>

```text
q_t,d = 150 MJ/m², b = 1160, t_lim = 20 min

  t [min]      0     10     20     30     45     60     75     90    120
  O = 0.04     20    700    789    841    900    759    619    478    197
  O = 0.10     20    733    818    525     86     20     20     20     20

A mano:
  O = 0.04: ventilación, Γ = 1.00, t_max = 45 min, Θ_max = 900 °C, t*_max = 0.750; Θ_g(55 min) = 806 °C (paquete 806)
    continuidad en t_max: 899.9 → 899.9 °C
  O = 0.10: combustible, Γ = 6.25, t_max = 20 min, Θ_max = 818 °C, t*_max = 1.875; Θ_g(30 min) = 525 °C (paquete 525)
    continuidad en t_max: 818.2 → 818.0 °C

Perfil sin proteger, Am/V = 200 m⁻¹ (θ_a máxima y cuándo):
  ISO 834:            θ_a(120 min) = 1048 °C
  paramétrica O = 0.04: θ_a,max = 895 °C a los 46 min; a 120 min 263 °C
  paramétrica O = 0.10: θ_a,max = 784 °C a los 21 min; a 120 min 20 °C
```

</details>

#### Varrimento do fator de massividade: de um perfil maciço a uma chapa fina

Temperatura aos 15, 30 e 60 min e tempo até atingir 500 °C para Am/V de 50 a 300 m⁻¹.

<details><summary>Saída real de <code>python examples/unprotected_steel_heating_section_factor_sweep.py</code></summary>

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

#### Efeito de sombra em perfis em I (eq. 4.26a)

k_sh a partir do fator de massividade em caixão e o seu efeito no aquecimento aos 30 min. O módulo implementa apenas a eq. 4.26a; a 4.26b (outras secções) não está incluída.

<details><summary>Saída real de <code>python examples/shadow_factor_i_section_boxed_section_factor.py</code></summary>

```text
perfil     Am/V  [Am/V]_b   k_sh |  θ 30 min k_sh=1  θ 30 min con k_sh
IPE 300     200       140  0.630 |              828                798
IPE 500     150       110  0.660 |              815                766
HEB 300     115        85  0.665 |              787                738

k_sh solo depende del cociente [Am/V]_b/[Am/V]; el chequeo por perfil del paquete usa k_sh = 0,90 por defecto.
```

</details>

#### Espessura de placa para R60 e R90 (eq. 4.27)

Placa de silicato de cálcio numa viga com Am/V = 200 m⁻¹: a primeira linha que cumpre marca a espessura mínima a pedir ao fabricante.

<details><summary>Saída real de <code>python examples/protected_steel_board_thickness_selection_r60_r90.py</code></summary>

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

#### O pico do calor específico a 735 °C e o patamar de aquecimento

c_a(θ) por troços (§3.4.1.2) e velocidade de aquecimento medida por faixas: o perfil abranda ao aproximar-se dos 735 °C.

<details><summary>Saída real de <code>python examples/specific_heat_peak_735c_and_heating_rate.py</code></summary>

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

### 2. Temperatura crítica, fatores de redução e tempo até ao colapso

#### Temperatura crítica em cinco casos de exame do mestrado (ficha W01437)

Cada μ₀ foi resolvido à mão pelo aluno; a eq. 4.22 reprodu-los à décima de grau. Fora do domínio a função lança ValueError.

<details><summary>Saída real de <code>python examples/critical_temperature_exam_cases_w01437.py</code></summary>

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

#### k_y, k_E e k_p da Tabela 3.1 e dois casos do mestrado (fichas W01409 e W01411)

Tabela completa com interpolação e os valores de exame; a ficha W01411 imprime k_E = 0,4004 onde a tabela dá 0,4034 (errata documentada, ancora-se o valor recalculado).

<details><summary>Saída real de <code>python examples/reduction_factors_ky_ke_kp_table_3_1_w01409_w01411.py</code></summary>

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

#### Fatores de retenção por norma: EN 1993-1-2 face à AISC 360 Apêndice 4

A AISC adota os valores do Eurocódigo em nós de °F: k_E e k_y coincidem nos nós, k_p fica até 0,04 abaixo entre 300 e 500 °C. Até esta versão o ramo US usava uma quadrática sem fonte que dava k_E = 0 a 400 °C.

<details><summary>Saída real de <code>python examples/retention_factors_multicode_eu_us_au.py</code></summary>

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

#### Histórico térmico para um modelo de barras: modificadores de E e f_y e tempo até ao colapso

k_E e k_y por passo de tempo a partir da temperatura do aço, prontos a reatribuir como «Property Modifiers», e o instante em que k_y desce abaixo de μ₀.

<details><summary>Saída real de <code>python examples/thermal_history_property_modifiers_and_collapse_time.py</code></summary>

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

#### Memória de temperatura crítica e tempo até ao colapso (extra `memos`)

Viga IPE 300 não protegida (R30) e com placa de 20 mm (R60): θ_cr, t_cr, veredito e a memória em Markdown.

<details><summary>Saída real de <code>python examples/critical_temperature_memo_markdown_collapse_time.py</code></summary>

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

### 3. Verificação por perfil e proteção passiva

#### Verificação da classe exigida por perfil com argamassa, placa e intumescente

Com camada inerte o pacote aplica a espessura média do produto, integra a eq. 4.27 e compara com θ_cr; com tinta intumescente e sem tabela de ensaio não há veredito.

<details><summary>Saída real de <code>python examples/fire_rating_check_by_profile_r30_r60_r90.py</code></summary>

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

#### Pilar HEB 300: R60 e R90 com argamassa ou placa, e espessura mínima que cumpre

Quando a espessura média do catálogo não chega, o estado é CON_PROTECCION_NO_CUMPLE e procura-se a espessura mínima milímetro a milímetro.

<details><summary>Saída real de <code>python examples/spray_mortar_protection_check_heb300_column_r60_r90.py</code></summary>

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

#### Tinta intumescente: sem tabela de ensaio não há veredito; com ela, verificação certificada

Carrega-se uma linha ILUSTRATIVA (não é um dado real) para mostrar o caminho por classificação certificada e que fora do Am/V ensaiado não se extrapola.

<details><summary>Saída real de <code>python examples/intumescent_coating_certified_test_data_required.py</code></summary>

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

#### Catálogo de proteções: recomendar por classe e orçamento

<details><summary>Saída real de <code>python examples/protection_catalog_recommend_by_rating_and_budget.py</code></summary>

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

#### Classificações EN 13501-2: minutos e prestações (R, E, I)

«R120» cobre «R90» embora como texto '1' < '9'; «R120» não cobre «EI90»; uma cadeia ininteligível lança ValueError.

<details><summary>Saída real de <code>python examples/fire_rating_string_parsing_and_coverage_rules.py</code></summary>

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

### 4. Análise térmica 2D e 1D

#### Secção retangular 200×400 por diferenças finitas: quatro faces, três faces e com proteção

<details><summary>Saída real de <code>python examples/thermal_fea_2d_rectangular_section_iso834.py</code></summary>

```text
Sección 200 x 400 mm, curva ISO 834

4 caras expuestas, sin protección          15 min: máx    232 / media    151 °C | 30 min: máx    444 / media    339 °C
3 caras expuestas (cara superior protegida) 15 min: máx    233 / media    131 °C | 30 min: máx    444 / media    295 °C
4 caras, 15 mm de protección (k = 0,12 W/mK) 15 min: máx     77 / media     55 °C | 30 min: máx    146 / media    114 °C
```

</details>

#### Barra maciça: solver 2D face ao modelo de massa concentrada da EN 1993-1-2

Com o mesmo fluxo líquido, a média da secção segue a eq. 4.25 com diferenças de poucos °C. Até esta versão o solver aquecia quase o dobro porque as células de bordo não conduziam para o interior.

<details><summary>Saída real de <code>python examples/thermal_2d_vs_lumped_en1993_1_2_massive_bar.py</code></summary>

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

#### Refinamento da malha e passo de tempo pelo CFL

A média converge com a malha (±2 %); um Δt maior que o limite lança ValueError.

<details><summary>Saída real de <code>python examples/thermal_2d_mesh_refinement_and_cfl_time_step.py</code></summary>

```text
  n  Δx [mm]  Δt_max [s]   pasos  T_max 10 min  T_media
  5       40      29.656      60           148      119
 10       20       7.414     210           162      118
 20       10       1.853     810           169      117

Δt = 5·Δt_max → ValueError: dt=37.0694s viola CFL (dt_max=7.4139s). Reduce dt o aumenta resolución.

Diferencia de la media respecto a la malla de 20: n = 5 → +1.9%, n = 10 → +0.5%. La máxima (celda de esquina) sí depende del tamaño de celda.
```

</details>

#### Serviço tipado: viga sob laje (três faces) face a um pilar (quatro)

<details><summary>Saída real de <code>python examples/thermal_service_typed_api_three_sides_exposed.py</code></summary>

```text
viga 300x500, 3 caras (superior cubierta)    15 min: máx   217 / media    98 °C | 30 min: máx   402 / media   218 °C  (39 instantes guardados)
pilar 300x300, 4 caras                       15 min: máx   217 / media   136 °C | 30 min: máx   411 / media   306 °C  (39 instantes guardados)
pilar 300x300, 4 caras, 20 mm protección     15 min: máx    62 / media    45 °C | 30 min: máx   112 / media    87 °C  (39 instantes guardados)

n_x = 1 → ConfigurationError: n_x y n_y deben ser >= 2
```

</details>

#### Placa de proteção e chapa de aço em 1D (elementos finitos, Crank-Nicolson)

<details><summary>Saída real de <code>python examples/thermal_1d_board_protected_steel_plate_crank_nicolson.py</code></summary>

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

### 5. Betão em incêndio e carga de incêndio

#### Pilar de betão: isotérmica de 500 °C e método das zonas (EN 1992-1-2 Anexo B)

O perfil de temperaturas no betão é um modelo semiempírico do pacote, não os perfis do Anexo A: pré-dimensionamento.

<details><summary>Saída real de <code>python examples/concrete_column_isotherm_500_and_zone_method_en1992_1_2.py</code></summary>

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

#### Distância ao eixo da armadura por classe R (método tabelado)

<details><summary>Saída real de <code>python examples/concrete_cover_axis_distance_for_r_rating_en1992_1_2.py</code></summary>

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

#### k_c do betão e k_s da armadura em função da temperatura

<details><summary>Saída real de <code>python examples/concrete_and_rebar_strength_reduction_tables.py</code></summary>

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

#### Densidade de carga de incêndio por utilização e norma, valor de cálculo e duração equivalente

<details><summary>Saída real de <code>python examples/fire_load_density_by_occupancy_multicode.py</code></summary>

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

#### Do compartimento à viga: duração equivalente e temperatura do aço

<details><summary>Saída real de <code>python examples/compartment_equivalent_fire_duration_vs_steel_heating.py</code></summary>

```text
Viga Am/V = 200 m⁻¹, μ₀ = 0.6 → θ_cr = 554 °C

local                         q_f,d   t_eq | θ sin prot.     θ placa 20    
biblioteca sin rociadores      1440    101 |        1021  NO        737  NO
oficina con rociadores          246     17 |         705  NO        190  OK
vivienda                        624     44 |         892  NO        459  OK
```

</details>

### 6. API REST

#### Curvas, temperatura crítica e verificação de perfil por HTTP, sem servidor

<details><summary>Saída real de <code>python examples/rest_api_fire_curves_critical_temperature_check_profile.py</code></summary>

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

## Verificação

- A temperatura crítica reproduz os cinco casos resolvidos à mão da ficha W01437 (exames da UPC) e os fatores de redução, os das fichas W01409 e W01411 (com a errata de k_E documentada).
- O primeiro passo da eq. 4.25 está derivado à mão para gás a temperatura constante (600 °C e 400 °C com k_sh = 0,7), tal como c_a(θ) nos seus quatro troços e k_sh da eq. 4.26a.
- A verificação por perfil tem testes de defeitos corrigidos: veredito por comparação térmica real, requisito ininteligível que aborta, sem substituição do tipo de proteção pedido, revestimentos reativos sem cálculo de camada inerte.
- Correções desta revisão (1.2.0): o solver térmico 2D não conduzia a partir das células de bordo (média dependente da malha e quase o dobro da massa concentrada); o ramo US de `retention_multi` usava uma quadrática sem fonte (k_E = 0 a 400 °C) em vez da Tabela A-4.2.1 da AISC 360.

## Limitações

- `iso834.FireEvaluator` (e o endpoint `/api/thermal/iso834`) é por defeito um estimador simplificado da temperatura do aço, não o método do §4.2.5; com `use_en1993_exact_c_a=True` integra o §4.2.5, mas o caso protegido usa uma placa fixa (15 mm, λ_p = 0,12, c_p = 1100, ρ_p = 400). Para veredictos use `en_steel_temperature` ou `/api/fire/check-profile`.
- A temperatura de referência T_Ed e os perfis de temperatura do Anexo A da EN 1992-1-2 não estão implementados. A curva paramétrica do Anexo A da EN 1991-1-2 (aa269db) dá Θ_g, mas não pela API; na 1.2.1 corrigiu-se o seu arrefecimento em incêndios controlados pelo combustível (Θ_max com Γ_lim e t*_max da Eq. A.12: antes saltava de 818 para 1052 °C em t_max).
- `protection_catalog` tem seis produtos genéricos sem tabelas de ensaio carregadas; os intumescentes só se verificam depois de carregar linhas do relatório do fabricante.
- `check_fire_resistance_from_profile` usa k_sh = 0,90, A_p/V = Am/V e a espessura média da gama do produto; afine com `ProtectedSteel` diretamente.
- `thermal_fea` usa por defeito k = 45 W/mK constante (com `variable_k=True`, λ_a(θ) do §3.4.1.3 avaliada à temperatura média da secção, não célula a célula) e c_a à temperatura média; a proteção modela-se como uma resistência térmica no fluxo, não como camada malhada. `fem_thermal_1d` usa h = 25 W/m²K na face exposta (mais radiação linearizada com ε = 0,7 se `include_radiation=True`) e propriedades constantes salvo com `variable_steel_properties=True`, que reconhece o aço pelo nome da camada («steel» ou «acero»).
- `concrete_fire` usa um perfil de temperaturas semiempírico (difusividade dependente de T e patamar a 100 °C); as tabelas 5.2a/5.5/5.8 estão resumidas.
- `fire_load_density`: valores característicos e fatores δ por defeito; k_c = 0,07 min·m²/MJ é uma simplificação da EN 1991-1-2 Anexo F.
- O código AU é encaminhado para a tabela EN sem os ajustes da AS 4100.

## Normas e referências

- EN 1993-1-2:2005, Eurocódigo 3, Parte 1-2: Verificação da resistência ao fogo. §3.2.1 (Tabela 3.1), §3.4.1.2, §4.2.4 (eq. 4.22), §4.2.5.1 (eq. 4.25, 4.26a), §4.2.5.2 (eq. 4.27).
- EN 1991-1-2:2002, Parte 1-2: Ações em estruturas expostas ao fogo. §3.1, §3.2 (curvas nominais), Anexo E (carga de incêndio), Anexo F (duração equivalente).
- EN 1992-1-2:2004, Eurocódigo 2, Parte 1-2. Tabelas 3.1, 3.2a, 5.2a, 5.5, 5.8; Anexo B.1 (isotérmica de 500 °C) e B.2 (zonas).
- EN 13501-2 (classificação R/E/I); EN 13381-8 e UL 263 (ensaios de proteção).
- AISC 360-16/22, Appendix 4, Table A-4.2.1.
- ASTM E119 (ajuste de Lie, 1992); Rijkswaterstaat (curva RWS).
- Fichas do Mestrado em Engenharia Estrutural e da Construção (UPC) citadas por WorkID nas docstrings de `tests/`.

## Licença

MIT. Consulte [LICENSE](LICENSE).

---

Parte do **Loadpath**, a coleção de bibliotecas estruturais de código aberto de [Jesús Murgas](https://github.com/jmurgass99).
