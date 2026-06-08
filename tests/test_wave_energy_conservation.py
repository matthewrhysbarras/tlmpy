import numpy as np

from tlmpy import Grid2D
from tlmpy.physics import ScalarWaveTLM2D


def energy(s):
    return float(np.sum(s.n**2 + s.s**2 + s.e**2 + s.w**2))


def test_reflective_energy_conservation():
    rng = np.random.default_rng(3)
    solver = ScalarWaveTLM2D(Grid2D((20, 22), (1.0, 1.0)), boundary="reflective")
    solver.n = rng.normal(size=solver.grid.shape)
    solver.s = rng.normal(size=solver.grid.shape)
    solver.e = rng.normal(size=solver.grid.shape)
    solver.w = rng.normal(size=solver.grid.shape)
    e0 = energy(solver)
    for _ in range(50):
        solver.step()
    assert abs(energy(solver) - e0) / e0 < 1e-12

