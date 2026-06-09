# Koay 2008 Gaussian TLM Diffusion Case Study

This case study is an experimental path toward understanding the parabolic TLM
diffusion and nodal state-estimator work of Koay, Wilkinson and Pulko (2008).
It is not yet a full reproduction of that paper.

The local reference PDF is used for development reading only and is ignored by
Git. Do not commit the PDF.

## Paper Scope

The paper reviews a two-dimensional resistance-loaded TLM heat-transfer
algorithm, then introduces a nodal state estimator intended to reconstruct pulse
states from prescribed temperature fields. The key distinction for TLMpy is that
temperature is an observed nodal potential, while the TLM state is represented by
link and stub pulses.

## Equations Recorded For Future Work

The paper's heat-transfer TLM review uses four link pulses plus one stub pulse
per 2D node. The nodal potential is computed from incident link and stub pulses
using weighted admittances. Reflected link and stub pulses are then connected to
neighbouring nodes, while the reflected stub pulse is re-incident on the same
node at the next timestep.

For the parabolic parameterisation, the paper gives:

```text
d = 1 / dl**2
Ys = (specific_heat * density * dl**2) / (thermal_conductivity * dt) - 4
```

A valid implementation must require positive material parameters, positive
spacing and timestep, square spacing for the first 2D case, and `Ys >= 0`.

The estimator update described in the paper depends on an estimator parameter
`ld` and requires `ld > 2` for the reported stability region. The estimator also
uses current and predicted error terms. TLMpy does not implement this estimator
yet.

## Stage 1 Benchmark

TLMpy now includes a Stage 1 benchmark:

```bash
python benchmarks/koay2008_gaussian_tlm_diffusion.py
```

This benchmark uses the existing finite-difference diffusion reference solver,
not a parabolic TLM pulse solver. It compares the numerical result against the
Gaussian analytical solution used in the paper's Section 6:

```text
T(x, y, t) = Theta / (4*pi*D*(t0 + t))
             * exp(-((x - x0)**2 + (y - y0)**2) / (4*D*(t0 + t)))
```

The benchmark uses the paper-style parameterisation `D = dx**2 / (4*dt)` for the
analytical Gaussian case and records:

- centre-node transient error;
- relative RMS error at selected timesteps;
- masked maximum relative error;
- a mass-conservation proxy;
- pass/fail status in a `BenchmarkResult` JSON file.

## What Is Not Implemented

This case study does not yet implement:

- parabolic TLM pulse scattering;
- a five-array link-plus-stub pulse state;
- the nodal state estimator;
- steady-state or transient pulse-state initialisation;
- a full reproduction of the 2008 paper;
- heterogeneous wave-speed media, PML, EM, clinical, radar or ultrasound
  capability.

## Required Next Steps

Before implementing `tlmpy.experimental.parabolic_tlm`, the project needs:

- a short derivation note mapping the paper's link/stub notation to TLMpy array
  conventions;
- a passive scattering update checked against Equations 5 to 10;
- validation that the parabolic parameterisation is implemented with `Ys >= 0`;
- a separately tested estimator update using Equations 26 to 28;
- comparison of naive and estimated pulse initialisation against the Gaussian
  analytical benchmark.
