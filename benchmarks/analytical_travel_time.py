"""Analytical homogeneous scalar-wave travel-time benchmark.

This benchmark exercises the existing homogeneous 2D scalar TLM-style solver and
compares a two-probe measured propagation speed against the mesh-speed relation
``dx / (dt * sqrt(2))``. It does not validate heterogeneous media, PML, or
external-solver agreement.
"""

from __future__ import annotations

import argparse
from math import sqrt
from pathlib import Path

from tlmpy import Grid2D
from tlmpy.benchmarking import BenchmarkResult, make_benchmark_result
from tlmpy.core.probes import PointProbe2D
from tlmpy.core.sources import PointSource2D, RickerPulse
from tlmpy.physics import ScalarWaveTLM2D
from tlmpy.validation.analytical import estimate_wave_speed_from_probes

DEFAULT_OUTPUT = Path("outputs/benchmarks/analytical_travel_time.json")


def run_benchmark(output_path: str | Path = DEFAULT_OUTPUT) -> BenchmarkResult:
    """Run the deterministic travel-time benchmark and write a JSON result."""
    grid = Grid2D((180, 90), (1.0, 1.0))
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary="matched")
    source_location = (45, 45)
    first_probe = (75, 45)
    second_probe = (115, 45)
    steps = 170
    tolerance = 0.10

    solver.add_source(
        PointSource2D(
            source_location,
            RickerPulse(frequency=0.035, delay=16 * solver.dt),
        )
    )
    solver.add_probe(PointProbe2D("first", first_probe))
    solver.add_probe(PointProbe2D("second", second_probe))

    simulation = solver.run(steps=steps)
    distance = (second_probe[0] - first_probe[0]) * grid.dx
    measured_speed = estimate_wave_speed_from_probes(
        simulation.probes["first"],
        simulation.probes["second"],
        distance=distance,
        dt=simulation.dt,
    )
    expected_speed = grid.dx / (simulation.dt * sqrt(2))
    relative_error = abs(measured_speed - expected_speed) / expected_speed

    result = make_benchmark_result(
        name="analytical-travel-time",
        backend="numpy",
        grid_shape=grid.shape,
        grid_spacing=grid.spacing,
        dt=simulation.dt,
        steps=steps,
        parameters={
            "boundary": "matched",
            "wave_speed": solver.wave_speed,
            "source_location": list(source_location),
            "first_probe": list(first_probe),
            "second_probe": list(second_probe),
            "distance": distance,
            "source": {
                "type": "RickerPulse",
                "frequency": 0.035,
                "delay_steps": 16,
            },
            "arrival_estimator": "cross_correlation",
        },
        metrics={
            "measured_speed": measured_speed,
            "expected_speed": expected_speed,
            "relative_error": relative_error,
            "passed": relative_error <= tolerance,
        },
        tolerances={"relative_error": tolerance},
        artifacts={"result_json": str(output_path)},
        notes=(
            "Homogeneous mesh-speed benchmark only. The tolerance accounts for "
            "numerical dispersion and finite source bandwidth."
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
    print(f"relative_error={result.metrics['relative_error']:.6g}")
    print(f"passed={result.metrics['passed']}")
    return 0 if result.metrics["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

