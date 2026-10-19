**OpenFOAM 12.** The tracer release over the Atsugi campus of Tokyo Polytechnic University: ethylene in a 1:600 tunnel, with 18 field runs. An Eddy3D production run solved on 2026-10-18, realizable k-ε at numerics level 3, **one steady solve** on one mesh for the tunnel's heading WD 180 only (1,394,053 cells, 3000 iterations). It stopped at the iteration limit with the SIMPLE residual control unmet; the initial residual of epsilon at the last iteration was $$1.9 \times 10^{-2}$$.

- Scored at WD 180 against the wind-tunnel run: $$U$$, $$V$$, $$W$$ and $$k$$ over the tunnel's $$U_R$$ = 4.08 m/s on the measurement and over the **solved** speed at the reference mast (4.686 m/s) on the model, because $$U_R$$ is defined at the mast.
- The concentration is the measured $$C/c_0$$ ($$c_0$$ = 132.5 ppm) against the model's $$c^\ast = c\thinspace U_R H_R^2/Q$$ with the same solved $$U_R$$, for the turbulent Schmidt numbers 0.3, 0.5 and 0.7: three passive tracers on one flow, **three runs** (`configuration` sct03, sct05, sct07); the flow scores are the same in all three. One detection limit, $$10^{-3}$$ of the largest measured value.

<details markdown="block">
<summary>Data notes: Scores here and Eddy3D's own</summary>

- The velocities and the concentration lose the CSV's rounding (to 0.01 m/s and 0.1 ppm). $$U$$ R is 0.7085 here and 0.7081 there, $$k$$ R 0.4464 and 0.4499, and $$W$$, whose values are of the order of the rounding, R 0.1814 and 0.1757 (FAC2 0.27 and 0.20). The field values divide by $$H_R$$ = 41 m as the cleaned table states, Eddy3D's by 40.8 m (a 1 % difference in every field $$c^\ast$$).
- Eddy3D's scores of $$V$$ and $$W$$ have a fractional bias (−6.15 and +2.15) that this repository leaves undefined for a signed component whose means are not both positive.

</details>

## Measurement layout

{% include figure.html name="case-m-layout.png" alt="Measurement points, Case M" caption="<strong>Figure 1.</strong> Case M, measurement points: A near field, within 100 m of the release point; B mid field, 100 to 300 m from the release point; C far field, beyond 300 m. Positions in metres, full scale. Star: release point; R: reference point; dotted circles: 100 m and 300 m from the release point." %}

## OpenFOAM 12: measured against modelled

{% include figure.html name="case-m-openfoam-agreement.png" alt="Case M, measured vs modelled velocity, k and concentration" caption="<strong>Figure 2.</strong> Case M, WD 180: measured vs modelled $$U$$, $$V$$, $$W$$, $$k$$ and $$c^\ast$$ at three turbulent Schmidt numbers (log axes show the positive pairs within eight decades). The last panel is the tunnel's own WD 175 and WD 185 against its WD 180. The dots take the colour of their group in Figure 1." %}

