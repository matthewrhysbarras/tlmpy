import importlib.util

import pytest

cupy_missing = importlib.util.find_spec("cupy") is None


@pytest.mark.skipif(cupy_missing, reason="CuPy not installed")
def test_cupy_matches_numpy():
    from tlmpy import Grid2D
    from tlmpy.core.sources import PointSource2D, RickerPulse
    from tlmpy.physics import ScalarWaveTLM2D
    from tlmpy.validation.metrics import relative_l2_error

    grid = Grid2D((20, 20), (1.0, 1.0))
    results = []
    for backend in ["numpy", "cupy"]:
        solver = ScalarWaveTLM2D(grid, backend=backend)
        solver.add_source(PointSource2D((10, 10), RickerPulse(0.1)))
        results.append(solver.run(10, store_final_field=True).final_field)
    assert relative_l2_error(results[1], results[0]) < 1e-12

