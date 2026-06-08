# Codex build prompt for `tlmpy` v0.1

You are Codex acting as a senior scientific-computing, numerical-methods engineer and open-source maintainer.

Build a complete, working v0.1 of an open-source Python package called **TLMpy**.

The Python package name, import name, repository name and CLI command are all lowercase:

```text
Distribution name: tlmpy
Import name:       tlmpy
CLI command:       tlmpy
Display name:      TLMpy
```

TLMpy is a Python-first toolkit for Transmission Line Matrix, TLM, style time-domain simulation of scalar wave problems, plus a finite-difference diffusion reference solver for validation.

Do not merely plan. Create the repo, source, tests, examples, docs skeleton and packaging. Work in the current repository. Initialise from scratch if empty.

Import style:

```python
import tlmpy as tlm
```

Python 3.10+. License BSD-3-Clause. Version 0.1.0.

---

## Non-negotiable correctness rule, read first

In 2D TLM the mesh velocity is fixed by the grid:

```text
c = dx / (dt * sqrt(2))
```

Therefore `dt` is not a free user parameter, and the parameter-free 4-port scattering matrix models only a homogeneous, matched mesh. v0.1 must reflect this honestly:

* The solver takes a single scalar `wave_speed` and computes its own `dt` from `dx` and the `sqrt(2)` mesh condition. It then returns the `dt` it used. Do not accept a free `dt`.
* There is no heterogeneous wave-speed medium in v0.1. That needs stub-loaded nodes, which belongs in the roadmap. Spatial structure is limited to reflective obstacle masks, geometry only.
* Document the fixed-speed and matched-boundary limitations explicitly.

If any instruction below conflicts with physical correctness, prefer correctness and note it.

---

## Scope guards, do not implement in v0.1

No 3D EM, no heterogeneous or stub-loaded TLM, no CAD import, no GUI, no MPI, no PML, no clinical ECGi, no mmWave room-scale simulation, no JAX, no Numba, no Triton backends.

No empty importable stubs. Future modules live in the roadmap doc, not as broken imports.

Do not require CuPy, internet access or external datasets for any core functionality or test.

---

## Repository layout

Create this layout:

```text
tlmpy/
  pyproject.toml
  README.md
  LICENSE
  CITATION.cff
  CONTRIBUTING.md
  CHANGELOG.md
  .gitignore
  paper/
    paper.md
    paper.bib
  .github/
    workflows/
      tests.yml
  src/
    tlmpy/
      __init__.py
      _version.py
      cli.py
      __main__.py
      array_backend.py
      core/
        __init__.py
        grid.py
        sources.py
        probes.py
        results.py
        boundaries.py
        obstacles.py
      physics/
        __init__.py
        scalar_wave_2d.py
        diffusion_2d.py
      validation/
        __init__.py
        analytical.py
        metrics.py
      io/
        __init__.py
        arrays.py
      viz/
        __init__.py
        plots.py
  examples/
    01_scalar_wave_pulse.py
    02_scalar_wave_obstacle.py
    03_thermal_diffusion_slab.py
    04_gpu_benchmark.py
    README.md
  benchmarks/
    benchmark_wave2d.py
  tests/
    test_imports.py
    test_grid.py
    test_backend.py
    test_scalar_wave_2d.py
    test_wave_energy_conservation.py
    test_wave_speed.py
    test_diffusion_2d.py
    test_diffusion_analytical.py
    test_validation_metrics.py
    test_cupy_optional.py
  docs/
    index.md
    getting_started.md
    numerical_methods.md
    validation.md
    roadmap.md
    publication_readiness.md
    ai_usage_disclosure.md
```

---

## Backends, keep it thin

`src/tlmpy/array_backend.py` exposes one main function:

```python
def get_array_module(name: str | None = None):
    """Return the numpy or cupy module. name in {None, "numpy", "cupy"}; None -> numpy.

    Requesting "cupy" when it is not installed raises:
    'CuPy backend requested but CuPy is not installed. Install tlmpy[cuda].'
    """
```

