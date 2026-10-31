"""Tests for fire_load_density."""
import pytest
from steelfire.fire_load_density import (
    FireLoadInput, fire_load_density, equivalent_fire_duration_min,
)


def test_basic_office_eu():
    r = fire_load_density(FireLoadInput(occupancy="oficina", floor_area_m2=200, code="EU"))
    assert r.qfk_MJ_m2 == pytest.approx(420.0)
    assert r.qfd_MJ_m2 == pytest.approx(420.0 * 0.8 * 1.2 * 1.0 * 1.0)
    assert r.total_energy_GJ > 0


def test_multi_code():
    for code in ("EU", "USA", "AS", "SG", "NSR"):
        r = fire_load_density(FireLoadInput(occupancy="vivienda", code=code))
        assert r.qfk_MJ_m2 > 0
    with pytest.raises(ValueError):
        fire_load_density(FireLoadInput(occupancy="vivienda", code="ZZ"))


def test_unknown_occupancy():
    with pytest.raises(ValueError):
        fire_load_density(FireLoadInput(occupancy="garaje_secreto"))


def test_equivalent_duration():
    t = equivalent_fire_duration_min(qfd_MJ_m2=500.0)
    assert t == pytest.approx(35.0)
    with pytest.raises(ValueError):
        equivalent_fire_duration_min(-1.0)
