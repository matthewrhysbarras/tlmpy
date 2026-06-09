import importlib.util
from pathlib import Path

import pytest

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "benchmarks" / "koay2008_gaussian_tlm_diffusion.py"
)
SPEC = importlib.util.spec_from_file_location("koay2008_gaussian_tlm_diffusion", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
koay2008_gaussian_tlm_diffusion = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(koay2008_gaussian_tlm_diffusion)


def test_koay2008_gaussian_tlm_diffusion_experimental_benchmark(tmp_path):
    output = tmp_path / "koay2008_gaussian_tlm_diffusion.json"

    result = koay2008_gaussian_tlm_diffusion.run_benchmark(output, figure_dir=None)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "koay2008-gaussian-tlm-diffusion-experimental"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (101, 101)
    assert loaded.grid_spacing == (0.001, 0.001)
    assert loaded.dt == 0.001
    assert loaded.steps == 50

    assert loaded.parameters["modes"] == [
        "analytical_gaussian",
        "ftcs_reference",
        "parabolic_tlm_equal_pulse_initialisation",
        "parabolic_tlm_estimated_from_zero_initialisation",
    ]
    assert loaded.parameters["diffusivity_parameterisation"] == "D = dx**2 / (4 * dt)"
    assert loaded.metrics["ftcs_max_relative_rms_error"] <= loaded.tolerances[
        "ftcs_max_relative_rms_error"
    ]
    assert loaded.metrics["parabolic_tlm_equal_max_relative_rms_error"] <= loaded.tolerances[
        "parabolic_tlm_equal_max_relative_rms_error"
    ]
    assert loaded.metrics["parabolic_tlm_estimated_max_relative_rms_error"] <= loaded.tolerances[
        "parabolic_tlm_estimated_max_relative_rms_error"
    ]
    assert loaded.metrics["ftcs_max_masked_relative_error"] <= loaded.tolerances[
        "max_masked_relative_error"
    ]
    assert loaded.metrics["parabolic_tlm_equal_mass_relative_change"] <= loaded.tolerances[
        "mass_relative_change"
    ]
    assert loaded.metrics["parabolic_tlm_estimated_mass_relative_change"] <= loaded.tolerances[
        "mass_relative_change"
    ]
    assert loaded.metrics["estimator_initial_rms_error"] <= loaded.tolerances[
        "estimator_initial_rms_error"
    ]
    assert loaded.metrics["estimator_initial_mass_relative_error"] <= loaded.tolerances[
        "estimator_initial_mass_relative_error"
    ]
    assert loaded.metrics["estimator_iterations"] > 0
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)


def test_koay2008_gaussian_tlm_diffusion_figure_generation(tmp_path):
    pytest.importorskip("matplotlib")
    output = tmp_path / "koay2008_gaussian_tlm_diffusion.json"
    figure_dir = tmp_path / "figures"

    result = koay2008_gaussian_tlm_diffusion.run_benchmark(output, figure_dir=figure_dir)
    loaded = BenchmarkResult.from_json(output)

    assert loaded == result
    for key in [
        "gaussian_initial_profile",
        "centre_node_transient",
        "relative_error",
        "estimator_convergence",
        "naive_vs_estimated_initialisation",
    ]:
        assert key in loaded.artifacts
        assert Path(loaded.artifacts[key]).exists()
        assert Path(loaded.artifacts[key]).suffix == ".png"
