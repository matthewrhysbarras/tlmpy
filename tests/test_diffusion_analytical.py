"""Infinite-domain Gaussian reference approximated on a large, centered finite grid."""

from tlmpy import Grid2D
from tlmpy.physics import Diffusion2D
from tlmpy.validation.analytical import gaussian_diffusion_2d
from tlmpy.validation.metrics import relative_l2_error


def test_gaussian_diffusion_reference():
    grid = Grid2D((101, 101), (0.01, 0.01))
    alpha = 1e-4
    sigma0 = 0.05
    dt = 0.2
    steps = 10
    u0 = gaussian_diffusion_2d(grid, alpha, sigma0, 0.0)
    solver = Diffusion2D(grid, alpha, boundary="neumann")
    solver.set_initial_condition(u0)
    result = solver.run(steps, dt, store_final_field=True)
    expected = gaussian_diffusion_2d(grid, alpha, sigma0, steps * dt)
    assert relative_l2_error(result.final_field, expected) < 0.03

