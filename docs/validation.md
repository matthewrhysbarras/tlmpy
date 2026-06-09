# Validation

Current tests cover port-energy conservation, exact `dt`, boundary non-periodicity, propagation-based mesh-speed regression, obstacle-mask behavior, SimulationResult NPZ round trips, CLI behavior, Gaussian diffusion, and conservative Neumann mass conservation.

The propagation-based wave-speed test uses two probes and cross-correlation. Its tolerance is intentionally looser than the exact `dt` formula test because v0.1 has numerical dispersion and a finite-band source pulse. Boundary tests include an early-time opposite-edge probe check designed to fail for accidental periodic wraparound.

Obstacle validation is limited to documented v0.1 behavior: circular mask construction, finite fields, propagation changes relative to no obstacle, and no unbounded port-energy growth under reflective conditions. These tests do not claim material-interface accuracy.

Benchmark scripts currently record homogeneous travel-time behavior and a
source-free boundary behavior case. The boundary benchmark demonstrates
reflective port-energy conservation and matched-boundary energy loss for one
deterministic setup; it does not claim a full absorbing boundary condition.

The Koay 2008 Gaussian diffusion case-study benchmark now includes an
experimental parabolic link-plus-stub pulse-state prototype and estimator
feedback under `tlmpy.experimental`. It is a partial reproduction path only:
the FTCS reference and equal-pulse parabolic node match the analytical Gaussian
case closely for the selected setup. Because that setup has `Ys = 0`, the
equal-pulse parabolic node is expected to match the FTCS update and is not
independent validation. The estimator feedback reports non-convergence against
the strict benchmark tolerance and still requires independent review before it
can be called a full reproduction of the paper.

Tolerances are intentionally stated in tests and should be tightened only after dispersion characterization.

## Validation Planning Documents

Additional validation planning documents:

- [Validation checklist](validation_checklist.md)
- [Benchmarking](benchmarking.md)
- [Dispersion characterisation design](design/dispersion_characterisation.md)
- [Boundary-condition characterisation design](design/boundary_characterisation.md)
- [Benchmarking against references design](design/benchmarking_against_references.md)
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
