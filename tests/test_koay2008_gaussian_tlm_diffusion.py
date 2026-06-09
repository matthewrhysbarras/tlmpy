import importlib.util
from pathlib import Path

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "benchmarks" / "koay2008_gaussian_tlm_diffusion.py"
)
SPEC = importlib.util.spec_from_file_location("koay2008_gaussian_tlm_diffusion", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
koay2008_gaussian_tlm_diffusion = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(koay2008_gaussian_tlm_diffusion)


def test_koay2008_gaussian_tlm_diffusion_stage1_benchmark(tmp_path):
    output = tmp_path / "koay2008_gaussian_tlm_diffusion.json"
    figure_dir = tmp_path / "figures"

    result = koay2008_gaussian_tlm_diffusion.run_benchmark(output, figure_dir=figure_dir)
    loaded = BenchmarkResult.from_json(output)

    assert output.exists()
    assert loaded == result
    assert loaded.name == "koay2008-gaussian-tlm-diffusion-stage1"
    assert loaded.package_version == __version__
    assert loaded.backend == "numpy"
    assert loaded.grid_shape == (101, 101)
    assert loaded.grid_spacing == (0.001, 0.001)
    assert loaded.dt == 0.001
    assert loaded.steps == 50

    assert loaded.parameters["mode"] == "existing_ftcs_diffusion_reference_solver"
    assert loaded.parameters["diffusivity_parameterisation"] == "D = dx**2 / (4 * dt)"
    assert loaded.metrics["max_relative_rms_error"] <= loaded.tolerances[
        "max_relative_rms_error"
    ]
    assert loaded.metrics["max_center_relative_error"] <= loaded.tolerances[
        "max_center_relative_error"
    ]
    assert loaded.metrics["max_masked_relative_error"] <= loaded.tolerances[
        "max_masked_relative_error"
    ]
    assert loaded.metrics["mass_relative_change"] <= loaded.tolerances["mass_relative_change"]
    assert loaded.metrics["passed"] is True
    assert loaded.artifacts["result_json"] == str(output)
    for key in [
        "gaussian_initial_profile",
        "centre_node_transient",
        "relative_error",
    ]:
        assert key in loaded.artifacts
        assert Path(loaded.artifacts[key]).exists()
        assert Path(loaded.artifacts[key]).suffix == ".png"
