"""Experimental parabolic TLM diffusion after Koay et al. 2008.

This module implements the link-plus-stub parabolic node mapping documented in
``docs/derivations/parabolic_tlm_diffusion_koay2008.md``. The estimator is a
practical implementation hypothesis based on Equations 26--28 of Koay,
Wilkinson and Pulko (2008); it is not a complete root-locus reproduction.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tlmpy.core.grid import Grid2D


def parabolic_ys(
    *,
    spacing: float,
    dt: float,
    thermal_conductivity: float,
    specific_heat: float,
    density: float,
) -> float:
    """Return the parabolic TLM stub admittance parameter ``Ys``."""
    if spacing <= 0:
        raise ValueError("spacing must be positive")
    if dt <= 0:
        raise ValueError("dt must be positive")
    if thermal_conductivity <= 0:
        raise ValueError("thermal_conductivity must be positive")
    if specific_heat <= 0:
        raise ValueError("specific_heat must be positive")
    if density <= 0:
        raise ValueError("density must be positive")
    ys = (specific_heat * density * spacing**2) / (thermal_conductivity * dt) - 4.0
    if -1e-12 < ys < 0:
        ys = 0.0
    if ys < 0:
        raise ValueError("Ys must be non-negative; reduce dt or adjust material parameters")
    return float(ys)


@dataclass
class EstimatorHistory:
    """Convergence history for the experimental estimator."""

    rms_error: list[float]
    max_abs_error: list[float]
    iterations: int
    converged: bool


class ParabolicTLMDiffusion2D:
    """Experimental 2D parabolic TLM link-plus-stub diffusion model.

    The state arrays are incident pulse arrays. Nodal temperature is derived as
    ``2 * (v1 + v2 + v3 + v4 + Ys*vs) / (4 + Ys)``.
    """

    def __init__(
        self,
        grid: Grid2D,
        *,
        dt: float,
        thermal_conductivity: float,
        specific_heat: float,
        density: float,
    ) -> None:
        if grid.dx != grid.dy:
            raise ValueError("ParabolicTLMDiffusion2D requires square spacing")
        self.grid = grid
        self.dt = float(dt)
        self.thermal_conductivity = float(thermal_conductivity)
        self.specific_heat = float(specific_heat)
        self.density = float(density)
        self.d = 1.0 / grid.dx**2
        self.ys = parabolic_ys(
            spacing=grid.dx,
            dt=dt,
            thermal_conductivity=thermal_conductivity,
            specific_heat=specific_heat,
            density=density,
        )
        self.v1 = np.zeros(grid.shape, dtype=float)
        self.v2 = np.zeros(grid.shape, dtype=float)
        self.v3 = np.zeros(grid.shape, dtype=float)
        self.v4 = np.zeros(grid.shape, dtype=float)
        self.vs = np.zeros(grid.shape, dtype=float)
        self.r1 = np.zeros(grid.shape, dtype=float)
        self.r2 = np.zeros(grid.shape, dtype=float)
        self.r3 = np.zeros(grid.shape, dtype=float)
        self.r4 = np.zeros(grid.shape, dtype=float)
        self.rs = np.zeros(grid.shape, dtype=float)

    @property
    def diffusivity(self) -> float:
        """Thermal diffusivity ``K / (rho*c_p)``."""
        return self.thermal_conductivity / (self.specific_heat * self.density)

    def set_equal_pulse_temperature(self, temperature) -> None:
        """Set all incident pulse arrays to represent a target temperature."""
        arr = np.asarray(temperature, dtype=float)
        if arr.shape != self.grid.shape:
            raise ValueError("temperature shape must match grid")
        if not np.isfinite(arr).all():
            raise ValueError("temperature must be finite")
        pulse = 0.5 * arr
        self.v1 = pulse.copy()
        self.v2 = pulse.copy()
        self.v3 = pulse.copy()
        self.v4 = pulse.copy()
        self.vs = pulse.copy()

    def temperature(self) -> np.ndarray:
        """Return nodal potential/temperature from incident pulses."""
        return 2.0 * (self.v1 + self.v2 + self.v3 + self.v4 + self.ys * self.vs) / (
            4.0 + self.ys
        )

    def scatter(self) -> None:
        """Scatter incident pulses into reflected pulses."""
        t = self.temperature()
        link_reflection = 0.5 * t
        self.r1 = link_reflection.copy()
        self.r2 = link_reflection.copy()
        self.r3 = link_reflection.copy()
        self.r4 = link_reflection.copy()
        self.rs = t - self.vs

    def connect(self) -> None:
        """Connect reflected pulses into next-step incident pulses."""
        nv1 = np.empty_like(self.v1)
        nv2 = np.empty_like(self.v2)
        nv3 = np.empty_like(self.v3)
        nv4 = np.empty_like(self.v4)

        nv1[:-1, :] = self.r2[1:, :]
        nv1[-1, :] = self.r2[-1, :]
        nv2[1:, :] = self.r1[:-1, :]
        nv2[0, :] = self.r1[0, :]
        nv3[:, :-1] = self.r4[:, 1:]
        nv3[:, -1] = self.r4[:, -1]
        nv4[:, 1:] = self.r3[:, :-1]
        nv4[:, 0] = self.r3[:, 0]

        self.v1, self.v2, self.v3, self.v4, self.vs = nv1, nv2, nv3, nv4, self.rs.copy()

    def step(self) -> None:
        """Advance one scatter/connect step."""
        self.scatter()
        self.connect()
        self._validate_finite()

    def run(self, steps: int) -> list[np.ndarray]:
        """Advance and return temperature snapshots after each step."""
        if steps < 0:
            raise ValueError("steps must be non-negative")
        out = []
        for _ in range(steps):
            self.step()
            out.append(self.temperature().copy())
        return out

    def pulse_energy_proxy(self) -> float:
        """Return a non-physical but useful pulse-state boundedness proxy."""
        return float(
            np.sum(self.v1**2 + self.v2**2 + self.v3**2 + self.v4**2 + self.ys * self.vs**2)
        )

    def _validate_finite(self) -> None:
        arrays = [self.v1, self.v2, self.v3, self.v4, self.vs]
        if not all(np.isfinite(a).all() for a in arrays):
            raise FloatingPointError("non-finite parabolic TLM state")


class TLMStateEstimator:
    """Experimental nodal-state estimator feedback for parabolic TLM states."""

    def __init__(self, model: ParabolicTLMDiffusion2D, *, ld: float) -> None:
        if ld <= 2:
            raise ValueError("ld must be greater than 2")
        self.model = model
        self.ld = float(ld)
        self.previous_error = np.zeros(model.grid.shape, dtype=float)
        self.previous_link_correction = np.zeros(model.grid.shape, dtype=float)
        self.previous_stub_correction = np.zeros(model.grid.shape, dtype=float)

    def correction(self, target_temperature) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute and apply one estimator correction to the incident pulse state."""
        target = np.asarray(target_temperature, dtype=float)
        if target.shape != self.model.grid.shape:
            raise ValueError("target_temperature shape must match grid")
        if not np.isfinite(target).all():
            raise ValueError("target_temperature must be finite")
        estimated = self.model.temperature()
        error = target - estimated
        predicted_error = error + (error - self.previous_error)
        link_correction = (
            error + (self.ld - 2.0) * self.previous_link_correction
        ) / self.ld
        stub_correction = (
            -predicted_error + error + (self.ld - 2.0) * self.previous_stub_correction
        ) / self.ld

        self.model.v1 += link_correction
        self.model.v2 += link_correction
        self.model.v3 += link_correction
        self.model.v4 += link_correction
        self.model.vs += stub_correction
        self.model._validate_finite()

        self.previous_error = error
        self.previous_link_correction = link_correction
        self.previous_stub_correction = stub_correction
        return error, link_correction, stub_correction

    def converge_to_target(
        self,
        target_temperature,
        *,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
        advance_model: bool = False,
    ) -> EstimatorHistory:
        """Iterate estimator corrections until the target potential is approached."""
        if max_iterations < 0:
            raise ValueError("max_iterations must be non-negative")
        if tolerance <= 0:
            raise ValueError("tolerance must be positive")
        rms_history: list[float] = []
        max_history: list[float] = []
        converged = False
        for iteration in range(max_iterations):
            error, _, _ = self.correction(target_temperature)
            rms = float(np.sqrt(np.mean(error**2)))
            max_abs = float(np.max(np.abs(error)))
            rms_history.append(rms)
            max_history.append(max_abs)
            if rms <= tolerance:
                converged = True
                return EstimatorHistory(rms_history, max_history, iteration + 1, converged)
            if advance_model:
                self.model.step()
        return EstimatorHistory(rms_history, max_history, max_iterations, converged)