Also provide a small `to_numpy(a)` helper.

Solvers call:

```python
xp = get_array_module(backend)
```

and then use `xp.zeros`, `xp.asarray`, etc.

Do not build a Backend ABC, Protocol or registry. Add that only when a third backend, such as JAX, actually needs unifying.

All public API must import without CuPy present.

---

## Core classes

### `Grid2D`

File: `src/tlmpy/core/grid.py`

`Grid2D` stores:

* `shape=(nx, ny)`
* `spacing=(dx, dy)`

Expose:

* `nx`
* `ny`
* `dx`
* `dy`
* `extent`
* coordinate arrays if useful

Validate:

* shape values are positive integers
* spacing values are positive floats

Raise `ValueError` otherwise.

Example:

```python
from tlmpy import Grid2D

grid = Grid2D(shape=(256, 256), spacing=(1e-3, 1e-3))
```

### Signals and sources

File: `src/tlmpy/core/sources.py`

Keep temporal signals and spatial injection separate.

Implement temporal signals:

* `GaussianPulse`
* `RickerPulse`

Each should be a dataclass with:

```python
value(t: float) -> float
```

where `t` is time in seconds, not step count.

Implement spatial injector:

```python
PointSource2D(location, signal)
```

where `location` is an integer `(i, j)` index. Document the index convention clearly.

The solver evaluates:

```python
signal.value(step * dt)
```

and injects equally into the four ports. Document this clearly.

### Probes

File: `src/tlmpy/core/probes.py`

Implement:

```python
PointProbe2D(name, location)
```

It records the scalar field at its integer index each step into a list or array.

### Results

File: `src/tlmpy/core/results.py`

Implement a `SimulationResult` dataclass:

```python
SimulationResult(
    probes: dict[str, np.ndarray],
    time: np.ndarray,
    dt: float,
    metadata: dict,
    final_field: np.ndarray | None = None,
)
```

Methods:

```python
save_npz(path)
load_npz(path)
```

The round trip must be lossless for result data.

Probe data and final field are always returned as NumPy host arrays, even if the simulation backend is CuPy.

### Boundaries

File: `src/tlmpy/core/boundaries.py`

Implement scalar link-line reflection coefficient `Gamma`.

Boundary options:

* `reflective`, `Gamma=1.0`
* `matched`, `Gamma=0.0`
* optional user-specified coefficient in `[0, 1]`

Name the absorbing option `matched`, not `absorbing`.

Document that this is a first-order termination: exact only at normal incidence, leaky at oblique angles. Real ABC/PML is roadmap.

### Obstacles

File: `src/tlmpy/core/obstacles.py`

Implement:

```python
ObstacleMask(grid)
```

with:

```python
add_circle(center, radius)
```

It produces a boolean mask of cells treated as reflective geometry.

This replaces a heterogeneous material map in v0.1.

Do not expose a spatial or material `wave_speed` map. Do not implement heterogeneous wave-speed media. Do not add `wave_speed` to `ObstacleMask` or any material-like class.

The homogeneous solver-level parameter is allowed and required:

```python
ScalarWaveTLM2D(grid, wave_speed=1500.0)
```

`solver.wave_speed` is also allowed and required.

---

## Physics 1: `ScalarWaveTLM2D`

File: `src/tlmpy/physics/scalar_wave_2d.py`

Implement a 2D scalar TLM-style solver using four float64 port fields:

```python
n, s, e, w
```

Each has shape `(nx, ny)`.

Use structure-of-arrays layout.

### Scatter

Use the standard 2D shunt-node scatter:

```python
total = n + s + e + w
on = 0.5 * total - n
os = 0.5 * total - s
oe = 0.5 * total - e
ow = 0.5 * total - w
```

### Connect

Connect via explicit slicing, preferred. Do not use `xp.roll` unless all wrapped boundaries are overwritten immediately and tested.

