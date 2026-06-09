"""Koay et al. 2008 Gaussian diffusion case-study benchmark.

This benchmark compares the Section 6 Gaussian analytical diffusion profile with:

1. TLMpy's existing FTCS diffusion reference solver;
2. the experimental parabolic link-plus-stub TLM solver with equal-pulse
   initialization;
3. the experimental estimator feedback initialized from zero.

The parabolic node update is implemented from the paper's Equations 5--10 and
13/16. The estimator is an implementation hypothesis based on Equations 26--28,
not a full root-locus reproduction of the paper.
"""

from __future__ import annotations

import argparse
from math import pi
from pathlib import Path

import numpy as np

from tlmpy import Grid2D
from tlmpy.benchmarking import BenchmarkResult, make_benchmark_result
from tlmpy.experimental import ParabolicTLMDiffusion2D, TLMStateEstimator
from tlmpy.physics import Diffusion2D

DEFAULT_OUTPUT = Path("outputs/benchmarks/koay2008_gaussian_tlm_diffusion.json")
DEFAULT_FIGURE_DIR = Path("docs/assets/koay2008_gaussian_diffusion")


def analytical_gaussian(
    grid: Grid2D,
    theta: float,
    diffusivity: float,
    t0: float,
    t: float,
    center: tuple[float, float],
) -> np.ndarray:
    """Return the Section 6 infinite-domain Gaussian diffusion profile."""
    tau = t0 + t
    x = np.arange(grid.nx)[:, None] * grid.dx
    y = np.arange(grid.ny)[None, :] * grid.dy
    r2 = (x - center[0]) ** 2 + (y - center[1]) ** 2
    return theta / (4.0 * pi * diffusivity * tau) * np.exp(
        -r2 / (4.0 * diffusivity * tau)
    )


def _relative_rms(numerical: np.ndarray, expected: np.ndarray) -> float:
    return float(np.sqrt(np.mean((numerical - expected) ** 2)) / np.sqrt(np.mean(expected**2)))


def _masked_max_relative_error(numerical: np.ndarray, expected: np.ndarray) -> float:
    mask = expected > expected.max() * 1e-6
    return float(np.max(np.abs(numerical[mask] - expected[mask]) / expected[mask]))


