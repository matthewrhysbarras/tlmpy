# Numerical Methods

The scalar wave solver uses the 2D shunt-node scatter relation with four ports. The mesh velocity is fixed by `c = dx / (dt * sqrt(2))`, so v0.1 computes `dt` from one homogeneous `wave_speed`.

The diffusion solver is FTCS with the von Neumann bound `dt <= dx^2 dy^2 / (2 alpha (dx^2 + dy^2))`.

Matched boundaries are first-order link terminations: exact only at normal incidence and leaky at oblique angles. Numerical dispersion and full PML are roadmap items.

References are listed in `paper/paper.bib`.