`xp.roll` imposes periodic wraparound, a torus, by default. Accidental periodic domains are not caught by energy conservation, because a periodic lossless mesh also conserves energy.

Out-of-domain links are handled only by the boundary reflection coefficient `Gamma`.

Apply obstacle masks as reflective geometry.

The field used for plotting and probing is:

```python
field = 0.5 * (n + s + e + w)
```

### Construction and run

Public API:

```python
from tlmpy import Grid2D
from tlmpy.physics import ScalarWaveTLM2D
from tlmpy.core.sources import RickerPulse, PointSource2D
from tlmpy.core.probes import PointProbe2D

grid = Grid2D(shape=(256, 256), spacing=(1e-3, 1e-3))

solver = ScalarWaveTLM2D(
    grid,
    wave_speed=1500.0,
    backend="numpy",
    boundary="matched",
    obstacles=None,
)

solver.add_source(
    PointSource2D(
        location=(128, 128),
        signal=RickerPulse(frequency=1000.0),
    )
)

solver.add_probe(PointProbe2D(name="centre", location=(128, 128)))

result = solver.run(steps=500, store_final_field=True)

assert result.dt == solver.dt
```

Important: `run()` does not accept `dt`.

`dt` is derived internally:

```python
dt = dx / (wave_speed * sqrt(2))
```

Require `dx == dy`. Raise `ValueError` for anisotropic spacing. Anisotropic mesh support is roadmap.

Requirements:

* validate grid and shapes
* require `wave_speed > 0`
* require `dx == dy`
* no Python loop over cells
* Python loop over timesteps is acceptable
* keep all field arrays on the selected backend during simulation
* use float64 throughout
* transfer only probes and final field to host
* expose `solver.wave_speed` and `solver.dt` as public read-only attributes
* compute `dt` from the single expression `dx / (wave_speed * sqrt(2))`

---

## Physics 2: `Diffusion2D`

File: `src/tlmpy/physics/diffusion_2d.py`

Implement an honest FTCS reference solver. Do not claim it is TLM in v0.1.

Equation:

```text
du/dt = alpha * laplacian(u)
```

Update:

```python
u_next = u + dt * alpha * laplacian(u)
```

Because `dt` is passed to `run()`, the stability check must happen inside `run()`, not at construction:

```python
stable_dt = dx**2 * dy**2 / (2 * diffusivity * (dx**2 + dy**2))
if dt > stable_dt:
    raise ValueError(...)
```

Mention the von Neumann stability result in the message or docstring.

The constructor validates:

* diffusivity
* boundary type
* backend
* grid

It cannot validate timestep stability until `run(dt=...)`.

Note in the docstring that `dt == stable_dt` is only marginally stable. The highest mode has amplification factor `-1`, giving a non-decaying checkerboard. Recommend a safety margin such as:

```python
dt <= 0.9 * stable_dt
```

Support:

* homogeneous `alpha`
* user initial condition array
* `dirichlet` fixed-value boundary
* `neumann` insulated conservative zero-flux boundary

### Neumann implementation

Implement `neumann` as a conservative zero-flux boundary.

Use edge-replicated padding for the Laplacian:

```python
u_pad = xp.pad(u, 1, mode="edge")
```

or an equivalent finite-volume form where only interior neighbour fluxes contribute at boundary cells.

Do not use:

```python
mode="reflect"
```

`mode="reflect"` reflects about the cell centre and can impose a nonzero gradient at the boundary face, leaking flux and breaking discrete mass conservation.

Under `boundary="neumann"`, the discrete sum of `u` must be conserved to approximately `1e-12` relative for float64 tests.

Add a dedicated test that fails if a non-conservative mirror convention is used.

Example API:

```python
from tlmpy.physics import Diffusion2D

solver = Diffusion2D(
    grid,
    diffusivity=1e-5,
    backend="numpy",
    boundary="neumann",
)

solver.set_initial_condition(u0)

result = solver.run(
    steps=1000,
    dt=stable_dt,
    store_final_field=True,
)
```

