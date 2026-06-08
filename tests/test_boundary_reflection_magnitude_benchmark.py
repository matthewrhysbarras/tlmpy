import importlib.util
from pathlib import Path

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "benchmarks" / "boundary_reflection_magnitude.py"
)
SPEC = importlib.util.spec_from_file_location("boundary_reflection_magnitude", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
boundary_reflection_magnitude = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(boundary_reflection_magnitude)


def test_boundary_reflection_magnitude_benchmark_writes_result(tmp_path):
    output = tmp_path / "boundary_reflection_magnitude.json"

    result = boundary_reflection_magnitude.run_benchmark(output)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "boundary-reflection-magnitude"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (180, 90)
    assert loaded.grid_spacing == (1.0, 1.0)
    assert loaded.dt > 0
    assert loaded.steps == 260

    expected_metrics = [
        "reflective_incident_peak",
        "reflective_reflected_peak",
        "reflective_reflection_ratio",
        "matched_incident_peak",
        "matched_reflected_peak",
        "matched_reflection_ratio",
        "matched_to_reflective_ratio",
        "passed",
    ]
    for key in expected_metrics:
        assert key in loaded.metrics

    assert (
        loaded.metrics["reflective_reflection_ratio"]
        >= loaded.tolerances["reflective_reflection_ratio_min"]
    )
    assert (
        loaded.metrics["matched_to_reflective_ratio"]
        <= loaded.tolerances["matched_to_reflective_ratio_max"]
    )
    assert loaded.metrics["matched_reflection_ratio"] < loaded.metrics["reflective_reflection_ratio"]
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)