| Quantity | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.412 | 0.200 | +1.396 | 0.133 | 15 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.251 | 0.200 | +1.524 | 0.133 | 15 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.198 | 0.133 | +1.579 | 0.133 | 15 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, points turned 180° about the source (control) | −0.050 | 0.071 | +2.000 | 0.071 | 14 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, points turned 180° about the source (control) | −0.058 | 0.071 | +2.000 | 0.071 | 14 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, points turned 180° about the source (control) | −0.058 | 0.071 | +2.000 | 0.071 | 14 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, points mirrored across the plume axis (control) | +0.675 | 0.467 | +0.321 | 0.133 | 15 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, points mirrored across the plume axis (control) | +0.655 | 0.400 | +0.220 | 0.333 | 15 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, points mirrored across the plume axis (control) | +0.650 | 0.400 | +0.180 | 0.333 | 15 |
| $$c^\ast$$, tunnel WD 175 as a model of WD 180 (control) | +0.932 | 0.733 | +0.401 | 0.267 | 15 |
| $$c^\ast$$, tunnel WD 185 as a model of WD 180 (control) | +0.976 | 0.800 | −0.117 | 0.533 | 15 |
| $$c^\ast$$, mean of WD 175 and WD 185 as a model of WD 180 (control) | +0.998 | 1.000 | +0.111 | 0.867 | 15 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, against the field's geometric mean | +0.464 | 0.067 | +1.012 | 0.000 | 15 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, against the field's geometric mean | +0.285 | 0.067 | +1.202 | 0.000 | 15 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, against the field's geometric mean | +0.224 | 0.067 | +1.287 | 0.000 | 15 |
| $$c^\ast$$, tunnel WD 180 as a model of the field's geometric mean (control) | +0.984 | 0.600 | −0.593 | 0.000 | 15 |
| $$U$$ | +0.708 | 0.267 | +1.460 | 0.267 | 15 |
| $$V$$ | +0.731 | 0.333 | — | 0.133 | 15 |
| $$V$$, sign flipped (control) | −0.731 | 0.067 | −0.616 | 0.133 | 15 |
| $$W$$ | +0.181 | 0.267 | — | 0.733 | 15 |
| $$\lvert\mathbf{U}\rvert$$ | +0.601 | 0.733 | +0.185 | 0.400 | 15 |
| $$k$$ | +0.446 | 0.133 | +1.131 | 0.067 | 15 |
{: .scores }

{% include nomenclature-scores.md %}

FB is positive when the model is low, and left out (—) for a signed component whose measured and modelled means are not both positive.

The concentration across the three Schmidt numbers:

| Run | $$c^\ast$$ over the imposed speed at the mast: FB | over 4.08 m/s: FB | mean $$c^\ast$$ tunnel | mean $$c^\ast$$ model | peak tunnel | peak model | top five shared | near three, tunnel | model | far two, tunnel | model |
|---|---|---|---|---|---|---|---|---|---|---|---|
| $$\mathrm{Sc_t}$$ 0.3 | +1.480 | +1.464 | 0.998 | 0.177 | 3.04 | 1.27 | 3 of 5 | 2.52 | 0.26 | 0.21 | 0.11 |
| $$\mathrm{Sc_t}$$ 0.5 | +1.592 | +1.579 | 0.998 | 0.135 | 3.04 | 1.37 | 3 of 5 | 2.52 | 0.11 | 0.21 | 0.10 |
| $$\mathrm{Sc_t}$$ 0.7 | +1.640 | +1.628 | 0.998 | 0.117 | 3.04 | 1.38 | 3 of 5 | 2.52 | 0.05 | 0.21 | 0.09 |

{% include nomenclature-scores.md %}

