import importlib.util
from pathlib import Path

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "boundary_corner_behaviour.py"
SPEC = importlib.util.spec_from_file_location("boundary_corner_behaviour", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
boundary_corner_behaviour = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(boundary_corner_behaviour)


def test_boundary_corner_behaviour_benchmark_writes_result(tmp_path):
    output = tmp_path / "boundary_corner_behaviour.json"

    result = boundary_corner_behaviour.run_benchmark(output)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "boundary-corner-behaviour"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (180, 140)
    assert loaded.grid_spacing == (1.0, 1.0)
    assert loaded.dt > 0
    assert loaded.steps == 360

    expected_metrics = [
        "reflective_direct_peak",
        "reflective_corner_return_peak",
        "reflective_corner_return_ratio",
        "matched_direct_peak",
        "matched_corner_return_peak",
        "matched_corner_return_ratio",
        "matched_to_reflective_ratio",
        "passed",
    ]
    for key in expected_metrics:
        assert key in loaded.metrics

    assert (
        loaded.metrics["reflective_corner_return_ratio"]
        >= loaded.tolerances["reflective_corner_return_ratio_min"]
    )
    assert (
        loaded.metrics["matched_to_reflective_ratio"]
        <= loaded.tolerances["matched_to_reflective_ratio_max"]
    )
    assert (
        loaded.metrics["matched_corner_return_ratio"]
        < loaded.metrics["reflective_corner_return_ratio"]
    )
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)
