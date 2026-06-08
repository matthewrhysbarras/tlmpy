# Stub-Loaded 2D TLM Design Notes

This document starts the v0.2 design work for spatially varying wave speed in
TLMpy. It is intentionally a design note, not a public API or production solver
specification.

## Scope And Non-Goals

Scope:

- Design a minimal heterogeneous 2D scalar TLM capability for spatially varying
  wave speed.
- Preserve the existing homogeneous `ScalarWaveTLM2D` API and tests.
- Identify the smallest node formulation that can be validated before any public
  API is added.
- Define validation gates for a future experimental implementation.

Non-goals:

- No PML.
- No 3D EM.
- No heterogeneous model exposed through the v0.1 four-port solver.
- No JAX, Numba, Triton, MPI, GUI, CAD import, ECGi, or mmWave features.
- No claim that reflective obstacle masks are material interfaces.

## Why The v0.1 Four-Port Mesh Is Insufficient

The v0.1 scalar wave solver uses a parameter-free four-port shunt-node scatter:

```python
total = n + s + e + w
on = 0.5 * total - n
os = 0.5 * total - s
oe = 0.5 * total - e
ow = 0.5 * total - w
```

For a square 2D mesh this fixes the mesh velocity through
`c = dx / (dt * sqrt(2))`. With a single global `dx` and `dt`, that relation gives
one homogeneous mesh speed. A spatial map of wave speed cannot be represented by
changing only the four-port values cell by cell, because the four-port scatter has
no local storage or loading parameter that changes the wave impedance or delay
while preserving a consistent passive connection.

The v0.1 `ObstacleMask` is therefore only reflective geometry. It is not a
heterogeneous wave-speed map.

## Candidate Stub-Loaded Formulation

The candidate v0.2 direction is a stub-loaded 2D shunt-node TLM formulation based
on standard TLM loading ideas in Christopoulos and Johns. In outline, each node
keeps the four spatial link ports plus one or more local stub variables. The stub
stores local energy and changes the effective wave velocity at the node without
changing the global grid spacing or connection topology.

A scalar analogue should be derived carefully from a passive loaded shunt-node
model. The design target is:

- one global timestep `dt`;
- one square grid spacing `dx == dy`;
- a local wave-speed field `c[i, j]`;
- local loading parameter(s) derived from `c[i, j]`, `dx`, and `dt`;
- a scatter matrix that is passive for the allowed parameter range;
- explicit slicing connection between neighbouring link ports, as in v0.1.

The exact scalar stub equations are not yet locked. This document therefore does
not define a production update rule.

Reference status:

- Christopoulos, *The Transmission-Line Modeling Method*.
- Johns, *The Transmission-Line Matrix Method for Numerical Electromagnetic Field
  Computation*.
- A scalar-wave-specific stub-loading reference is needed before implementation.

## Required State Variables

Candidate state for each node:

- link ports: `n`, `s`, `e`, `w`;
- one scalar open- or short-circuit stub amplitude, if a one-stub scalar model is
  sufficient;
- possibly separate capacitive and inductive stubs if the physically correct
  scalar analogue requires both effective compliance and inertia;
- local medium data: `wave_speed[i, j]`;
- derived local loading coefficient(s), stored as arrays on the selected backend.

The state layout should remain structure-of-arrays for NumPy/CuPy compatibility.

## Local Wave Speed, Node Parameters And Timestep

The existing homogeneous mesh has
`c_mesh = dx / (dt * sqrt(2))`. A stub-loaded model should choose a global `dt`
from the fastest supported local wave speed:

```text
dt <= dx / (max(c) * sqrt(2))
```

The local loading parameter should then slow each node from the unloaded mesh
speed to `c[i, j]`. A likely design constraint is:

```text
0 < c[i, j] <= c_mesh
```

where `c_mesh` is set by `dx` and the selected `dt`. If the fastest medium uses
zero loading, slower media use positive loading. The precise relation between
stub admittance/impedance and `c[i, j]` must be derived from the chosen loaded
node formulation before code is written.

## Stability Constraints

