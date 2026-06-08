import importlib.util
from pathlib import Path

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "boundary_reflection.py"
SPEC = importlib.util.spec_from_file_location("boundary_reflection", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
boundary_reflection = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(boundary_reflection)


def test_boundary_reflection_benchmark_writes_result(tmp_path):
    output = tmp_path / "boundary_reflection.json"

    result = boundary_reflection.run_benchmark(output)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "boundary-reflection"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (36, 34)
    assert loaded.grid_spacing == (1.0, 1.0)
    assert loaded.dt > 0
    assert loaded.steps == 60

    expected_metrics = [
        "initial_energy",
        "reflective_final_energy",
        "reflective_relative_energy_change",
        "reflective_passed",
        "matched_final_energy",
        "matched_energy_ratio",
        "matched_passed",
        "passed",
    ]
    for key in expected_metrics:
        assert key in loaded.metrics

    assert (
        loaded.metrics["reflective_relative_energy_change"]
        <= loaded.tolerances["reflective_relative_energy_change"]
    )
    assert loaded.metrics["matched_energy_ratio"] <= loaded.tolerances["matched_energy_ratio"]
    assert loaded.metrics["reflective_passed"] is True
    assert loaded.metrics["matched_passed"] is True
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)
