"""Tests for steelfire.concrete_fire (EN 1992-1-2)."""
import pytest
from steelfire.concrete_fire import (
    concrete_kc_T,
    rebar_ks_T,
    isotherm_method_500,
    zone_method,
    cover_for_R_rating,
)


def test_kc_anchors_table_3_1():
    assert concrete_kc_T(20) == pytest.approx(1.0, abs=1e-6)
    assert concrete_kc_T(500) == pytest.approx(0.60, abs=1e-6)
    assert concrete_kc_T(1100) == pytest.approx(0.01, abs=1e-6)
    assert concrete_kc_T(1200) == 0.0
    assert concrete_kc_T(1500) == 0.0


def test_kc_monotonic_decreasing():
    Ts = [20, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200]
    vals = [concrete_kc_T(T) for T in Ts]
    for a, b in zip(vals[:-1], vals[1:]):
        assert a >= b


def test_ks_hot_rolled_anchors_table_3_2a():
    assert rebar_ks_T(20) == pytest.approx(1.0, abs=1e-6)
    assert rebar_ks_T(500, "hot_rolled") == pytest.approx(0.78, abs=1e-6)
    assert rebar_ks_T(600, "hot_rolled") == pytest.approx(0.47, abs=1e-6)
    assert rebar_ks_T(1200, "hot_rolled") == 0.0


def test_ks_cold_worked_differs():
    assert rebar_ks_T(500, "cold_worked") == pytest.approx(0.67, abs=1e-6)
    # Cold worked degrades faster than hot rolled in 400-700 range
    assert rebar_ks_T(500, "cold_worked") < rebar_ks_T(500, "hot_rolled")


def test_isotherm_500_column_300x300_60min():
    res = isotherm_method_500(300, 300, 60, fire_curve="ISO834")
    # After 60 minutes ISO834 surface T ~ 945 deg C: 500 deg C isotherm
    # should be at some depth < 50 mm; effective core remains substantial.
    assert res["a500_mm"] > 5.0
    assert res["a500_mm"] < 80.0
    assert res["b_fi_mm"] < 300.0
    assert res["h_fi_mm"] < 300.0
    assert res["b_fi_mm"] > 100.0  # Core still exists


def test_isotherm_500_zero_time():
    res = isotherm_method_500(300, 300, 0)
    assert res["a500_mm"] == 0.0
    assert res["b_fi_mm"] == 300.0


def test_zone_method_capacity_reduces():
    fc = 30.0  # MPa
    ambient = zone_method(300, 300, 0, fc=fc, num_zones=10)
    fire = zone_method(300, 300, 90, fc=fc, num_zones=10)
    assert fire["N_fire_kN"] < ambient["N_fire_kN"]
    assert fire["b_fi_mm"] < 300.0
    assert fire["az_mm"] > 0.0


def test_cover_R120_column_axis_distance():
    res = cover_for_R_rating(b=350, R_min=120, member_type="column")
    # Tabla 5.2a R120: a >= 57 mm (column, mu_fi=0.7), b_min = 350 mm
    assert res["axis_distance_a_mm"] >= 56
    assert res["b_min_required_mm"] == 350
    assert res["b_ok"] is True


def test_cover_R_ratings_increase():
    a_prev = 0
    for R in (30, 60, 90, 120, 180, 240):
        res = cover_for_R_rating(b=500, R_min=R, member_type="column")
        assert res["axis_distance_a_mm"] >= a_prev
        a_prev = res["axis_distance_a_mm"]


def test_cover_beam_and_slab_work():
    rb = cover_for_R_rating(b=200, R_min=120, member_type="beam")
    rs = cover_for_R_rating(b=200, R_min=120, member_type="slab")
    assert rb["axis_distance_a_mm"] == 65
    assert rs["axis_distance_a_mm"] == 40
