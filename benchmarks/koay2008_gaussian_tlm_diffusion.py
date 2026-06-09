"""Koay et al. 2008 Gaussian diffusion case-study benchmark.

This benchmark is Stage 1 infrastructure for a possible parabolic TLM diffusion
case study inspired by Koay, Wilkinson and Pulko (2008). It uses TLMpy's existing
FTCS diffusion reference solver and the analytical Gaussian diffusion solution
from the paper's Section 6.

It does not implement the paper's pulse-state parabolic TLM solver or nodal
state estimator.
"""

from __future__ import annotations

import argparse
from math import pi
from pathlib import Path

import numpy as np

from tlmpy import Grid2D
from tlmpy.benchmarking import BenchmarkResult, make_benchmark_result
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


def _save_figures(
    figure_dir: Path,
    grid: Grid2D,
    initial: np.ndarray,
    centre_times: list[float],
    numerical_centre: list[float],
    analytical_centre: list[float],
    centre_relative_errors: list[float],
    masked_max_relative_errors: list[float],
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
    ax.plot(centre_times, analytical_centre, "o-", label="analytical", color="tab:blue")
    ax.plot(centre_times, numerical_centre, "s--", label="FTCS reference", color="tab:orange")
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
        centre_times[1:],
        centre_relative_errors,
        "o-",
        label="centre-node relative error",
        color="tab:red",
    )
    ax.plot(
        centre_times[1:],
        masked_max_relative_errors,
        "s--",
        label="masked maximum relative error",
        color="tab:purple",
    )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("relative error")
    ax.set_title("Gaussian benchmark relative errors")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(error_path, dpi=160)
    plt.close(fig)

    return {
        "gaussian_initial_profile": str(initial_path),
        "centre_node_transient": str(transient_path),
        "relative_error": str(error_path),
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

    solver = Diffusion2D(grid, diffusivity=diffusivity, boundary="neumann")
    initial = analytical_gaussian(grid, theta, diffusivity, t0, 0.0, center)
    initial_mass = float(initial.sum() * grid.dx * grid.dy)
    solver.set_initial_condition(initial)

    metrics: dict[str, float | int | str | bool] = {}
    centre_times = [0.0]
    numerical_centre = [float(initial[grid.nx // 2, grid.ny // 2])]
    analytical_centre = [float(initial[grid.nx // 2, grid.ny // 2])]
    centre_relative_errors: list[float] = []
    masked_max_relative_errors: list[float] = []
    previous_step = 0
    final_field = initial
    for step in selected_steps:
        result = solver.run(step - previous_step, dt=dt, store_final_field=True)
        final_field = result.final_field
        expected = analytical_gaussian(grid, theta, diffusivity, t0, step * dt, center)
        center_value = final_field[grid.nx // 2, grid.ny // 2]
        expected_center = expected[grid.nx // 2, grid.ny // 2]
        metrics[f"step_{step}_relative_rms_error"] = _relative_rms(final_field, expected)
        center_relative_error = float(abs(center_value - expected_center) / expected_center)
        masked_max_relative_error = _masked_max_relative_error(final_field, expected)
        metrics[f"step_{step}_center_relative_error"] = center_relative_error
        metrics[f"step_{step}_masked_max_relative_error"] = masked_max_relative_error
        centre_times.append(step * dt)
        numerical_centre.append(float(center_value))
        analytical_centre.append(float(expected_center))
        centre_relative_errors.append(center_relative_error)
        masked_max_relative_errors.append(masked_max_relative_error)
        previous_step = step

    final_mass = float(final_field.sum() * grid.dx * grid.dy)
    mass_relative_change = abs(final_mass - initial_mass) / initial_mass
    max_relative_rms_error = max(
        float(metrics[f"step_{step}_relative_rms_error"]) for step in selected_steps
    )
    max_center_relative_error = max(
        float(metrics[f"step_{step}_center_relative_error"]) for step in selected_steps
    )
    max_masked_relative_error = max(
        float(metrics[f"step_{step}_masked_max_relative_error"]) for step in selected_steps
    )
    tolerances = {
        "max_relative_rms_error": 0.01,
        "max_center_relative_error": 0.01,
        "max_masked_relative_error": 0.15,
        "mass_relative_change": 1e-12,
    }
    passed = (
        max_relative_rms_error <= tolerances["max_relative_rms_error"]
        and max_center_relative_error <= tolerances["max_center_relative_error"]
        and max_masked_relative_error <= tolerances["max_masked_relative_error"]
        and mass_relative_change <= tolerances["mass_relative_change"]
    )
    metrics.update(
        {
            "max_relative_rms_error": max_relative_rms_error,
            "max_center_relative_error": max_center_relative_error,
            "max_masked_relative_error": max_masked_relative_error,
            "initial_mass": initial_mass,
            "final_mass": final_mass,
            "mass_relative_change": mass_relative_change,
            "passed": passed,
        }
    )

    artifacts = {"result_json": str(output_path)}
    if figure_dir is not None:
        artifacts.update(
            _save_figures(
                Path(figure_dir),
                grid,
                initial,
                centre_times,
                numerical_centre,
                analytical_centre,
                centre_relative_errors,
                masked_max_relative_errors,
            )
        )

    result = make_benchmark_result(
        name="koay2008-gaussian-tlm-diffusion-stage1",
        backend="numpy",
        grid_shape=grid.shape,
        grid_spacing=grid.spacing,
        dt=dt,
        steps=max(selected_steps),
        parameters={
            "mode": "existing_ftcs_diffusion_reference_solver",
            "boundary": "neumann",
            "theta": theta,
            "t0": t0,
            "center": list(center),
            "diffusivity": diffusivity,
            "diffusivity_parameterisation": "D = dx**2 / (4 * dt)",
            "selected_steps": list(selected_steps),
            "source_paper": "Koay, Wilkinson and Pulko (2008), Section 6",
        },
        metrics=metrics,
        tolerances=tolerances,
        artifacts=artifacts,
        notes=(
            "Stage 1 Koay 2008 case-study benchmark using the existing FTCS "
            "diffusion reference solver only. It does not implement parabolic "
            "TLM pulse scattering or the nodal state estimator."
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
    print(f"max_relative_rms_error={result.metrics['max_relative_rms_error']:.6g}")
    print(f"max_center_relative_error={result.metrics['max_center_relative_error']:.6g}")
    print(f"max_masked_relative_error={result.metrics['max_masked_relative_error']:.6g}")
    print(f"mass_relative_change={result.metrics['mass_relative_change']:.6g}")
    print(f"passed={result.metrics['passed']}")
    return 0 if result.metrics["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
