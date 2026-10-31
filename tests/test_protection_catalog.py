"""Tests protection catalog."""
from steelfire.protection_catalog import CATALOG, lookup, recommend


def test_catalog_count():
    assert len(CATALOG) >= 6


def test_recommend_R90():
    out = recommend(target_rating_min=90)
    assert all(p.rating_minutes >= 90 for p in out)


def test_recommend_con_budget():
    out = recommend(target_rating_min=60, budget_USD_per_m2=40)
    assert all(p.cost_USD_per_m2 <= 40 for p in out)


def test_lookup():
    p = lookup("Concrete-R180")
    assert p is not None
    assert p.rating_minutes == 180
