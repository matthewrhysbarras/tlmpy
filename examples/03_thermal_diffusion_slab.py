"""Transient diffusion from a hot square region."""

from pathlib import Path

import numpy as np

from tlmpy import Grid2D
from tlmpy.physics import Diffusion2D
from tlmpy.viz import plot_field

out = Path("outputs")
out.mkdir(exist_ok=True)
grid = Grid2D((100, 100), (1e-3, 1e-3))
u0 = np.zeros(grid.shape)
u0[40:60, 40:60] = 1.0
solver = Diffusion2D(grid, diffusivity=1e-5, boundary="neumann")
solver.set_initial_condition(u0)
result = solver.run(steps=120, dt=0.8 * solver.stable_dt(), store_final_field=True)
plot_field(result.final_field, "Thermal diffusion slab", out / "thermal_diffusion_slab.png")

