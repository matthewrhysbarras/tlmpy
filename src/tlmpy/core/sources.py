"""Temporal signals and spatial source injection."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, pi


@dataclass(frozen=True)
class GaussianPulse:
    """Gaussian temporal signal evaluated in seconds."""

    amplitude: float = 1.0
    center_time: float = 0.0
    width: float = 1.0

    def value(self, t: float) -> float:
        return self.amplitude * exp(-0.5 * ((t - self.center_time) / self.width) ** 2)


@dataclass(frozen=True)
class RickerPulse:
    """Ricker wavelet temporal signal evaluated in seconds."""

    frequency: float
    amplitude: float = 1.0
    delay: float | None = None

    def value(self, t: float) -> float:
        delay = 4.0 / self.frequency if self.delay is None else self.delay
        x = pi * self.frequency * (t - delay)
        return self.amplitude * (1.0 - 2.0 * x * x) * exp(-(x * x))


@dataclass(frozen=True)
class PointSource2D:
    """Point source at integer ``(i, j)`` grid index.

    ``i`` indexes the first grid axis and ``j`` indexes the second. The wave
    solver evaluates ``signal.value(step * dt)`` in seconds and injects one
    quarter of that amplitude into each of the four directional ports.
    """

    location: tuple[int, int]
    signal: GaussianPulse | RickerPulse
