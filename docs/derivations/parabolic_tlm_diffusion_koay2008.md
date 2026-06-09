# Parabolic TLM Diffusion From Koay 2008

This derivation note maps the notation in Koay, Wilkinson and Pulko (2008) to
TLMpy conventions. It supports an experimental implementation only. It is not a
claim of full paper reproduction.

## Index And Port Convention

TLMpy arrays use index `(i, j)`, where `i` is the first array axis and `j` is the
second. The paper uses node `(m, n)`.

The paper's four link ports are mapped as:

- port 1: incident pulse arriving from the `+i` neighbour;
- port 2: incident pulse arriving from the `-i` neighbour;
- port 3: incident pulse arriving from the `+j` neighbour;
- port 4: incident pulse arriving from the `-j` neighbour;
- stub: local incident stub pulse re-entering the same node.

The implementation stores incident pulses as `v1`, `v2`, `v3`, `v4`, `vs` and
reflected pulses as `r1`, `r2`, `r3`, `r4`, `rs`.

## Parabolic Parameterisation

The paper's parabolic parameterisation is:

```text
d = 1 / dl**2
Ys = (specific_heat * density * dl**2) / (thermal_conductivity * dt) - 4
```

The experimental implementation requires:

- `dl > 0`;
- `dt > 0`;
- positive thermal conductivity, specific heat and density;
- square 2D spacing for the first implementation;
- `Ys >= 0`.

For the paper-style Gaussian case with `D = dl**2/(4*dt)`, `Ys = 0` when
`D = thermal_conductivity/(specific_heat*density)`. The literal
`Rs = Zs = 1/(Ys*d)` expression is singular at `Ys = 0`, so the implementation
uses the substituted nodal-potential and scattering equations as the
zero-admittance stub limit. In that benchmark setting, the equal-pulse
parabolic update is expected to match the FTCS reference update and is not an
independent validation of the full estimator paper. The paper's copper-like
material parameters give `Ys > 0`.

## Nodal Potential

Equations 5 and 6 define the nodal potential from incident link and stub pulses.
For the parabolic case, Equation 13 sets:

```text
Rl = Zl = 1/d
Rs = Zs = 1/(Ys*d)
```

Substitution into Equations 5 and 6 for a 2D node with four link ports gives:

```text
T = 2 * (v1 + v2 + v3 + v4 + Ys*vs) / (4 + Ys)
```

where `T` is the nodal potential/temperature represented by the incident pulse
state.

## Scattering

Equation 7 gives each reflected link pulse. With `Rl = Zl`, the second term
vanishes and:

```text
r1 = r2 = r3 = r4 = 0.5 * T
```

Equation 9 gives the parabolic resistance-free stub reflection:

```text
rs = T - vs
```

This scattering map is the experimental passive scalar node used in TLMpy's
`tlmpy.experimental` namespace.

## Connection

Equation 10 connects reflected pulses into next-step incident pulses:

```text
v1[i, j] <- r2[i + 1, j]
v2[i, j] <- r1[i - 1, j]
v3[i, j] <- r4[i, j + 1]
v4[i, j] <- r3[i, j - 1]
vs[i, j] <- rs[i, j]
```

For the first implementation, edges are reflective/insulated:

```text
v1[-1, j] <- r2[-1, j]
v2[0, j] <- r1[0, j]
v3[i, -1] <- r4[i, -1]
v4[i, 0] <- r3[i, 0]
```

This is a closed-domain boundary approximation for the case study, not PML.

## Initial Pulse State

A simple equal-pulse initialization for a target temperature `T0` sets all five
incident arrays to `T0/2`. This exactly represents the target potential at
initial time because:

```text
2 * (4*(T0/2) + Ys*(T0/2)) / (4 + Ys) = T0
```

It is not guaranteed to reconstruct the dynamic pulse history that the Koay
estimator targets.

## Estimator Variables

The paper's estimator compares target potential `y(t)` and estimated potential
`y_hat(t)`, producing error:

```text
e(t) = y(t) - y_hat(t)
```

The paper states that `ld > 2` is required for the reported stable root-locus
region.

Equations 26 to 28 are implemented as a practical feedback hypothesis:

```text
e_next = e + (e - e_previous)
eE_stub = (-e_next + e + (ld - 2)*previous_stub_correction) / ld
eE_link = (e + (ld - 2)*previous_link_correction) / ld
```

The implementation applies `eE_link` equally to all four link incident arrays and
`eE_stub` to the stub incident array before advancing the estimator model.

This is not claimed as a complete reproduction of the paper's estimator because
the paper's full state-space matrices and root-locus construction are not
implemented.

## Open Questions

- Does equal application of `eE_link` to all link ports exactly match the paper's
  intended state correction for every boundary setup?
- Which initial pulse state should be canonical for comparing against Enders'
  first-timestep method?
- What tolerances are appropriate for a paper-quality reproduction of Figures 8
  to 10?
- Should the estimator use a more explicit target sequence before release to
  free diffusion, matching the paper's steady-state and transient variants?
