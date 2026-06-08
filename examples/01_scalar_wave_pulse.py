"""Free-space Ricker pulse example."""

from pathlib import Path

from tlmpy import Grid2D
from tlmpy.core.probes import PointProbe2D
from tlmpy.core.sources import PointSource2D, RickerPulse
from tlmpy.physics import ScalarWaveTLM2D
from tlmpy.viz import plot_field

out = Path("outputs")
out.mkdir(exist_ok=True)
grid = Grid2D((96, 96), (1e-3, 1e-3))
solver = ScalarWaveTLM2D(grid, wave_speed=1500.0, boundary="matched")
solver.add_source(PointSource2D((48, 48), RickerPulse(frequency=100_000.0)))
solver.add_probe(PointProbe2D("centre", (48, 48)))
result = solver.run(180, store_final_field=True)
result.save_npz(out / "scalar_wave_pulse.npz")
plot_field(result.final_field, "Scalar wave pulse", out / "scalar_wave_pulse.png")

