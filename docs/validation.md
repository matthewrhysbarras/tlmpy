# Validation

Current tests cover port-energy conservation, exact `dt`, boundary non-periodicity, propagation-based mesh-speed regression, obstacle-mask behavior, SimulationResult NPZ round trips, CLI behavior, Gaussian diffusion, and conservative Neumann mass conservation.

The propagation-based wave-speed test uses two probes and cross-correlation. Its tolerance is intentionally looser than the exact `dt` formula test because v0.1 has numerical dispersion and a finite-band source pulse. Boundary tests include an early-time opposite-edge probe check designed to fail for accidental periodic wraparound.

Obstacle validation is limited to documented v0.1 behavior: circular mask construction, finite fields, propagation changes relative to no obstacle, and no unbounded port-energy growth under reflective conditions. These tests do not claim material-interface accuracy.

Tolerances are intentionally stated in tests and should be tightened only after dispersion characterization.
