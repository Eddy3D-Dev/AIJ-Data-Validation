---
title: "Cases H and I (OpenFOAM)"
parent: Validation
nav_order: 6
summary: "OpenFOAM 12 on the 1:1:2 building with a floor source and the cube with a roof source: velocity, k and tracer concentration"
description: "OpenFOAM 12 against the tunnel for Case H (1:1:2 building, floor point source) and Case I (cube, roof point source): velocity, turbulent kinetic energy and tracer concentration, and three turbulence closures on Case I."
---

# Cases H and I, OpenFOAM 12

OpenFOAM 12 runs on the 1:1:2 building with a floor point source (Case H) and on the cube with a roof point source (Case I). Per-run scores and per-point files: [Case H]({{ '/cases/case-h/validation/' | relative_url }}) and [Case I]({{ '/cases/case-i/validation/' | relative_url }}) Validation pages.

## Runs

- Eddy3D production runs, realizable k-ε at numerics level 3 and 3000 iterations, at 1:100 (H) and 1:60 (I), with the probe at the tunnel's own coordinates. Case I was also solved with standard k-ε and with k-ω SST on the same mesh.
- Velocities are divided by $$U_H$$, $$k$$ by $$U_H^2$$. Each side uses its own $$U_H$$: the tunnel's (H 3.226 m/s, I 1.7 m/s) for the measurement, the value the solve was driven with (H 3.23 m/s, I 1.7 m/s) for the model.
- Concentration: the cleaned table's $$C/c_0$$ ($$c_0$$ = 45.18 ppm in H, 39.22 ppm in I) against the model's $$c^\ast = c\thinspace U_H H^2/Q$$, scored at the turbulent Schmidt numbers 0.3, 0.5 and 0.7 (the figures show 0.5). One detection limit, $$10^{-3}$$ of the largest measured value.

## Measurement layout

{% include figure.html name="case-h-layout.png" alt="Measurement lines and planes, Case H" caption="<strong>Figure 1.</strong> Case H, measurement lines and planes: A vertical profiles, $$y/H = 0$$; B plane $$z/H = 0.0625$$; C plane $$z/H = 0.25$$; D plane $$z/H = 0.5$$. Positions in multiples of $$H$$." %}

{% include figure.html name="case-i-layout.png" alt="Measurement lines and planes, Case I" caption="<strong>Figure 2.</strong> Case I, measurement lines and planes: A concentration, vertical profiles, $$y/H = 0$$; B concentration, plane $$z/H = 0$$; C velocity, vertical profiles, $$y/H = 0$$; D velocity, plane $$z/H = 0.5$$. Positions in multiples of $$H$$; panels c and d: $$x/H = -2\text{ to }5$$." %}

## Scores

{% include figure.html name="cases-hi-openfoam-agreement.png" alt="Measured vs modelled, Cases H and I" caption="<strong>Figure 3.</strong> Measured vs modelled $$U$$, $$W$$, $$k$$ and $$c^\ast$$, Cases H (top) and I (bottom), realizable k-ε; the dots take the colour of the line or plane they were measured on, as in Figures 1 and 2. The concentration panels show the positive pairs only." %}

Realizable k-ε, normalised by $$U_H$$.

| Quantity | R | FAC2 | FB | Hit rate |
|---|---|---|---|---|
| H — $$U$$ | +0.897 | 0.609 | +0.355 | 0.446 |
| H — $$V$$ | +0.935 | 0.355 | −0.432 | 0.682 |
| H — $$W$$ | +0.887 | 0.314 | +2.758 | 0.713 |
| H — $$k$$ | +0.107 | 0.570 | +0.514 | 0.305 |
| H — $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.954 | 0.694 | −0.597 | 0.493 |
| H — $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.951 | 0.615 | −0.825 | 0.507 |
| H — $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.946 | 0.588 | −0.934 | 0.493 |
| I — $$U$$ | +0.998 | 0.879 | +0.020 | 0.813 |
| I — $$V$$ | +0.985 | 0.895 | −2.016 | 1.000 |
| I — $$W$$ | +0.972 | 0.659 | −0.049 | 0.967 |
| I — $$k$$ | +0.905 | 0.923 | +0.106 | 0.582 |
| I — $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.922 | 0.360 | +0.398 | 0.106 |
| I — $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.940 | 0.475 | +0.083 | 0.284 |
| I — $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.946 | 0.477 | −0.100 | 0.291 |
{: .scores }

{% include nomenclature-scores.md %}

