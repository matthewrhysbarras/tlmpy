import numpy as np
import pytest

from tlmpy import Grid2D
from tlmpy.physics import Diffusion2D


def test_diffusion_stability_and_smoothing():
    grid = Grid2D((21, 21), (1.0, 1.0))
    solver = Diffusion2D(grid, diffusivity=1.0)
    u = np.zeros(grid.shape)
    u[10, 10] = 1.0
    solver.set_initial_condition(u)
    with pytest.raises(ValueError, match="von Neumann"):
        solver.run(1, solver.stable_dt() * 1.01)
    result = solver.run(5, solver.stable_dt() * 0.5, store_final_field=True)
    assert np.isfinite(result.final_field).all()
    assert result.final_field[10, 10] < 1.0


def test_neumann_mass_conserved():
    grid = Grid2D((18, 19), (1.0, 1.0))
    rng = np.random.default_rng(4)
    solver = Diffusion2D(grid, diffusivity=0.2, boundary="neumann")
    solver.set_initial_condition(rng.random(grid.shape))
    m0 = float(solver.u.sum())
    solver.run(50, solver.stable_dt() * 0.8)
    assert abs(float(solver.u.sum()) - m0) / m0 < 1e-12


def test_dirichlet_runs():
    grid = Grid2D((10, 10), (1.0, 1.0))
    solver = Diffusion2D(grid, diffusivity=1.0, boundary="dirichlet")
    solver.set_initial_condition(np.ones(grid.shape))
    result = solver.run(2, solver.stable_dt() * 0.5, store_final_field=True)
    assert result.final_field[0, 0] == 0.0

