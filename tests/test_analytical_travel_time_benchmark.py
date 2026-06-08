import importlib.util
from pathlib import Path

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "analytical_travel_time.py"
SPEC = importlib.util.spec_from_file_location("analytical_travel_time", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
analytical_travel_time = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analytical_travel_time)


def test_analytical_travel_time_benchmark_writes_result(tmp_path):
    output = tmp_path / "analytical_travel_time.json"

    result = analytical_travel_time.run_benchmark(output)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "analytical-travel-time"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (180, 90)
    assert loaded.grid_spacing == (1.0, 1.0)
    assert loaded.dt > 0
    assert loaded.steps == 170

    for key in ["measured_speed", "expected_speed", "relative_error", "passed"]:
        assert key in loaded.metrics

    assert loaded.metrics["relative_error"] < loaded.tolerances["relative_error"]
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)
