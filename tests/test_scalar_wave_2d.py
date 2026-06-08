import numpy as np
import pytest

from tlmpy import Grid2D
from tlmpy.core.obstacles import ObstacleMask
from tlmpy.core.probes import PointProbe2D
from tlmpy.core.sources import PointSource2D, RickerPulse
from tlmpy.physics import ScalarWaveTLM2D


def test_wave_smoke_boundaries():
    for boundary in ["reflective", "matched"]:
        solver = ScalarWaveTLM2D(Grid2D((32, 32), (1e-3, 1e-3)), boundary=boundary)
        solver.add_source(PointSource2D((16, 16), RickerPulse(50_000.0)))
        solver.add_probe(PointProbe2D("p", (16, 16)))
        result = solver.run(8, store_final_field=True)
        assert result.probes["p"].shape == (8,)
        assert np.isfinite(result.final_field).all()


def test_boundary_is_not_periodic():
    grid = Grid2D((24, 24), (1.0, 1.0))
    solver = ScalarWaveTLM2D(grid, boundary="matched")
    solver.e[12, 0] = 1.0
    solver.step()
    assert solver.w[12, -1] == 0.0
    assert solver.e[12, -1] == 0.0


@pytest.mark.parametrize("boundary", ["matched", "reflective"])
def test_source_near_boundary_does_not_wrap_to_opposite_edge(boundary):
    """Regression for accidental periodic connection.

    A torus-like xp.roll connection would let a pulse launched near the left edge
    reach the right-edge probe in the early wraparound window. In the explicit
    slicing implementation, the direct non-periodic path is much longer than this
    window, so the opposite-edge probe should remain effectively silent.
    """

    grid = Grid2D((96, 48), (1.0, 1.0))
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary=boundary)
    solver.add_source(
        PointSource2D(
            (2, 24),
            RickerPulse(frequency=0.05, delay=8 * solver.dt),
        )
    )
    solver.add_probe(PointProbe2D("opposite", (93, 24)))

    result = solver.run(steps=28)

    assert np.max(np.abs(result.probes["opposite"])) < 1e-12


def test_obstacle_circle_mask_creation():
    grid = Grid2D((40, 40), (0.5, 0.5))
    obstacles = ObstacleMask(grid).add_circle(center=(10.0, 10.0), radius=2.0)

    assert obstacles.mask.shape == grid.shape
    assert obstacles.mask.dtype == np.bool_
    assert obstacles.mask.any()
    assert obstacles.mask[20, 20]


def test_obstacle_mask_affects_propagation_without_nans():
    grid = Grid2D((80, 60), (1.0, 1.0))
    source = PointSource2D((18, 30), RickerPulse(frequency=0.06, delay=8.0))

    free = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary="matched")
    free.add_source(source)
    free_field = free.run(steps=85, store_final_field=True).final_field

    obstacles = ObstacleMask(grid).add_circle(center=(42.0, 30.0), radius=7.0)
    blocked = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary="matched", obstacles=obstacles)
    blocked.add_source(source)
    blocked_field = blocked.run(steps=85, store_final_field=True).final_field

    assert np.isfinite(blocked_field).all()
    assert np.linalg.norm(blocked_field - free_field) > 1e-6


def test_obstacle_reflective_geometry_preserves_port_energy_without_sources():
    """Obstacle masks are approximate reflective geometry, not material interfaces."""

    rng = np.random.default_rng(13)
    grid = Grid2D((32, 30), (1.0, 1.0))
    obstacles = ObstacleMask(grid).add_circle(center=(16.0, 15.0), radius=5.0)
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary="reflective", obstacles=obstacles)
    solver.n = rng.normal(size=grid.shape)
    solver.s = rng.normal(size=grid.shape)
    solver.e = rng.normal(size=grid.shape)
    solver.w = rng.normal(size=grid.shape)

    def port_energy():
        return float(np.sum(solver.n**2 + solver.s**2 + solver.e**2 + solver.w**2))

    initial = port_energy()
    for _ in range(40):
        solver.step()

    assert abs(port_energy() - initial) / initial < 1e-12
