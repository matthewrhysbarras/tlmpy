# Example Gallery

This page lists the current TLMpy examples and the commands used to regenerate
their local outputs. These examples demonstrate existing v0.1 homogeneous scalar
wave behavior, approximate reflective obstacle masks, diffusion reference
support and optional backend timing. They do not demonstrate heterogeneous media,
PML, production electromagnetics or external-solver validation.

Run examples from the repository root. Plotting examples require the optional
visualisation dependencies:

```bash
pip install -e ".[dev,viz]"
```

Generated files are written under `outputs/`. They are local artifacts and are
not required for normal package use.

## Scalar Wave Pulse

```bash
python examples/01_scalar_wave_pulse.py
```

This example launches a Ricker pulse in a homogeneous 2D scalar TLM-style mesh
with a first-order matched termination. It writes:

- `outputs/scalar_wave_pulse.npz`;
- `outputs/scalar_wave_pulse.png`.

What it demonstrates:

- source injection into the four directional ports;
- probe/result saving through `SimulationResult`;
- plotting the final scalar field.

Limitations:

- homogeneous mesh speed only;
- matched boundary is not PML;
- no external reference comparison.

## Reflective Obstacle Mask

```bash
python examples/02_scalar_wave_obstacle.py
```

This example uses a circular obstacle mask in the existing homogeneous scalar
wave solver and writes `outputs/scalar_wave_obstacle.png`.

What it demonstrates:

- a geometric reflective mask inside the computational domain;
- qualitative scattering behavior for the final scalar field.

Limitations:

- obstacle masks are approximate reflective geometry;
- the mask is not a refractive material interface;
- this is not a heterogeneous wave-speed example.

## Thermal Diffusion Reference

```bash
python examples/03_thermal_diffusion_slab.py
```

This example runs the finite-difference diffusion reference solver from a hot
square initial condition and writes `outputs/thermal_diffusion_slab.png`.

What it demonstrates:

- explicit FTCS diffusion with Neumann boundary handling;
- plotting the final scalar field;
- a validation-support solver separate from the TLM wave solver.

Limitations:

- this is not a TLM diffusion solver;
- timestep choice follows the finite-difference stability limit;
- it is included as a reference/validation support example.

## Optional GPU Timing

```bash
python examples/04_gpu_benchmark.py
```

This example times a small homogeneous scalar-wave run on NumPy and, if CuPy is
installed, CuPy. It prints a clean skip message when CuPy is unavailable.

What it demonstrates:

- optional backend selection;
- a smoke-level timing comparison.

Limitations:

- this is not a rigorous performance benchmark;
- CuPy is optional and not installed by default;
- results depend on hardware, drivers and array-library versions.

## Related Benchmarks

Benchmarks with machine-readable JSON summaries live under `benchmarks/`.

```bash
python benchmarks/analytical_travel_time.py
python benchmarks/boundary_reflection.py
```

See [Benchmarking](benchmarking.md) for details.
