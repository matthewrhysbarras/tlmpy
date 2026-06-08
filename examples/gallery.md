# Example Gallery

The maintained example gallery is documented in
[`docs/example_gallery.md`](../docs/example_gallery.md).

Run examples from the repository root:

```bash
python examples/01_scalar_wave_pulse.py
python examples/02_scalar_wave_obstacle.py
python examples/03_thermal_diffusion_slab.py
python examples/04_gpu_benchmark.py
```

These examples cover current v0.1 homogeneous scalar wave behavior, approximate
reflective obstacle masks, the finite-difference diffusion reference solver and
optional backend timing. They do not demonstrate heterogeneous media, PML or
external-solver validation.