---

## Validation

### `validation/analytical.py`

Implement:

```python
gaussian_diffusion_2d(grid, alpha, sigma0, t, center=None, mass=1.0)
```

This returns the closed-form heat-kernel spreading of a 2D Gaussian.

Variance per axis:

```text
sigma(t)^2 = sigma0^2 + 2 * alpha * t
```

Amplitude is scaled to conserve `mass`.

`center` defaults to the grid centre.

The returned field must use the same normalisation convention as the initial condition used in the analytical diffusion test, so mass comparisons are meaningful.

Also implement:

```python
estimate_wave_speed_from_probes(p1, p2, distance, dt)
```

This estimates time-of-flight wave speed.

### `validation/metrics.py`

Implement:

```python
relative_l2_error(a, b)
max_abs_error(a, b)
assert_close_relative(a, b, tol)
```

---

## Tests

All tests must pass in CI without CuPy.

### Imports

Test:

```python
import tlmpy
from tlmpy import Grid2D
from tlmpy.physics import ScalarWaveTLM2D, Diffusion2D
```

### Grid

Test:

* valid grid builds
* invalid shape raises
* invalid spacing raises

### Backend

Test:

* NumPy backend works
* `get_array_module("cupy")` without CuPy raises the clear message:

```text
CuPy backend requested but CuPy is not installed. Install tlmpy[cuda].
```

### Wave smoke tests

Test:

* solver initialises
* one step runs
* impulse stays finite
* no NaNs
* reflective and matched boundaries both run
* source and probe populate `result.probes`

### Wave energy conservation

With reflective walls and no source, initialise random port fields. Total energy:

```python
sum(n**2 + s**2 + e**2 + w**2)
```

must be conserved to approximately `1e-12` over many steps.

The scattering matrix is orthogonal and connection is a permutation.

Important: compute energy from all four port arrays, not from the plotted scalar field.

### Exact `dt`

Test:

```python
math.isclose(
    solver.dt,
    grid.dx / (solver.wave_speed * sqrt(2)),
    rel_tol=1e-12,
)
```

Use `isclose`, not `==`, to avoid ULP fragility.

### Boundary is not periodic

Record probes near the source-side edge and near the opposite edge.

Inject a pulse near one edge.

Assert it does not appear at the opposite-edge probe at the timestep where a periodic `roll` implementation would create wraparound.

Under `reflective`, it returns toward the source side.

Under `matched`, it does not reappear.

This test is essential because the energy test cannot catch an accidental torus.

### Wave speed

Use a low-frequency, long-wavelength pulse. Place probes far from boundaries.

Estimate arrival by cross-correlation or thresholded envelope peak.

Compare measured speed to theoretical mesh speed:

```text
dx / (dt * sqrt(2))
```

Start with less than 10 percent tolerance.

Document that tightening the tolerance requires dispersion characterisation in v0.2.

### Diffusion

Test:

* stable `dt` accepted
* unstable `dt` raises
* impulse smooths
* Neumann mass conserved to approximately `1e-12`
* Dirichlet behaves sensibly
* no NaNs

### Diffusion analytical

Build the initial condition using the same normalisation convention as `gaussian_diffusion_2d`.

Evolve a modest number of steps.

Assert the result matches `gaussian_diffusion_2d` in relative L2 below a stated tolerance.

The analytical reference is an infinite-domain solution approximated on a large finite domain, so the test must use:

* a large domain
* a centred Gaussian
* final time small enough that the Gaussian remains negligible at the boundaries
* Neumann or sufficiently distant boundaries

State this limitation in the test docstring.

### Metrics

Test:

* L2 error is zero for identical arrays
* max error is zero for identical arrays
* metrics scale correctly

### CuPy optional

Use:

```python
@pytest.mark.skipif(cupy_missing, reason="CuPy not installed")
```

Run identical float64 wave simulations on NumPy and CuPy.

Assert relative L2 error is less than `1e-12`.

