"""Initial homogeneous scalar-wave dispersion-characterisation benchmark.

This benchmark measures direction-dependent group-speed estimates for the
existing homogeneous 2D scalar TLM-style solver using two-probe
cross-correlation. It is an initial CI-friendly dispersion characterization, not
a full phase/group-velocity study versus wavelength.
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

DEFAULT_OUTPUT = Path("outputs/benchmarks/dispersion_characterisation.json")

DIRECTION_CASES = (
    {
        "name": "x",
        "source": (45, 90),
        "first_probe": (75, 90),
        "second_probe": (115, 90),
    },
    {
        "name": "y",
        "source": (90, 45),
        "first_probe": (90, 75),
        "second_probe": (90, 115),
    },
    {
        "name": "diagonal",
        "source": (45, 45),
        "first_probe": (75, 75),
        "second_probe": (105, 105),
    },
)


def _probe_distance(grid: Grid2D, p1: tuple[int, int], p2: tuple[int, int]) -> float:
    dx = (p2[0] - p1[0]) * grid.dx
    dy = (p2[1] - p1[1]) * grid.dy
    return sqrt(dx * dx + dy * dy)


def _run_case(case: dict[str, object], frequency: float) -> dict[str, float | str]:
    grid = Grid2D((180, 180), (1.0, 1.0))
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary="matched")
    source = case["source"]
    first_probe = case["first_probe"]
    second_probe = case["second_probe"]
    assert isinstance(source, tuple)
    assert isinstance(first_probe, tuple)
    assert isinstance(second_probe, tuple)

    solver.add_source(
        PointSource2D(
            source,
            RickerPulse(frequency=frequency, delay=16 * solver.dt),
        )
    )
    solver.add_probe(PointProbe2D("first", first_probe))
    solver.add_probe(PointProbe2D("second", second_probe))
    result = solver.run(steps=200)
    distance = _probe_distance(grid, first_probe, second_probe)
    measured_speed = estimate_wave_speed_from_probes(
        result.probes["first"],
        result.probes["second"],
        distance=distance,
        dt=result.dt,
    )
    expected_speed = grid.dx / (result.dt * sqrt(2))
    relative_error = abs(measured_speed - expected_speed) / expected_speed
    return {
        "name": str(case["name"]),
        "distance": distance,
        "measured_speed": measured_speed,
        "expected_speed": expected_speed,
        "relative_error": relative_error,
        "central_wavelength_cells": expected_speed / frequency,
    }


def run_benchmark(output_path: str | Path = DEFAULT_OUTPUT) -> BenchmarkResult:
    """Run the deterministic directionality benchmark and write JSON."""
    frequency = 0.035
    cases = [_run_case(case, frequency) for case in DIRECTION_CASES]
    speeds = [float(case["measured_speed"]) for case in cases]
    errors = [float(case["relative_error"]) for case in cases]
    expected_speed = float(cases[0]["expected_speed"])
    max_relative_error = max(errors)
    directional_speed_spread = max(speeds) - min(speeds)
    directional_spread_relative = directional_speed_spread / expected_speed
    max_relative_error_tolerance = 0.10
    directional_spread_tolerance = 0.03
    passed = (
        max_relative_error <= max_relative_error_tolerance
        and directional_spread_relative <= directional_spread_tolerance
    )

    grid = Grid2D((180, 180), (1.0, 1.0))
    metrics = {
        "expected_speed": expected_speed,
        "max_relative_error": max_relative_error,
        "directional_speed_spread": directional_speed_spread,
        "directional_spread_relative": directional_spread_relative,
        "passed": passed,
    }
    for case in cases:
        name = str(case["name"])
        metrics[f"{name}_measured_speed"] = float(case["measured_speed"])
        metrics[f"{name}_relative_error"] = float(case["relative_error"])

    result = make_benchmark_result(
        name="dispersion-characterisation",
        backend="numpy",
        grid_shape=grid.shape,
        grid_spacing=grid.spacing,
        dt=grid.dx / (expected_speed * sqrt(2)),
        steps=200,
        parameters={
            "boundary": "matched",
            "wave_speed": 1.0,
            "source": {
                "type": "RickerPulse",
                "frequency": frequency,
                "delay_steps": 16,
                "central_wavelength_cells": expected_speed / frequency,
            },
            "directions": [
                {
                    "name": str(case["name"]),
                    "source": list(direction["source"]),
                    "first_probe": list(direction["first_probe"]),
                    "second_probe": list(direction["second_probe"]),
                    "probe_distance": float(case["distance"]),
                }
                for case, direction in zip(cases, DIRECTION_CASES, strict=True)
            ],
            "estimator": "two_probe_cross_correlation",
        },
        metrics=metrics,
        tolerances={
            "max_relative_error": max_relative_error_tolerance,
            "directional_spread_relative": directional_spread_tolerance,
        },
        artifacts={"result_json": str(output_path)},
        notes=(
            "Initial homogeneous directionality benchmark using two-probe "
            "cross-correlation. This is not a full wavelength-resolved phase or "
            "group-velocity dispersion study."
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
    print(f"max_relative_error={result.metrics['max_relative_error']:.6g}")
    print(f"directional_spread_relative={result.metrics['directional_spread_relative']:.6g}")
    print(f"passed={result.metrics['passed']}")
    return 0 if result.metrics["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
