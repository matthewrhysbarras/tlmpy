import importlib.util
from pathlib import Path

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "boundary_oblique_path.py"
SPEC = importlib.util.spec_from_file_location("boundary_oblique_path", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
boundary_oblique_path = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(boundary_oblique_path)


def test_boundary_oblique_path_benchmark_writes_result(tmp_path):
    output = tmp_path / "boundary_oblique_path.json"

    result = boundary_oblique_path.run_benchmark(output)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "boundary-oblique-path"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (180, 140)
    assert loaded.grid_spacing == (1.0, 1.0)
    assert loaded.dt > 0
    assert loaded.steps == 340

    ratios = [
        loaded.metrics["gamma_0_0_oblique_return_ratio"],
        loaded.metrics["gamma_0_25_oblique_return_ratio"],
        loaded.metrics["gamma_0_5_oblique_return_ratio"],
        loaded.metrics["gamma_0_75_oblique_return_ratio"],
        loaded.metrics["gamma_1_0_oblique_return_ratio"],
    ]
    assert ratios == sorted(ratios)
    assert loaded.metrics["monotonic_oblique_return_ratio"] is True
    assert loaded.metrics["ratio_span"] >= loaded.tolerances["min_ratio_span"]
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)
