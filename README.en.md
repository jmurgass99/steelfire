# steelfire

[Español](README.md) · **English**

Structural steel in fire, following EN 1993-1-2.

[![CI](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml/badge.svg)](https://github.com/jmurgass99/steelfire/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## What it does

- Temperature of unprotected and protected steel under the nominal fire curves (ISO 834, hydrocarbon).
- Critical temperature from the utilization ratio, and the time at which it is reached.
- Reduction factors k_y, k_E and k_p (EN 1993-1-2 Table 3.1 and AISC 360 Appendix 4).
- Check of the required R class with the passive protection in the catalog.
- 2D and 1D thermal screening, and for concrete the 500 °C isotherm and zone methods (EN 1992-1-2 Annex B).

## Install

```bash
pip install git+https://github.com/jmurgass99/steelfire.git
```

Optional extras: `analytic` (sympy), `memos` (handcalcs), `api`. Base dependency: `numpy`.

## Example

Critical temperature of a member with utilization ratio 0.16:

```python
from steelfire.en_steel_temperature import critical_temperature

print(round(critical_temperature(0.16), 1))   # 758.5 °C
```

More cases in [`examples/`](examples).

## What it does not do

- Obtain internal forces or utilization ratios: there is no structural analysis.
- Verify intumescent paints without the manufacturer's test report: it answers `NO_VERIFICADO`, by design.
- Composite steel-concrete sections (EN 1994-1-2) or timber.
- AS 4100: the `AU` code uses the EN 1993-1-2 table without adjustments.

Details are in [docs/LIMITACIONES.md](docs/LIMITACIONES.md) (in Spanish).

## Tests

```bash
pip install -e ".[test,api,analytic,memos]"
pytest -q
```

On Windows, if the console is not UTF-8, use `python -X utf8 examples/<name>.py`.

## License

MIT. See [LICENSE](LICENSE). Author: [Jesús Murgas](https://github.com/jmurgass99).
