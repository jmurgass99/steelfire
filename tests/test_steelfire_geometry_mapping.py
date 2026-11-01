from __future__ import annotations

from steelfire.geometry_mapping import build_isection_thermal_mesh


def test_build_isection_thermal_mesh_geometry_mapping():
    m = build_isection_thermal_mesh(divisions_per_region=6)
    assert len(m.cells) == 18
    assert len(m.region_to_cells["bottom_flange"]) == 6
    assert len(m.region_to_cells["web"]) == 6
    assert len(m.region_to_cells["top_flange"]) == 6
    # Web is thinner than flange -> higher section factor Am/V
    web_cell = m.cells[m.region_to_cells["web"][0]]
    flange_cell = m.cells[m.region_to_cells["bottom_flange"][0]]
    assert web_cell[4] > flange_cell[4]
