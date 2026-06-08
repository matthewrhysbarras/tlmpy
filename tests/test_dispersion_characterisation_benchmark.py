import importlib.util
from pathlib import Path

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "dispersion_characterisation.py"
SPEC = importlib.util.spec_from_file_location("dispersion_characterisation", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
dispersion_characterisation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dispersion_characterisation)


def test_dispersion_characterisation_benchmark_writes_result(tmp_path):
    output = tmp_path / "dispersion_characterisation.json"

    result = dispersion_characterisation.run_benchmark(output)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "dispersion-characterisation"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (180, 180)
    assert loaded.grid_spacing == (1.0, 1.0)
    assert loaded.dt > 0
    assert loaded.steps == 200

    expected_metrics = [
        "expected_speed",
        "max_relative_error",
        "directional_speed_spread",
        "directional_spread_relative",
        "x_measured_speed",
        "y_measured_speed",
        "diagonal_measured_speed",
        "passed",
    ]
    for key in expected_metrics:
        assert key in loaded.metrics

    assert loaded.metrics["max_relative_error"] <= loaded.tolerances["max_relative_error"]
    assert (
        loaded.metrics["directional_spread_relative"]
        <= loaded.tolerances["directional_spread_relative"]
    )
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)
