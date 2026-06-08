"""Probe definitions."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PointProbe2D:
    name: str
    location: tuple[int, int]
    values: list[float] = field(default_factory=list)

    def record(self, value: float) -> None:
        self.values.append(float(value))

