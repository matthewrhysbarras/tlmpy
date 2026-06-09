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


def run_benchmark(output_path: str | Path = DEFAULT_OUTPUT) -> BenchmarkResult:
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
    previous_step = 0
    final_field = initial
    for step in selected_steps:
        result = solver.run(step - previous_step, dt=dt, store_final_field=True)
        final_field = result.final_field
        expected = analytical_gaussian(grid, theta, diffusivity, t0, step * dt, center)
        center_value = final_field[grid.nx // 2, grid.ny // 2]
        expected_center = expected[grid.nx // 2, grid.ny // 2]
        metrics[f"step_{step}_relative_rms_error"] = _relative_rms(final_field, expected)
        metrics[f"step_{step}_center_relative_error"] = float(
            abs(center_value - expected_center) / expected_center
        )
        metrics[f"step_{step}_masked_max_relative_error"] = _masked_max_relative_error(
            final_field, expected
        )
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
        artifacts={"result_json": str(output_path)},
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
    args = parser.parse_args(argv)

    result = run_benchmark(args.output)
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
