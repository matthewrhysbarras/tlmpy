# Numerical Methods

The scalar wave solver uses the 2D shunt-node scatter relation with four directional ports. The implementation stores the incoming link-line amplitudes in structure-of-arrays form as `n`, `s`, `e`, and `w`, each with shape `(nx, ny)`. Source and probe locations are integer array indices `(i, j)`, where `i` indexes the first grid axis and `j` indexes the second.

For a point source, the temporal signal is evaluated as `signal.value(step * dt)` in seconds and one quarter of that amplitude is added to each of the four ports at the source index. The scalar field used for plotting and probing is `0.5 * (n + s + e + w)`.

The mesh velocity is fixed by `c = dx / (dt * sqrt(2))`, so v0.1 computes `dt` from one homogeneous `wave_speed`. Heterogeneous wave-speed media are intentionally out of scope for v0.1.

The diffusion solver is FTCS with the von Neumann bound `dt <= dx^2 dy^2 / (2 alpha (dx^2 + dy^2))`.

Matched boundaries are first-order link terminations: exact only at normal incidence and leaky at oblique angles. Obstacle masks are approximate reflective geometry masks, not material interfaces or refractive media. Numerical dispersion, full PML, and stub-loaded heterogeneous TLM are roadmap items.

References are listed in `paper/paper.bib`.