- **Tracer.** R is 0.41, 0.25 and 0.20 and FAC2 0.20, 0.20 and 0.13 from $$\mathrm{Sc_t}$$ 0.3 to 0.7; the mean $$c^\ast$$ is 0.18, 0.13 and 0.12 against the tunnel's 1.00 (FB +1.40 to +1.58), the peak 1.27 to 1.38 against 3.04, and three of the five highest points are shared. Over the imposed speed at the mast's height (3.934 m/s) FB is +1.48 and over the tunnel's 4.08 m/s +1.46 at $$\mathrm{Sc_t}$$ 0.3 (the solved speed at the mast is 4.686 m/s, 1.19 of the imposed one).
- **Near and far points.** The three points nearest the source carry $$c^\ast$$ 2.52 in the tunnel and 0.26, 0.11 and 0.05 in the model; the two far downwind ones 0.21 in the tunnel and 0.11, 0.10 and 0.09 in the model. The tunnel's near points exceed its far ones by a factor of about twelve; the model's by 2.3 and 1.1 at $$\mathrm{Sc_t}$$ 0.3 and 0.5, and at $$\mathrm{Sc_t}$$ 0.7 they carry *less* (0.055 against 0.087).
- **Controls on the plume.** The points turned 180° about the source (14 of the 15 lie in the fluid) score R −0.05 to −0.06 (the model's mean over them is $$7 \times 10^{-6}$$ against 0.19 at the real points, $$\mathrm{Sc_t}$$ 0.3). The points mirrored across the plume axis score R +0.65 to +0.68, FAC2 0.40 to 0.47, against R +0.20 to +0.41 at the real points.
- **Neighbouring headings.** The tunnel's own WD 175 and WD 185 scored as models of its WD 180 reach FAC2 0.73 and 0.80 (R 0.93 and 0.98), and the mean of the two 1.00 (R 0.998). 8 of the 15 points change by more than a factor of two between WD 175 and WD 185 (up to 11 at point 14). The model's FAC2 is 0.13 to 0.20.
- **Field campaign.** The 10 of 18 runs within 10° of 180 at 3 m/s or more, each with its own $$U_R$$ and tracer flow, give a geometric-mean $$c^\ast$$ at each point; the spread of the field at point 1 is a factor of 4.5. The model against that mean scores R 0.46, 0.29 and 0.22, FAC2 0.07 and FB +1.01 to +1.29, and lies inside the field's minimum–maximum range at 2 of the 15 points. The tunnel's WD 180 against the same mean scores R 0.98, FAC2 0.60 and FB −0.59: the tunnel is higher than the field's geometric mean at the same points (mean $$c^\ast$$ 1.00 against 0.54).
- **Velocity.** $$\lvert\mathbf{U}\rvert$$: R 0.60, FAC2 0.73, FB +0.19, means 0.206 modelled against 0.247 measured. $$U$$: R 0.71, FAC2 0.27, FB +1.46, the mean $$U/U_R$$ 0.026 modelled against 0.164 measured. $$V$$: R 0.73; flipping its sign gives −0.73. $$W$$: R 0.18. $$k$$: R 0.45, FAC2 0.13 and FB +1.13 (mean $$k/U_R^2$$ 0.008 against 0.029).

<details markdown="block">
<summary>Interpretation: Case M tracer, plume and velocity</summary>

- The tracer is under-predicted at every Schmidt number and the pattern is weakly correlated; the choice of normalising speed does not change this. A higher Schmidt number lowers the modelled $$c^\ast$$ further.
- The tracer goes downwind. The mirrored points score better than the real points, so the modelled plume is displaced sideways against the tunnel's.
- The model's FAC2 of 0.13 to 0.20 is below the 0.73 and 0.80 that the tunnel's neighbouring headings score against its WD 180, and a steady solve at one heading is not a mean over headings.
- The magnitude of the velocity is close and the streamwise component is not: $$V$$ correlates and its sign agrees with the tunnel's, $$W$$ does not.

</details>

{% include figure.html name="case-m-openfoam-plan.png" alt="Case M, the tracer on the plan of the campus" caption="<strong>Figure 3.</strong> Case M, WD 180: $$\log_{10}$$ of $$c^\ast$$ at the 15 points on the plan of the campus, the tunnel and the three Schmidt numbers on one scale (open: below $$10^{-3}$$ or zero). The star is the gas source and the square the reference mast; the arrow is the wind." %}

## Not run

- A second mesh or iteration count.
- WD 175 and WD 185, which the tunnel also measured. Model set-up: a cylinder on the terrain sheet, none of the tunnel's side walls and ceiling, a smooth floor under the tabulated inflow. Its source is a 4 m cube of 20 cells where the tunnel's outlet is 6 mm (3.6 m at 1:600).
- OpenLB, FluidX3D, UMF and the ML surrogate.

<details markdown="block">
<summary>Interpretation: Limits of this run</summary>

- With one mesh and the residual control unmet, none of these numbers is mesh- or iteration-independent.
- A finer source or a finer surface mesh was not tried, so the source size's effect on the tracer scores is unknown.

</details>