FB is positive when the model is low.

- **Case H, flow.** R is 0.90, 0.94 and 0.89 for $$U$$, $$V$$ and $$W$$. $$W$$: FB +2.76 on a near-zero mean. $$k$$: R 0.11, FB +0.51.
- **Case H, concentration.** R is 0.95 at every Schmidt number. FB is −0.83 at 0.5, and the modelled $$c^\ast$$ at the measured points peaks at 238 against a measured peak of 66. FB is −0.60, −0.83 and −0.93 for 0.3, 0.5 and 0.7; FAC2 falls from 0.69 to 0.59.
- **Case I, flow.** $$U$$: R 1.00, FAC2 0.88. $$W$$: R 0.97. $$k$$: R 0.91, FAC2 0.92. $$V$$ is scored at the 38 points off the $$y = 0$$ plane; on the plane the workbook holds numerical zeros, which are left out. $$V$$: FB −2.0 on a near-zero mean, R 0.99.
- **Case I, concentration.** R is 0.92 to 0.95 and FAC2 stays below 0.5. FB +0.40 at 0.3, +0.08 at 0.5 and −0.10 at 0.7. Case H has a negative FB (model high) at all three.

<details markdown="block">
<summary>Interpretation: Cases H and I scores</summary>

- Case H: the mean flow is reproduced, $$k$$ is not. FAC2 on $$V$$ and $$W$$ is low by construction, because those components change sign (see [Cases A and B]({{ '/validation/cases-ab/' | relative_url }})); $$W$$'s FB of +2.76 comes from a near-zero mean, so R and the hit rate carry the comparison. The pattern of the tunnel's turbulence at the measured points is not followed ($$k$$ R 0.11).
- Case H: the concentration is well correlated and over-predicted. A higher turbulent Schmidt number raises the modelled concentration further.
- Case I: velocity and $$k$$ agree closely. $$V$$'s FB of −2.0 is the near-zero mean again.
- Case I: the concentration is well correlated, with a wide scatter at low concentration (visible in panel h). The bias changes sign with the Schmidt number: the model is low at 0.3, nearly unbiased at 0.5 and high at 0.7. Case H over-predicts at all three, so the Schmidt number that suits one case does not suit the other.

</details>

## Turbulence closures on Case I

{% include figure.html name="case-i-openfoam-closures.png" alt="Case I under three turbulence closures" caption="<strong>Figure 4.</strong> Case I under standard k-ε, realizable k-ε and k-ω SST on one mesh, dots coloured as in Figure 2: measured vs modelled $$U$$, $$k$$ and $$c^\ast$$ ($$\mathrm{Sc_t}$$ 0.5)." %}

| Closure | $$U$$ R | $$U$$ FAC2 | $$k$$ R | $$k$$ FAC2 | $$k$$ FB | $$c^\ast$$ ($$\mathrm{Sc_t}$$ 0.5) R | $$c^\ast$$ FAC2 | $$c^\ast$$ FB |
|---|---|---|---|---|---|---|---|---|
| standard k-ε | +0.990 | 0.846 | +0.870 | 0.912 | −0.037 | +0.955 | 0.519 | −0.035 |
| realizable k-ε | +0.998 | 0.879 | +0.905 | 0.923 | +0.106 | +0.940 | 0.475 | +0.083 |
| k-ω SST | +0.992 | 0.879 | +0.880 | 0.396 | +0.495 | +0.466 | 0.403 | −0.153 |
{: .scores }

{% include nomenclature-scores.md %}

- $$U$$: R is 0.99 to 1.00 and FAC2 0.85 to 0.88 under all three.
- The two k-ε closures keep $$k$$ within a factor of two at more than 90 % of the points (FAC2 0.912 and 0.923) and give a concentration with R of 0.94 to 0.96. Under k-ω SST, $$k$$ FAC2 is 0.40 (FB +0.49, model low) and the concentration's R is 0.47.
- Mean $$k/U_H^2$$ of the approach profile: 0.0006 under k-ω SST, 0.0075 under both k-ε closures.
- Reattachment length $$L_r/H$$: 2.23 (standard k-ε), 2.51 (realizable k-ε), 2.68 (k-ω SST).

<details markdown="block">
<summary>Interpretation: Case I turbulence closures</summary>

- The mean velocity does not tell the closures apart. $$k$$ and the concentration do.
- Under k-ω SST the turbulence is lower from the inlet on.
- This ranks three closures on one cube, one mesh and this release's numerics.

</details>