---

## Examples

Examples must auto-create an `outputs/` directory.

### `examples/01_scalar_wave_pulse.py`

Free-space Ricker pulse.

Save:

```text
outputs/scalar_wave_pulse.png
outputs/scalar_wave_pulse.npz
```

### `examples/02_scalar_wave_obstacle.py`

Add a reflective circular `ObstacleMask`.

Show scattering.

Save:

```text
outputs/scalar_wave_obstacle.png
```

Docstring must state this is geometric reflection, not a refractive medium.

### `examples/03_thermal_diffusion_slab.py`

Transient diffusion from a hot region.

Save:

```text
outputs/thermal_diffusion_slab.png
```

### `examples/04_gpu_benchmark.py`

Time NumPy versus CuPy if CuPy is available.

Print:

* backend
* grid size
* steps
* elapsed time

If CuPy is unavailable, print a clear skip message.

---

## Visualisation

File: `src/tlmpy/viz/plots.py`

Implement:

```python
plot_field(field, title=None, save_path=None)
plot_probe(time, values, title=None, save_path=None)
```

Both return:

```python
(fig, ax)
```

Use matplotlib.

Import matplotlib lazily inside the functions.

No seaborn.

Do not hardcode colours.

Examples that save PNGs require the optional `viz` extra. If matplotlib is missing, examples must fail with this clear message:

```text
This example requires matplotlib. Install with: pip install -e ".[viz]"
```

Do not make matplotlib a core dependency.

---

## CLI

Files:

```text
src/tlmpy/cli.py
src/tlmpy/__main__.py
```

`cli.py` defines:

```python
main()
```

`__main__.py` delegates to it:

```python
from tlmpy.cli import main

raise SystemExit(main())
```

These must work:

```bash
python -m tlmpy --version
python -m tlmpy info
tlmpy info
```

`info` prints:

* version
* available backends
* whether CuPy is importable

---

## Packaging

Use `pyproject.toml`.

Build backend: hatchling.

Use `src` layout.

Core dependencies:

```text
numpy
```

Optional extras:

```text
viz = [matplotlib]
cuda = [cupy]
dev = [pytest, pytest-cov, ruff, build, twine]
docs = [mkdocs, mkdocs-material]
```

Drop mypy from v0.1.

Expose console script:

```toml
[project.scripts]
tlmpy = "tlmpy.cli:main"
```

Configure ruff with line length 100.

---

## CI

Create:

```text
.github/workflows/tests.yml
```

Run on push and pull request.

Test Python:

* 3.10
* 3.11
* 3.12

Install:

```bash
python -m pip install -e ".[dev]"
```

Run:

```bash
ruff check .
pytest
```

Never install CuPy in CI.

Do not run PNG-generating examples in CI unless matplotlib is installed.

Core package must install with NumPy alone.

---

## README

Write a strong README with:

1. Project title: TLMpy
2. One-line description
3. v0.1 experimental banner
4. Installation:

```bash
pip install -e ".[dev]"
pip install -e ".[dev,viz]"
pip install -e ".[cuda,dev,viz]"
```

5. Quick-start scalar wave example
6. Quick-start diffusion example
7. Backend note
8. Explicit limitations:

   * fixed mesh speed
   * matched boundary is first-order
   * obstacles are reflective only
   * no heterogeneous media in v0.1
   * no PML in v0.1
9. Validation philosophy
10. Roadmap
11. Citation
12. License

---

## Docs, paper and JOSS readiness

### `docs/index.md`

Overview and project goals.

### `docs/getting_started.md`

Install and run first examples.

### `docs/numerical_methods.md`

Explain:

* 2D shunt-node scatter
* `sqrt(2)` mesh-velocity relation
* FTCS stability bound
* numerical dispersion
* matched-boundary limitation

Include citations.

### `docs/validation.md`

List validation tests and tolerances:

* energy conservation
* exact dt
* boundary not periodic
* mesh-speed regression
* analytical Gaussian diffusion
* Neumann mass conservation

