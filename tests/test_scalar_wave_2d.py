import numpy as np

from tlmpy import Grid2D
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
