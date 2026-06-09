# Roadmap

1. Stub-loaded heterogeneous 2D TLM with spatially varying wave speed.
2. Quantified dispersion and boundary-characterisation toolkit for 2D TLM.
3. Reproducible synthetic sensing demo, such as acoustic scattering or radar-style multipath, without overclaiming physical realism.
4. Experimental parabolic TLM diffusion case-study path, starting from an
   analytical Gaussian benchmark before any pulse-state estimator implementation.

## v0.2 Stub-Loaded TLM Sprint

The first v0.2 research sprint is design-first. The target is a minimal,
validated stub-loaded 2D scalar TLM formulation for spatially varying wave speed.
The design note is `docs/design/stub_loaded_2d_tlm.md`.

Implementation should remain experimental until the formulation is reviewed and
the following gates exist:

- homogeneous limit against the v0.1 solver;
- quasi-1D interface reflection/transmission validation;
- travel-time through two media;
- energy/passivity checks;
- stability sweep over wave-speed contrast;
- comparison with an analytical reference or established solver where feasible.
- literature-backed derivation and validation before exposing experimental
  parabolic TLM diffusion beyond case-study status.

PML, anisotropic meshes, CAD import, GUI, MPI, and accelerated backends beyond optional CuPy are future work.
