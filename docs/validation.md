# Validation

Current tests cover port-energy conservation, exact `dt`, boundary non-periodicity, propagation-based mesh-speed regression, obstacle-mask behavior, SimulationResult NPZ round trips, CLI behavior, Gaussian diffusion, and conservative Neumann mass conservation.

The propagation-based wave-speed test uses two probes and cross-correlation. Its tolerance is intentionally looser than the exact `dt` formula test because v0.1 has numerical dispersion and a finite-band source pulse. Boundary tests include an early-time opposite-edge probe check designed to fail for accidental periodic wraparound.

Obstacle validation is limited to documented v0.1 behavior: circular mask construction, finite fields, propagation changes relative to no obstacle, and no unbounded port-energy growth under reflective conditions. These tests do not claim material-interface accuracy.

Tolerances are intentionally stated in tests and should be tightened only after dispersion characterization.

## Validation Planning Documents

Additional validation planning documents:

- [Validation checklist](validation_checklist.md)
- [Dispersion characterisation design](design/dispersion_characterisation.md)
- [Boundary-condition characterisation design](design/boundary_characterisation.md)
- [Stub-loaded heterogeneous 2D TLM design](design/stub_loaded_2d_tlm.md)

## v0.2 Heterogeneous TLM Validation Plan

Stub-loaded heterogeneous 2D TLM is future design work. No public heterogeneous
solver is implemented yet. A future solver must pass validation before it becomes
public API. Required cases:

1. Homogeneous limit: the loaded formulation must match v0.1 `ScalarWaveTLM2D`
   for a constant wave speed.
2. Interface reflection/transmission: a 1D or quasi-1D interface should match an
   analytical coefficient where available.
3. Two-media travel time: measured arrival should match the sum of segment travel
   times through each medium within a dispersion-aware tolerance.
4. Energy/passivity: closed reflective domains should not exhibit unphysical
   growth.
5. Stability sweep: test wave-speed contrast, timestep safety factor, and
   interface placement.
6. External reference: compare at least one simple case against an analytical
   solution or established solver if feasible.

Obstacle-mask tests do not satisfy these heterogeneous-media requirements. The
stub-loaded formulation needs its own validation suite.
