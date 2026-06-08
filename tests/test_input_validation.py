import pytest

from tlmpy import Grid2D
from tlmpy.core.boundaries import reflection_coefficient
from tlmpy.core.probes import PointProbe2D
from tlmpy.core.sources import PointSource2D, RickerPulse
from tlmpy.physics import ScalarWaveTLM2D


@pytest.mark.parametrize("boundary", [-0.1, 1.1])
def test_boundary_reflection_coefficient_rejects_out_of_range_values(boundary):
    with pytest.raises(ValueError, match=r"reflection coefficient"):
        reflection_coefficient(boundary)


def test_boundary_reflection_coefficient_rejects_unknown_string():
    with pytest.raises(ValueError):
        reflection_coefficient("absorbing")


@pytest.mark.parametrize("location", [(-1, 3), (8, 3), (3, -1), (3, 8)])
def test_wave_solver_rejects_source_locations_outside_grid(location):
    solver = ScalarWaveTLM2D(Grid2D((8, 8), (1.0, 1.0)))

    with pytest.raises(ValueError, match="location must be inside grid"):
        solver.add_source(PointSource2D(location, RickerPulse(frequency=0.05)))


@pytest.mark.parametrize("location", [(-1, 3), (8, 3), (3, -1), (3, 8)])
def test_wave_solver_rejects_probe_locations_outside_grid(location):
    solver = ScalarWaveTLM2D(Grid2D((8, 8), (1.0, 1.0)))

    with pytest.raises(ValueError, match="location must be inside grid"):
        solver.add_probe(PointProbe2D("p", location))
