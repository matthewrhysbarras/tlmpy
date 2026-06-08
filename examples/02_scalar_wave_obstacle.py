"""Reflective circular obstacle example; geometric reflection, not refractive media."""

from pathlib import Path

from tlmpy import Grid2D
from tlmpy.core.obstacles import ObstacleMask
from tlmpy.core.sources import PointSource2D, RickerPulse
from tlmpy.physics import ScalarWaveTLM2D
from tlmpy.viz import plot_field

out = Path("outputs")
out.mkdir(exist_ok=True)
grid = Grid2D((128, 128), (1e-3, 1e-3))
obstacles = ObstacleMask(grid).add_circle((0.075, 0.064), 0.012)
solver = ScalarWaveTLM2D(grid, wave_speed=1500.0, boundary="matched", obstacles=obstacles)
solver.add_source(PointSource2D((32, 64), RickerPulse(frequency=80_000.0)))
result = solver.run(220, store_final_field=True)
plot_field(result.final_field, "Reflective obstacle", out / "scalar_wave_obstacle.png")

