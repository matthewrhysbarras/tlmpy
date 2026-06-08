"""JSON-friendly benchmark result records.

This module stores metadata and scalar metrics for future validation and
reference-comparison benchmarks. It does not run benchmarks or integrate external
solvers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tlmpy._version import __version__

ScalarMetric = float | int | str | bool


@dataclass
class BenchmarkResult:
    """Serializable benchmark/reference-comparison summary."""

    name: str
    package_version: str
    timestamp_utc: str
    backend: str
    grid_shape: tuple[int, int] | None = None
    grid_spacing: tuple[float, float] | None = None
    dt: float | None = None
    steps: int | None = None
    git_commit: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, ScalarMetric] = field(default_factory=dict)
    tolerances: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)
    notes: str | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.name:
            raise ValueError("benchmark name must be non-empty")
        if not self.backend:
            raise ValueError("backend must be non-empty")
        if self.grid_shape is not None:
            if (
                len(self.grid_shape) != 2
                or any(not isinstance(v, int) or v <= 0 for v in self.grid_shape)
            ):
                raise ValueError("grid_shape must contain two positive integers")
        if self.grid_spacing is not None:
            if len(self.grid_spacing) != 2 or any(float(v) <= 0 for v in self.grid_spacing):
                raise ValueError("grid_spacing must contain two positive floats")
        if self.dt is not None and self.dt <= 0:
            raise ValueError("dt must be positive when provided")
        if self.steps is not None and (not isinstance(self.steps, int) or self.steps < 0):
            raise ValueError("steps must be a non-negative integer when provided")
        for key, value in self.metrics.items():
            if not isinstance(value, (float, int, str, bool)):
                raise TypeError(f"metric {key!r} must be a JSON scalar")
        for key, value in self.artifacts.items():
            if not isinstance(value, str):
                raise TypeError(f"artifact {key!r} must be a string path")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""
        data = {
            "name": self.name,
            "package_version": self.package_version,
            "timestamp_utc": self.timestamp_utc,
            "backend": self.backend,
            "grid_shape": list(self.grid_shape) if self.grid_shape is not None else None,
            "grid_spacing": list(self.grid_spacing) if self.grid_spacing is not None else None,
            "dt": self.dt,
            "steps": self.steps,
            "git_commit": self.git_commit,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "tolerances": self.tolerances,
            "artifacts": self.artifacts,
            "environment": self.environment,
            "notes": self.notes,
        }
        json.dumps(data)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkResult:
        """Build a result from a dictionary produced by :meth:`to_dict`."""
        values = dict(data)
        if values.get("grid_shape") is not None:
            values["grid_shape"] = tuple(values["grid_shape"])
        if values.get("grid_spacing") is not None:
            values["grid_spacing"] = tuple(float(v) for v in values["grid_spacing"])
        return cls(**values)

    def to_json(self, path) -> None:
        """Write the result to a JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def from_json(cls, path) -> BenchmarkResult:
        """Read a result from a JSON file."""
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def make_benchmark_result(
    name: str,
    backend: str,
    *,
    package_version: str = __version__,
    timestamp_utc: str | None = None,
    **kwargs: Any,
) -> BenchmarkResult:
    """Create a :class:`BenchmarkResult` with current package metadata defaults."""
    if timestamp_utc is None:
        timestamp_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return BenchmarkResult(
        name=name,
        package_version=package_version,
        timestamp_utc=timestamp_utc,
        backend=backend,
        **kwargs,
    )

