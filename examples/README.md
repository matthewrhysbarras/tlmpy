# Examples

Run examples from the repository root. They create `outputs/` automatically. Plotting examples require `pip install -e ".[viz]"`.

The public example gallery is in [`docs/example_gallery.md`](../docs/example_gallery.md).

Available examples:

- `01_scalar_wave_pulse.py`: homogeneous scalar wave pulse with a matched
  first-order termination;
- `02_scalar_wave_obstacle.py`: approximate reflective obstacle mask;
- `03_thermal_diffusion_slab.py`: finite-difference diffusion reference example;
- `04_gpu_benchmark.py`: optional NumPy/CuPy timing smoke example.

The examples do not demonstrate heterogeneous media, PML, production EM or
external-solver validation.