### `docs/roadmap.md`

Record v0.2 scholarly differentiator options.

Preferred order:

1. stub-loaded heterogeneous 2D TLM with spatially varying wave speed
2. quantified dispersion and boundary-characterisation toolkit for 2D TLM
3. reproducible synthetic sensing demo, such as acoustic scattering or radar-style multipath, without overclaiming physical realism

### `docs/publication_readiness.md`

State plainly that TLMpy is not JOSS-ready at v0.1.

Include these reasons:

1. The repo must be public for more than six months with iterative development.
2. Demonstrated research use is required. Aspirational future-use statements are insufficient.
3. A scalar demonstrator plus FTCS reference is at risk of being read as educational or reinvention next to tools such as Meep and `fdtd`.
4. The path is to release v0.1 publicly, develop iteratively in the open, reach the v0.2 scholarly differentiator, accumulate real use, then submit.

### `docs/ai_usage_disclosure.md`

Create a placeholder AI usage disclosure stating:

* which tools and models were used
* where they were used, code, tests, docs, paper
* the nature and scope of assistance
* human authors reviewed, tested and validated all AI-assisted outputs
* human authors made the core design decisions

Mirror a short version in `paper/paper.md`.

### `paper/paper.md`

Create a valid JOSS-style draft, not just prose.

Begin with YAML front matter placeholders:

```yaml
---
title:
tags:
authors:
affiliations:
date:
bibliography: paper.bib
---
```

Then include:

* Summary
* Statement of Need
* AI usage disclosure placeholder
* References

Position TLMpy against existing tools:

* Meep
* the `fdtd` Python package
* established TLM codes

Emphasise what TLM offers that generic FD/FDTD does not.

Frame the diffusion solver as an internal validation reference only, not a headline capability.

Authors, ORCID and affiliation fields are placeholders.

Mark the paper explicitly as:

```text
Draft, not submission-ready at v0.1.
```

### `paper/paper.bib`

Include placeholder references for:

* Christopoulos, The Transmission-Line Modeling Method
* LeVeque, Finite Difference Methods for Ordinary and Partial Differential Equations
* Meep
* Python `fdtd` package
* relevant TLM references

### `CITATION.cff`

Create placeholder citation metadata:

* title: TLMpy
* version: 0.1.0
* license: BSD-3-Clause
* authors: placeholders
* message asking users to cite TLMpy

---

## v0.2 scholarly differentiator, define now but do not implement in v0.1

v0.1 is intentionally modest. The route to JOSS plausibility is one rigorously validated TLM capability not trivially available in generic finite-difference teaching codes.

Preferred, in order:

1. Stub-loaded heterogeneous 2D TLM with spatially varying wave speed.
2. Quantified dispersion and boundary-characterisation toolkit for 2D TLM.
3. Reproducible synthetic sensing demo, such as acoustic scattering or radar-style multipath, built on the validated solver without overclaiming physical realism.

Record this in `docs/roadmap.md`.

---

## Acceptance criteria

These must work locally:

```bash
python -m pip install -e ".[dev,viz]"
python -m tlmpy --version
python -m tlmpy info
tlmpy info
pytest
python examples/01_scalar_wave_pulse.py
python examples/03_thermal_diffusion_slab.py
python examples/04_gpu_benchmark.py
```

The examples should create an `outputs/` directory automatically.

---

## Process

1. Inspect the repository.
2. Build incrementally.
3. Run tests.
4. Fix failures.
5. Run examples.
6. Fix failures.
7. Finish with a summary.

The final summary must include:

* files created
* commands run
* test results
* known limitations
* recommended next GitHub issues

Top recommended GitHub issues should include:

1. Stub-loaded heterogeneous nodes.
2. Proper PML.
3. Dispersion characterisation.
4. Benchmark against an established solver to substantiate validation.
5. Better boundary-condition analysis.
6. Public example gallery.
7. v0.2 publication-readiness checklist.

