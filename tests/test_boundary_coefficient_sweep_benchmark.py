import importlib.util
from pathlib import Path

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "boundary_coefficient_sweep.py"
SPEC = importlib.util.spec_from_file_location("boundary_coefficient_sweep", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
boundary_coefficient_sweep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(boundary_coefficient_sweep)


def test_boundary_coefficient_sweep_benchmark_writes_result(tmp_path):
    output = tmp_path / "boundary_coefficient_sweep.json"

    result = boundary_coefficient_sweep.run_benchmark(output)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "boundary-coefficient-sweep"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (180, 90)
    assert loaded.grid_spacing == (1.0, 1.0)
    assert loaded.dt > 0
    assert loaded.steps == 260

    ratios = [
        loaded.metrics["gamma_0_0_reflection_ratio"],
        loaded.metrics["gamma_0_25_reflection_ratio"],
        loaded.metrics["gamma_0_5_reflection_ratio"],
        loaded.metrics["gamma_0_75_reflection_ratio"],
        loaded.metrics["gamma_1_0_reflection_ratio"],
    ]
    assert ratios == sorted(ratios)
    assert loaded.metrics["monotonic_reflection_ratio"] is True
    assert loaded.metrics["ratio_span"] >= loaded.tolerances["min_ratio_span"]
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)
