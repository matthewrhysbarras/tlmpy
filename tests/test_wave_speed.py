from math import isclose, sqrt

from tlmpy import Grid2D
from tlmpy.core.probes import PointProbe2D
from tlmpy.core.sources import PointSource2D, RickerPulse
from tlmpy.physics import ScalarWaveTLM2D
from tlmpy.validation.analytical import estimate_wave_speed_from_probes


def test_exact_dt():
    grid = Grid2D((16, 16), (0.01, 0.01))
    solver = ScalarWaveTLM2D(grid, wave_speed=1234.0)
    assert isclose(solver.dt, grid.dx / (solver.wave_speed * sqrt(2)), rel_tol=1e-12)
    assert isclose(grid.dx / (solver.dt * sqrt(2)), solver.wave_speed, rel_tol=1e-12)


def test_propagation_based_wave_speed_regression():
    """Two-probe time-of-flight check.

    The tolerance is intentionally looser than the exact dt formula test because
    the v0.1 scalar TLM demonstrator has numerical dispersion and the finite-band
    Ricker pulse has a broad arrival rather than a single sharp front.
    """

    grid = Grid2D((180, 90), (1.0, 1.0))
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary="matched")
    source = (45, 45)
    p1 = (75, 45)
    p2 = (115, 45)
    solver.add_source(
        PointSource2D(
            source,
            RickerPulse(frequency=0.035, delay=16 * solver.dt),
        )
    )
    solver.add_probe(PointProbe2D("p1", p1))
    solver.add_probe(PointProbe2D("p2", p2))

    result = solver.run(steps=170)

    measured = estimate_wave_speed_from_probes(
        result.probes["p1"],
        result.probes["p2"],
        distance=(p2[0] - p1[0]) * grid.dx,
        dt=result.dt,
    )
    expected = grid.dx / (result.dt * sqrt(2))

    assert abs(measured - expected) / expected < 0.10
