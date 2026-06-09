"""Wavelength/source-bandwidth sweep for homogeneous dispersion checks.

This benchmark sweeps a small set of Ricker-pulse frequencies and propagation
directions for the existing homogeneous 2D scalar TLM-style solver. It estimates
group speed from two probe traces using cross-correlation and records the result
as JSON.

The central wavelength reported here is based on ``expected_speed / frequency``.
The estimator is intentionally simple and CI-friendly; it is not a
phase-velocity measurement and does not replace an analytical TLM dispersion
study.
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

DEFAULT_OUTPUT = Path("outputs/benchmarks/dispersion_wavelength_sweep.json")
FREQUENCIES = (0.02, 0.035, 0.06, 0.08)
DIRECTION_CASES = (
    {
        "name": "x",
        "source": (45, 90),
        "first_probe": (75, 90),
        "second_probe": (115, 90),
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


def _run_case(direction: dict[str, object], frequency: float) -> dict[str, float | str]:
    grid = Grid2D((180, 180), (1.0, 1.0))
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary="matched")
    source = direction["source"]
    first_probe = direction["first_probe"]
    second_probe = direction["second_probe"]
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
    result = solver.run(steps=220)
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
        "direction": str(direction["name"]),
        "frequency": frequency,
        "central_wavelength_cells": expected_speed / frequency,
        "distance": distance,
        "measured_speed": measured_speed,
        "expected_speed": expected_speed,
        "relative_error": relative_error,
    }


def run_benchmark(output_path: str | Path = DEFAULT_OUTPUT) -> BenchmarkResult:
    """Run the deterministic wavelength sweep and write JSON."""
    cases = [
        _run_case(direction, frequency)
        for frequency in FREQUENCIES
        for direction in DIRECTION_CASES
    ]
    errors = [float(case["relative_error"]) for case in cases]
    speeds = [float(case["measured_speed"]) for case in cases]
    expected_speed = float(cases[0]["expected_speed"])
    max_relative_error = max(errors)
    speed_spread_relative = (max(speeds) - min(speeds)) / expected_speed
    max_relative_error_tolerance = 0.10
    speed_spread_tolerance = 0.04
    passed = (
        max_relative_error <= max_relative_error_tolerance
        and speed_spread_relative <= speed_spread_tolerance
    )

    grid = Grid2D((180, 180), (1.0, 1.0))
    metrics = {
        "expected_speed": expected_speed,
        "max_relative_error": max_relative_error,
        "speed_spread_relative": speed_spread_relative,
        "passed": passed,
    }
    for case in cases:
        frequency_key = str(case["frequency"]).replace(".", "_")
        prefix = f"{case['direction']}_f_{frequency_key}"
        metrics[f"{prefix}_measured_speed"] = float(case["measured_speed"])
        metrics[f"{prefix}_relative_error"] = float(case["relative_error"])

    result = make_benchmark_result(
        name="dispersion-wavelength-sweep",
        backend="numpy",
        grid_shape=grid.shape,
        grid_spacing=grid.spacing,
        dt=grid.dx / (expected_speed * sqrt(2)),
        steps=220,
        parameters={
            "boundary": "matched",
            "wave_speed": 1.0,
            "frequencies": list(FREQUENCIES),
            "directions": [
                {
                    "name": str(direction["name"]),
                    "source": list(direction["source"]),
                    "first_probe": list(direction["first_probe"]),
                    "second_probe": list(direction["second_probe"]),
                }
                for direction in DIRECTION_CASES
            ],
            "cases": [
                {
                    "direction": str(case["direction"]),
                    "frequency": float(case["frequency"]),
                    "central_wavelength_cells": float(case["central_wavelength_cells"]),
                    "probe_distance": float(case["distance"]),
                }
                for case in cases
            ],
            "source": {"type": "RickerPulse", "delay_steps": 16},
            "estimator": "two_probe_cross_correlation",
        },
        metrics=metrics,
        tolerances={
            "max_relative_error": max_relative_error_tolerance,
            "speed_spread_relative": speed_spread_tolerance,
        },
        artifacts={"result_json": str(output_path)},
        notes=(
            "Initial homogeneous wavelength/source-bandwidth sweep using "
            "two-probe cross-correlation. This does not measure phase velocity "
            "or prove analytical TLM dispersion agreement."
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
    print(f"speed_spread_relative={result.metrics['speed_spread_relative']:.6g}")
    print(f"passed={result.metrics['passed']}")
    return 0 if result.metrics["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
