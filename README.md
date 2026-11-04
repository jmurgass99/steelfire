# steelfire

**Español** · [English](README.en.md)

Acero estructural en situación de incendio según EN 1993-1-2.

[![CI](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-green)](LICENSE)

## Qué hace

- Temperatura del acero sin proteger y protegido bajo las curvas nominales de fuego (ISO 834, hidrocarburos).
- Temperatura crítica según el grado de utilización y tiempo en que se alcanza.
- Factores de reducción k_y, k_E y k_p (EN 1993-1-2 Tabla 3.1 y AISC 360 Apéndice 4).
- Comprobación de la clase R exigida con la protección pasiva del catálogo.
- Cribado térmico 2D y 1D, y para hormigón los métodos de la isoterma de 500 °C y de las zonas (EN 1992-1-2 Anexo B).

## Instalación

```bash
pip install git+https://github.com/jmurgass99/steelfire.git
```

Extras opcionales: `analytic` (sympy), `memos` (handcalcs), `api`. Dependencia base: `numpy`.

## Ejemplo

Temperatura crítica de un elemento con grado de utilización 0,16:

```python
from steelfire.en_steel_temperature import critical_temperature

print(round(critical_temperature(0.16), 1))   # 758.5 °C
```

Más casos en [`examples/`](examples).

## Qué no hace

- Obtener solicitaciones ni grados de utilización: no hay análisis estructural.
- Verificar pinturas intumescentes sin el informe de ensayo del fabricante: responde `NO_VERIFICADO`, por diseño.
- Secciones compuestas acero-hormigón (EN 1994-1-2) ni madera.
- AS 4100: el código `AU` usa la tabla de EN 1993-1-2 sin ajustes.

El detalle está en [docs/LIMITACIONES.md](docs/LIMITACIONES.md).

## Pruebas

```bash
pip install -e ".[test,api,analytic,memos]"
pytest -q
```

En Windows, si la consola no es UTF-8, usa `python -X utf8 examples/<nombre>.py`.

## Licencia

MIT. Ver [LICENSE](LICENSE). Autor: [Jesús Murgas](https://github.com/jmurgass99).