Expected constraints:

- square cells for the first implementation;
- positive finite wave speeds;
- local speeds no greater than the unloaded mesh speed implied by `dt`;
- passive non-negative loading coefficients;
- no gain at material interfaces;
- reflective and matched outer boundaries re-evaluated for loaded nodes.

A stability proof or reference is required. A numerical stability sweep is not a
substitute for a passive formulation, but it is still a required regression test.

## Numerical Dispersion Implications

Stub loading will change dispersion. The v0.1 propagation-speed tolerance should
not be reused blindly. v0.2 validation must measure phase or group velocity across:

- wavelength;
- propagation direction;
- wave-speed contrast;
- interface orientation.

The design should expect stronger dispersion near high contrast or under-resolved
interfaces.

## Boundary-Condition Implications

The v0.1 matched boundary is a first-order link termination and is exact only for
normal incidence in the homogeneous mesh. Loaded nodes add local storage near the
domain boundary and may change effective impedance. The boundary design must
answer:

- whether `Gamma=0` remains a meaningful first-order termination for loaded edge
  nodes;
- how reflective boundaries interact with local stub state;
- whether stub energy at boundary-adjacent nodes needs special handling;
- which boundary tests distinguish leakage, reflection, and instability.

PML remains out of scope.

## Proposed Minimal API

This API is a design target only. It should not be added to `tlmpy` until the
formulation and tests are reviewed.

```python
from tlmpy import Grid2D
from tlmpy.core.media import WaveSpeedMap2D
from tlmpy.physics import StubLoadedScalarWaveTLM2D

grid = Grid2D(shape=(256, 256), spacing=(1e-3, 1e-3))
medium = WaveSpeedMap2D.homogeneous(grid, wave_speed=1500.0)
medium.add_circle(center=(0.1, 0.1), radius=0.02, wave_speed=1000.0)

solver = StubLoadedScalarWaveTLM2D(
    grid,
    medium=medium,
    backend="numpy",
    boundary="matched",
)

result = solver.run(steps=500, store_final_field=True)
```

API constraints:

- `WaveSpeedMap2D` validates shape, finite positive speeds, and grid association.
- `StubLoadedScalarWaveTLM2D` computes or validates a global `dt`.
- The homogeneous limit must reproduce v0.1 behavior within a stated tolerance.
- The class must be marked experimental until validation is complete.

## Validation Plan

Required gates before public API:

1. Homogeneous limit matches v0.1 `ScalarWaveTLM2D` for the same wave speed.
2. A quasi-1D interface reflection/transmission case matches an analytical
   coefficient where available.
3. Travel-time through two media matches the expected sum of segment times within
   a dispersion-aware tolerance.
4. Energy/passivity tests show no unphysical growth in closed reflective domains.
5. Stability sweep covers wave-speed contrast, timestep safety factor, and
   interface placement.
6. Regression against an analytical reference or established solver is added if
   feasible.

## Open Questions And References

Open questions:

- Which scalar stub-loaded shunt-node equation is the correct analogue for the
  target scalar wave equation?
- Is one scalar stub sufficient, or are separate storage terms required?
- What is the exact relation between local loading coefficient and wave speed?
- What is the passive parameter range?
- How should source injection be normalized in loaded nodes?
- How should first-order matched boundaries be interpreted for loaded edge nodes?
- Which analytical interface coefficient is appropriate for the scalar quantity
  represented by `0.5 * (n + s + e + w)`?

References:

- `christopoulos1995tlm`
- `johns1987tlm`
- Scalar acoustic or scalar-wave stub-loaded TLM reference needed.
- Interface validation reference needed.

## Do Not Implement Until Resolved

- Do not add `StubLoadedScalarWaveTLM2D` to public imports.
- Do not add `WaveSpeedMap2D` to public imports.
- Do not expose heterogeneous media through `ScalarWaveTLM2D`.
- Do not claim material-interface accuracy from obstacle masks.
- Do not implement PML as part of this work.
- Do not merge an implementation without homogeneous-limit, interface,
  passivity, and stability tests.
