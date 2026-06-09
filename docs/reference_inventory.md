# TLM Reference Inventory

This page records the current reference backlog for future TLMpy research work.
It is a reading list and planning aid, not a claim that v0.1.1 implements the
methods below.

## Foundation References

These references are suitable starting points for the project bibliography and
for future documentation of the TLM method:

- Johns and Beurle, 1971, `@johns_beurle_1971_tlm_scattering`: early 2D
  transmission-line matrix scattering paper. Use this as a foundation reference
  for the historical 2D TLM mesh, not as a direct validation of TLMpy's scalar
  demonstrator.
- Johns, 1987, `@johns1987tlm`: symmetrical condensed node reference already
  listed in the draft bibliography. This is an electromagnetic node reference,
  not a scalar API specification for TLMpy.
- Christopoulos, 1995, `@christopoulos1995tlm`: book-length TLM reference
  already listed in the draft bibliography. Use it for broad TLM background and
  stub-loading concepts.

## Stub-Loaded Heterogeneous TLM References

These references are relevant to future heterogeneous or loaded-node work:

- Christopoulos, 1995, `@christopoulos1995tlm`: broad treatment of TLM,
  including loaded/stub concepts.
- Morente, Gimenez, Porti and Khalladi, 1995,
  `@morente1995dispersion_stubs`: dispersion analysis for a TLM mesh of
  symmetrical condensed nodes with stubs. This is directly relevant to any
  future stub-loaded formulation because it treats loaded nodes and dispersion,
  but it is still electromagnetic SCN work rather than a finished scalar TLMpy
  formulation.
- A scalar-wave-specific stub-loading reference is still needed before public
  implementation. Until then, `docs/design/stub_loaded_2d_tlm.md` should remain
  a design note and not an implementation specification.

## Analytical Dispersion References

Current dispersion benchmarks in TLMpy are empirical group-speed regressions.
They do not prove agreement with an analytical TLM dispersion relation. Candidate
analytical references to study before tightening claims or tolerances:

- Morente et al., 1995, `@morente1995dispersion_stubs`: reports analytical
  phase/group velocity expressions for a stub-loaded symmetrical condensed-node
  mesh.
- Nielsen and Hoefer, 1991, "A complete dispersion analysis of the condensed
  node TLM mesh": candidate reference for condensed-node analytical dispersion.
  Full bibliographic details and applicability to TLMpy's scalar four-port mesh
  still need verification before citation in the paper.
- Choi, 1989, "Comparison of the dispersion characteristics associated with the
  TLM and FD-TD methods": candidate comparative dispersion reference. Full
  bibliographic details and relevance to the scalar model still need
  verification.

## Published Benchmark-Case Candidates

These are candidates for future reference-comparison issues. They should not be
implemented until the modeled equation, boundary conditions and tolerances are
matched carefully.

- Homogeneous travel-time and mesh-speed checks: already covered internally by
  `benchmarks/analytical_travel_time.py`; suitable as a baseline but not an
  external validation case.
- Johns and Beurle, 1971 2D scattering: possible historical comparison target,
  but the source, boundary and field quantities must be mapped carefully before
  using it as a benchmark.
- "Transmission-line matrix acoustic modelling on a PC", Applied Acoustics,
  1997: candidate acoustic TLM reference with analytically solvable cases. Full
  author metadata and the exact analytical cases should be verified from the
  paper before use.
- "An improved transmission line matrix model for the 2D ideal wedge benchmark
  problem", Journal of Sound and Vibration, 2008, DOI
  `10.1016/j.jsv.2007.10.009`: candidate acoustic boundary benchmark based on
  an ideal wedge problem. This is not appropriate for immediate TLMpy comparison
  until boundary-condition and geometry support are closer to the published
  setup.

## Do Not Claim Yet

Do not claim:

- TLMpy implements stub-loaded heterogeneous media;
- TLMpy has an analytical dispersion match;
- TLMpy is validated against published TLM benchmark cases;
- TLMpy's first-order matched termination is PML;
- obstacle masks are material interfaces.

## Follow-Up Work

- Derive or adopt a passive scalar stub-loaded node equation from a checked
  reference.
- Decide whether the scalar four-port demonstrator has a direct analytical
  dispersion relation worth documenting, or whether comparison should remain
  empirical.
- Convert one published benchmark candidate into a precise implementation issue
  only after the equation, source, boundary and tolerance are unambiguous.
