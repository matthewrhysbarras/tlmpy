from math import isclose, sqrt

from tlmpy import Grid2D
from tlmpy.physics import ScalarWaveTLM2D


def test_exact_dt():
    grid = Grid2D((16, 16), (0.01, 0.01))
    solver = ScalarWaveTLM2D(grid, wave_speed=1234.0)
    assert isclose(solver.dt, grid.dx / (solver.wave_speed * sqrt(2)), rel_tol=1e-12)
    assert isclose(grid.dx / (solver.dt * sqrt(2)), solver.wave_speed, rel_tol=1e-12)

