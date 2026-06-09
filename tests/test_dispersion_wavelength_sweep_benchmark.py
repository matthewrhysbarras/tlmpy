import importlib.util
from pathlib import Path

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "dispersion_wavelength_sweep.py"
SPEC = importlib.util.spec_from_file_location("dispersion_wavelength_sweep", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
dispersion_wavelength_sweep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dispersion_wavelength_sweep)


def test_dispersion_wavelength_sweep_benchmark_writes_result(tmp_path):
    output = tmp_path / "dispersion_wavelength_sweep.json"

    result = dispersion_wavelength_sweep.run_benchmark(output)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "dispersion-wavelength-sweep"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (180, 180)
    assert loaded.grid_spacing == (1.0, 1.0)
    assert loaded.dt > 0
    assert loaded.steps == 220

    assert loaded.metrics["max_relative_error"] <= loaded.tolerances["max_relative_error"]
    assert loaded.metrics["speed_spread_relative"] <= loaded.tolerances["speed_spread_relative"]
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)

    cases = loaded.parameters["cases"]
    assert len(cases) == 8
    assert {case["direction"] for case in cases} == {"x", "diagonal"}
    assert {case["frequency"] for case in cases} == {0.02, 0.035, 0.06, 0.08}
