"""Boundary behavior benchmark for the existing homogeneous scalar-wave solver.

This benchmark records two source-free checks for current v0.1 boundary
handling:

- reflective boundaries conserve total four-port energy in a closed domain;
- matched boundaries remove energy from the domain for the same initial state.

It characterises the current first-order termination behavior only. It is not a
PML benchmark and does not estimate a general reflection coefficient.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from tlmpy import Grid2D
from tlmpy.benchmarking import BenchmarkResult, make_benchmark_result
from tlmpy.physics import ScalarWaveTLM2D

DEFAULT_OUTPUT = Path("outputs/benchmarks/boundary_reflection.json")
DEFAULT_STEPS = 60
DEFAULT_SEED = 20240609


def _port_energy(solver: ScalarWaveTLM2D) -> float:
    return float(np.sum(solver.n**2 + solver.s**2 + solver.e**2 + solver.w**2))


def _solver_with_ports(
    grid: Grid2D,
    initial_ports: dict[str, np.ndarray],
    boundary: str,
) -> ScalarWaveTLM2D:
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary=boundary)
    solver.n = initial_ports["n"].copy()
    solver.s = initial_ports["s"].copy()
    solver.e = initial_ports["e"].copy()
    solver.w = initial_ports["w"].copy()
    return solver


def run_benchmark(output_path: str | Path = DEFAULT_OUTPUT) -> BenchmarkResult:
    """Run the deterministic boundary benchmark and write a JSON result."""
    grid = Grid2D((36, 34), (1.0, 1.0))
    rng = np.random.default_rng(DEFAULT_SEED)
    initial_ports = {
        port: rng.normal(scale=0.1, size=grid.shape) for port in ("n", "s", "e", "w")
    }
    steps = DEFAULT_STEPS
    reflective_tolerance = 1e-12
    matched_energy_ratio_limit = 0.95

    reflective = _solver_with_ports(grid, initial_ports, "reflective")
    matched = _solver_with_ports(grid, initial_ports, "matched")
    initial_energy = _port_energy(reflective)

    for _ in range(steps):
        reflective.step()
        matched.step()

    reflective_final_energy = _port_energy(reflective)
    matched_final_energy = _port_energy(matched)
    reflective_relative_energy_change = (
        abs(reflective_final_energy - initial_energy) / initial_energy
    )
    matched_energy_ratio = matched_final_energy / initial_energy
    reflective_passed = reflective_relative_energy_change <= reflective_tolerance
    matched_passed = matched_energy_ratio <= matched_energy_ratio_limit
    passed = reflective_passed and matched_passed

    result = make_benchmark_result(
        name="boundary-reflection",
        backend="numpy",
        grid_shape=grid.shape,
        grid_spacing=grid.spacing,
        dt=reflective.dt,
        steps=steps,
        parameters={
            "wave_speed": reflective.wave_speed,
            "seed": DEFAULT_SEED,
            "initial_port_distribution": "normal",
            "initial_port_scale": 0.1,
            "boundaries": ["reflective", "matched"],
            "source_free": True,
        },
        metrics={
            "initial_energy": initial_energy,
            "reflective_final_energy": reflective_final_energy,
            "reflective_relative_energy_change": reflective_relative_energy_change,
            "reflective_passed": reflective_passed,
            "matched_final_energy": matched_final_energy,
            "matched_energy_ratio": matched_energy_ratio,
            "matched_passed": matched_passed,
            "passed": passed,
        },
        tolerances={
            "reflective_relative_energy_change": reflective_tolerance,
            "matched_energy_ratio": matched_energy_ratio_limit,
        },
        artifacts={"result_json": str(output_path)},
        notes=(
            "Source-free boundary behavior benchmark for existing homogeneous "
            "solver boundaries. The matched boundary is a first-order link "
            "termination, not PML or a full absorbing boundary condition."
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
    print(
        "reflective_relative_energy_change="
        f"{result.metrics['reflective_relative_energy_change']:.6g}"
    )
    print(f"matched_energy_ratio={result.metrics['matched_energy_ratio']:.6g}")
    print(f"passed={result.metrics['passed']}")
    return 0 if result.metrics["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