def _summarize_mode(
    metrics: dict[str, float | int | str | bool],
    prefix: str,
    fields: dict[int, np.ndarray],
    expected: dict[int, np.ndarray],
    grid: Grid2D,
    initial_mass: float,
) -> None:
    rms_values = []
    centre_values = []
    masked_values = []
    for step, field in fields.items():
        exp = expected[step]
        centre = field[grid.nx // 2, grid.ny // 2]
        expected_centre = exp[grid.nx // 2, grid.ny // 2]
        rms = _relative_rms(field, exp)
        centre_error = float(abs(centre - expected_centre) / expected_centre)
        masked_error = _masked_max_relative_error(field, exp)
        metrics[f"{prefix}_step_{step}_relative_rms_error"] = rms
        metrics[f"{prefix}_step_{step}_center_relative_error"] = centre_error
        metrics[f"{prefix}_step_{step}_masked_max_relative_error"] = masked_error
        rms_values.append(rms)
        centre_values.append(centre_error)
        masked_values.append(masked_error)
    final_mass = float(fields[max(fields)].sum() * grid.dx * grid.dy)
    metrics[f"{prefix}_max_relative_rms_error"] = max(rms_values)
    metrics[f"{prefix}_max_center_relative_error"] = max(centre_values)
    metrics[f"{prefix}_max_masked_relative_error"] = max(masked_values)
    metrics[f"{prefix}_mass_relative_change"] = abs(final_mass - initial_mass) / initial_mass


def _run_ftcs(
    grid: Grid2D,
    diffusivity: float,
    dt: float,
    initial: np.ndarray,
    selected_steps: tuple[int, ...],
) -> dict[int, np.ndarray]:
    solver = Diffusion2D(grid, diffusivity=diffusivity, boundary="neumann")
    solver.set_initial_condition(initial)
    fields = {}
    previous = 0
    for step in selected_steps:
        result = solver.run(step - previous, dt=dt, store_final_field=True)
        fields[step] = result.final_field
        previous = step
    return fields


def _make_tlm_model(grid: Grid2D, diffusivity: float, dt: float) -> ParabolicTLMDiffusion2D:
    specific_heat = 300.0
    density = 8930.0
    thermal_conductivity = diffusivity * specific_heat * density
    return ParabolicTLMDiffusion2D(
        grid,
        dt=dt,
        thermal_conductivity=thermal_conductivity,
        specific_heat=specific_heat,
        density=density,
    )


def _run_tlm(
    model: ParabolicTLMDiffusion2D,
    selected_steps: tuple[int, ...],
) -> dict[int, np.ndarray]:
    fields = {}
    previous = 0
    for step in selected_steps:
        model.run(step - previous)
        fields[step] = model.temperature().copy()
        previous = step
    return fields


def _save_figures(
    figure_dir: Path,
    grid: Grid2D,
    dt: float,
    initial: np.ndarray,
    selected_steps: tuple[int, ...],
    expected_fields: dict[int, np.ndarray],
    ftcs_fields: dict[int, np.ndarray],
    tlm_fields: dict[int, np.ndarray],
    estimated_fields: dict[int, np.ndarray],
    estimator_history: list[float],
) -> dict[str, str]:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - exercised only without viz extras
        raise RuntimeError(
            "matplotlib is required to generate documentation figures; "
            "install TLMpy with the viz extra or run with --figure-dir none"
        ) from exc

    figure_dir.mkdir(parents=True, exist_ok=True)
    x = np.arange(grid.nx) * grid.dx
    centre_j = grid.ny // 2
    times = [0.0, *(step * dt for step in selected_steps)]
    expected_centre = [
        float(initial[grid.nx // 2, grid.ny // 2]),
        *(float(expected_fields[step][grid.nx // 2, grid.ny // 2]) for step in selected_steps),
    ]
    ftcs_centre = [
        float(initial[grid.nx // 2, grid.ny // 2]),
        *(float(ftcs_fields[step][grid.nx // 2, grid.ny // 2]) for step in selected_steps),
    ]
    tlm_centre = [
        float(initial[grid.nx // 2, grid.ny // 2]),
        *(float(tlm_fields[step][grid.nx // 2, grid.ny // 2]) for step in selected_steps),
    ]
    estimated_centre = [
        float(estimated_fields[0][grid.nx // 2, grid.ny // 2]),
        *(float(estimated_fields[step][grid.nx // 2, grid.ny // 2]) for step in selected_steps),
    ]

    initial_path = figure_dir / "gaussian_initial_profile.png"
    fig, ax = plt.subplots(figsize=(6.0, 3.6), constrained_layout=True)
    ax.plot(x, initial[:, centre_j], color="tab:blue", linewidth=2)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("temperature")
    ax.set_title("Initial Gaussian centre cross-section")
    ax.grid(True, alpha=0.3)
    fig.savefig(initial_path, dpi=160)
    plt.close(fig)

    transient_path = figure_dir / "centre_node_transient.png"
    fig, ax = plt.subplots(figsize=(6.0, 3.6), constrained_layout=True)
    ax.plot(times, expected_centre, "o-", label="analytical", color="tab:blue")
    ax.plot(times, ftcs_centre, "s--", label="FTCS", color="tab:orange")
    ax.plot(times, tlm_centre, "^--", label="parabolic TLM", color="tab:green")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("centre temperature")
    ax.set_title("Centre-node transient")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(transient_path, dpi=160)
    plt.close(fig)

    error_path = figure_dir / "relative_error.png"
    fig, ax = plt.subplots(figsize=(6.0, 3.6), constrained_layout=True)
    ax.plot(
        [step * dt for step in selected_steps],
        [_relative_rms(ftcs_fields[step], expected_fields[step]) for step in selected_steps],
        "o-",
        label="FTCS RMS",
    )
    ax.plot(
        [step * dt for step in selected_steps],
        [_relative_rms(tlm_fields[step], expected_fields[step]) for step in selected_steps],
        "s--",
        label="parabolic TLM RMS",
    )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("relative RMS error")
    ax.set_title("Gaussian benchmark relative error")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(error_path, dpi=160)
    plt.close(fig)

    convergence_path = figure_dir / "estimator_convergence.png"
    fig, ax = plt.subplots(figsize=(6.0, 3.6), constrained_layout=True)
    ax.semilogy(np.arange(1, len(estimator_history) + 1), estimator_history, color="tab:red")
    ax.set_xlabel("estimator iteration")
    ax.set_ylabel("RMS target error")
    ax.set_title("Experimental estimator convergence")
    ax.grid(True, alpha=0.3)
    fig.savefig(convergence_path, dpi=160)
    plt.close(fig)

    init_path = figure_dir / "naive_vs_estimated_initialisation.png"
    fig, ax = plt.subplots(figsize=(6.0, 3.6), constrained_layout=True)
    ax.plot(times, expected_centre, "o-", label="analytical", color="tab:blue")
    ax.plot(times, tlm_centre, "s--", label="equal-pulse init", color="tab:green")
    ax.plot(times, estimated_centre, "^--", label="estimated-from-zero init", color="tab:red")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("centre temperature")
    ax.set_title("Naive vs estimated initialization")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(init_path, dpi=160)
    plt.close(fig)

    return {
        "gaussian_initial_profile": str(initial_path),
        "centre_node_transient": str(transient_path),
        "relative_error": str(error_path),
        "estimator_convergence": str(convergence_path),
        "naive_vs_estimated_initialisation": str(init_path),
    }


def run_benchmark(
    output_path: str | Path = DEFAULT_OUTPUT,
    figure_dir: str | Path | None = DEFAULT_FIGURE_DIR,
) -> BenchmarkResult:
    """Run the deterministic Gaussian diffusion case-study benchmark."""
    grid = Grid2D((101, 101), (0.001, 0.001))
    dt = 0.001
    diffusivity = grid.dx**2 / (4.0 * dt)
    theta = 0.01
    t0 = 0.1
    center = (0.05, 0.05)
    selected_steps = (10, 20, 50)
    expected_fields = {
        step: analytical_gaussian(grid, theta, diffusivity, t0, step * dt, center)
        for step in selected_steps
    }
    initial = analytical_gaussian(grid, theta, diffusivity, t0, 0.0, center)
    initial_mass = float(initial.sum() * grid.dx * grid.dy)

    ftcs_fields = _run_ftcs(grid, diffusivity, dt, initial, selected_steps)
    tlm_model = _make_tlm_model(grid, diffusivity, dt)
    tlm_model.set_equal_pulse_temperature(initial)
    tlm_fields = _run_tlm(tlm_model, selected_steps)

    estimated_model = _make_tlm_model(grid, diffusivity, dt)
    estimated_model.set_equal_pulse_temperature(np.zeros(grid.shape))
    estimator = TLMStateEstimator(estimated_model, ld=10.32)
    history = estimator.converge_to_target(initial, max_iterations=80, tolerance=1e-5)
    estimated_initial = estimated_model.temperature().copy()
    estimated_initial_mass = float(estimated_initial.sum() * grid.dx * grid.dy)
    estimated_fields = {0: estimated_initial}
    estimated_fields.update(_run_tlm(estimated_model, selected_steps))

    metrics: dict[str, float | int | str | bool] = {}
    _summarize_mode(metrics, "ftcs", ftcs_fields, expected_fields, grid, initial_mass)
    _summarize_mode(metrics, "parabolic_tlm_equal", tlm_fields, expected_fields, grid, initial_mass)
    _summarize_mode(
        metrics,
        "parabolic_tlm_estimated",
        estimated_fields,
        {0: initial, **expected_fields},
        grid,
        estimated_initial_mass,
    )
    metrics["estimator_initial_rms_error"] = _relative_rms(estimated_initial, initial)
    metrics["estimator_initial_mass_relative_error"] = (
        abs(estimated_initial_mass - initial_mass) / initial_mass
    )
    metrics["estimator_final_rms_error"] = history.rms_error[-1]
    metrics["estimator_iterations"] = history.iterations
    metrics["estimator_converged"] = history.converged
    metrics["equal_vs_estimated_initial_rms_ratio"] = (
        metrics["parabolic_tlm_equal_step_10_relative_rms_error"]
        / metrics["parabolic_tlm_estimated_step_10_relative_rms_error"]
    )

    tolerances = {
        "ftcs_max_relative_rms_error": 0.01,
        "parabolic_tlm_equal_max_relative_rms_error": 0.01,
        "parabolic_tlm_estimated_max_relative_rms_error": 0.02,
        "max_masked_relative_error": 0.15,
        "mass_relative_change": 1e-12,
        "estimator_initial_rms_error": 1e-3,
        "estimator_initial_mass_relative_error": 1e-3,
    }
    passed = (
        metrics["ftcs_max_relative_rms_error"] <= tolerances["ftcs_max_relative_rms_error"]
        and metrics["parabolic_tlm_equal_max_relative_rms_error"]
        <= tolerances["parabolic_tlm_equal_max_relative_rms_error"]
        and metrics["parabolic_tlm_estimated_max_relative_rms_error"]
        <= tolerances["parabolic_tlm_estimated_max_relative_rms_error"]
        and metrics["ftcs_max_masked_relative_error"] <= tolerances["max_masked_relative_error"]
        and metrics["parabolic_tlm_equal_max_masked_relative_error"]
        <= tolerances["max_masked_relative_error"]
        and metrics["parabolic_tlm_estimated_max_masked_relative_error"]
        <= tolerances["max_masked_relative_error"]
        and metrics["ftcs_mass_relative_change"] <= tolerances["mass_relative_change"]
        and metrics["parabolic_tlm_equal_mass_relative_change"] <= tolerances["mass_relative_change"]
        and metrics["parabolic_tlm_estimated_mass_relative_change"]
        <= tolerances["mass_relative_change"]
        and metrics["estimator_initial_rms_error"] <= tolerances["estimator_initial_rms_error"]
        and metrics["estimator_initial_mass_relative_error"]
        <= tolerances["estimator_initial_mass_relative_error"]
    )
    metrics["passed"] = passed

    artifacts = {"result_json": str(output_path)}
    if figure_dir is not None:
        artifacts.update(
            _save_figures(
                Path(figure_dir),
                grid,
                dt,
                initial,
                selected_steps,
                expected_fields,
                ftcs_fields,
                tlm_fields,
                estimated_fields,
                history.rms_error,
            )
        )

    result = make_benchmark_result(
        name="koay2008-gaussian-tlm-diffusion-experimental",
        backend="numpy",
        grid_shape=grid.shape,
        grid_spacing=grid.spacing,
        dt=dt,
        steps=max(selected_steps),
        parameters={
            "modes": [
                "analytical_gaussian",
                "ftcs_reference",
                "parabolic_tlm_equal_pulse_initialisation",
                "parabolic_tlm_estimated_from_zero_initialisation",
            ],
            "theta": theta,
            "t0": t0,
            "center": list(center),
            "diffusivity": diffusivity,
            "diffusivity_parameterisation": "D = dx**2 / (4 * dt)",
            "selected_steps": list(selected_steps),
            "estimator_ld": 10.32,
            "estimator_max_iterations": 80,
            "source_paper": "Koay, Wilkinson and Pulko (2008), Section 6",
        },
        metrics=metrics,
        tolerances=tolerances,
        artifacts=artifacts,
        notes=(
            "Experimental partial Koay 2008 case-study reproduction. The "
            "parabolic link-plus-stub node is implemented, but the estimator "
            "feedback is a practical hypothesis and not a full root-locus "
            "reproduction. Equal-pulse initialization exactly represents the "
            "initial potential for this Gaussian case."
        ),
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_json(output_path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="JSON output path")
    parser.add_argument(
        "--figure-dir",
        default=str(DEFAULT_FIGURE_DIR),
        help="directory for documentation PNG figures; use 'none' to skip",
    )
    args = parser.parse_args(argv)

    figure_dir = None if args.figure_dir.lower() == "none" else args.figure_dir
    result = run_benchmark(args.output, figure_dir=figure_dir)
    print(f"benchmark={result.name}")
    print(f"output={args.output}")
    print(f"ftcs_max_relative_rms_error={result.metrics['ftcs_max_relative_rms_error']:.6g}")
    print(
        "parabolic_tlm_equal_max_relative_rms_error="
        f"{result.metrics['parabolic_tlm_equal_max_relative_rms_error']:.6g}"
    )
    print(
        "parabolic_tlm_estimated_max_relative_rms_error="
        f"{result.metrics['parabolic_tlm_estimated_max_relative_rms_error']:.6g}"
    )
    print(f"estimator_initial_rms_error={result.metrics['estimator_initial_rms_error']:.6g}")
    print(f"passed={result.metrics['passed']}")
    return 0 if result.metrics["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
