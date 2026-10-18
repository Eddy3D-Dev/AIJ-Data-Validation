---
title: "Cases G and K (OpenFOAM)"
parent: Validation
nav_order: 7
summary: "OpenFOAM 12 on the 9 x 9 cube array with a floor source (Case K) and on the tree belt (Case G, a drag sweep): velocity, k and tracer concentration"
description: "OpenFOAM 12 against the wind tunnel for Case K (9 x 9 cube array, floor point source) and against the field for Case G (flow behind a tree belt, with an unknown leaf area density): velocity, turbulent kinetic energy and tracer concentration."
---

# Cases G and K, OpenFOAM 12

OpenFOAM 12 runs on the 9 × 9 cube array with a floor point source (Case K) and on the flow behind a black-pine belt (Case G). Per-run scores and per-point files: [Case K]({{ '/cases/case-k/validation/' | relative_url }}) and [Case G]({{ '/cases/case-g/validation/' | relative_url }}) Validation pages.

All runs are Eddy3D production runs solved on 2026-10-18, realizable k-ε at numerics level 3 and 3000 iterations, on one mesh each. The solves ran to the iteration limit with the SIMPLE residual control unmet; the initial residual of epsilon at the last iteration was 7 × 10⁻³ in Case K and 2.7 × 10⁻² to 3.6 × 10⁻² in Case G.

## Runs

- **Case K** is the tunnel at 1:100 (H = 6 m). Measured and modelled velocities are both divided by the dataset's stated $$U_H$$ = 2.33 m/s, and $$k$$ by $$U_H^2$$. The model is driven by the measured approach profile (3.23 m/s at 0.2 m), which gives 1.97 m/s at z = H, 0.85 of the stated $$U_H$$. The concentration is the measured $$C/c_0$$ ($$c_0$$ = 429.2 ppm) against the model's $$c^\ast = c\thinspace U_H H^2/Q$$ at the turbulent Schmidt numbers 0.3, 0.5 and 0.7, three species on one flow; all three are published.
- **Case G** is a field observation at full scale. The measurement is $$U/U_H$$ and $$k/U_H^2$$ at 28 points, $$U_H$$ the wind at the tree height (7 m) during each period. Eddy3D models trees as a Darcy-Forchheimer momentum sink only. The leaf area density (LAD) and drag coefficient (Cd) of the belt are not in the dataset (only its shading rate, 81 %); the drag values are crowns of the Eddy3D vegetation library. Eddy3D solved a **sweep**: no belt, and three crowns from its vegetation library of rising Cd·LAD (0.30, 0.625 and 0.875 1/m), on a two-dimensional slab, and the conifer crown on the real 74 m belt as a half domain. Each arm is a separate run. The model is divided by its own $$U(7\text{ m})$$ at x = −35 m, because the tabulated inlet has a smooth floor and the approach does not stay the imposed profile; scores over the imposed $$U_H$$ = 5.299 m/s are in the files too.

## Case K

### Measurement layout

{% include figure.html name="case-k-layout.png" alt="Measurement lines and planes, Case K" caption="<strong>Figure 1.</strong> Case K, measurement lines and planes: A vertical profiles, y/H = 0; B vertical profiles, y/H = ±1; C vertical profiles, y/H = ±2; D vertical profiles, y/H = ±3. Positions in multiples of H." %}

### Measured against modelled

{% include figure.html name="case-k-openfoam-agreement.png" alt="Case K, measured vs modelled" caption="<strong>Figure 2.</strong> Case K, measured vs modelled U, W, k and c* at three turbulent Schmidt numbers; the dots take the colour of their line in Figure 1. The concentration panels show the positive pairs within five decades; the four points within one cube height of the source are open." %}

| Quantity | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.958 | 0.586 | +0.594 | 0.123 | 203 |
| $$V$$ | −0.151 | 0.054 | — | 0.901 | 203 |
| $$W$$ | +0.573 | 0.143 | — | 0.685 | 203 |
| $$k$$ | +0.330 | 0.044 | +1.201 | 0.005 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.953 | 0.793 | −0.690 | 0.458 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.951 | 0.685 | −0.875 | 0.163 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.950 | 0.394 | −0.983 | 0.099 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, without the 4 near-source points | +0.923 | 0.799 | −0.218 | 0.467 | 199 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, without the 4 near-source points | +0.941 | 0.698 | −0.430 | 0.161 | 199 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, without the 4 near-source points | +0.923 | 0.402 | −0.561 | 0.101 | 199 |
| $$U$$, y-symmetric ceiling (control) | +1.000 | 1.000 | +0.000 | 1.000 | 203 |
| $$c^\ast$$, y-symmetric ceiling (control) | +0.997 | 0.995 | +0.000 | 0.793 | 203 |
{: .scores }

{% include nomenclature-scores.md %}

FB is positive when the model is low, and is left out (—) for a signed component whose measured and modelled means are not both positive.

- **Velocity.** $$U$$: R = 0.96, FAC2 0.59; the mean $$U/U_H$$ is 0.272 modelled against 0.502 measured (FB +0.59). FB by region: +0.35 over the roofs (31 points, FAC2 1.00, R +0.06), +0.79 in the streets along the wind (44 points, R +0.997, FAC2 0.34) and +0.78 in the streets across it (128 points, R +0.95, FAC2 0.57). Both sides are divided by 2.33 m/s; the solved $$U$$ at z = H is 0.85 of that.
- **$$k$$.** The mean $$k/U_H^2$$ is 0.027 modelled against 0.107 measured; R is 0.33 and FAC2 0.04.
- **$$V$$ and $$W$$.** $$V$$ has a constant offset in the tunnel and almost no antisymmetric part. A model with $$V$$ = 0 everywhere hits 0.91 of the points ($$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$); $$V$$'s hit rate is 0.90 and its R is −0.15. $$W$$: R = +0.57, FAC2 0.14.
- **Concentration.** R is 0.95 at every Schmidt number. FAC2 falls from 0.79 to 0.39 and FB from −0.69 to −0.98 as the Schmidt number rises; the mean $$c^\ast$$ is 0.374 measured against 0.768, 0.956 and 1.097 modelled. The modelled peak at the measured points is 44, 57 and 66 against a measured peak of 8.73. The four points within one cube height of the source (the first point *is* the source location) are 3.7, 4.5 and 5.1 times the measured value on average. Without those four points: FB −0.22, −0.43 and −0.56, FAC2 0.80, 0.70 and 0.40, R 0.92, 0.94 and 0.92. Case H has FB −0.60, −0.83 and −0.93 at the same three Schmidt numbers ([Cases H and I]({{ '/validation/cases-hi/' | relative_url }})).
- **Symmetry.** The measured plume is not y-symmetric: C at −y exceeds C at +y at 74 of 74 mirror pairs, and Eddy3D puts the measured plume's lateral centroid 0.011 to 0.017 m toward −y. The solve is y-symmetric. Scored against the mean of each mirror pair, the measurement has R = 1.00 for $$U$$ and R = 0.997, FAC2 0.995 for $$c^\ast$$ (the ceiling-control rows).
- **First ground cell.** 47 of the 203 points (the z = 4 mm plane) are inside the first ground cell; their modelled values are that cell's, pulled toward the wall's zero by the interpolation.
- **Flow structure.** The air over the roofs outruns the street along the wind, which outruns the cavity across it; the plume is clean 1 to 1.5 H ahead of the array, decays through four cavities and is cleaner over the roofs than in them; the solved velocity is y-symmetric to twice the tunnel's own mirror-pair difference.

<details markdown="block">
<summary>Interpretation: Case K velocity, k and concentration</summary>

- The modelled velocity is under the measured mean in every region. Part of the deficit is the inflow.
- $$k$$ is a factor of four low and uncorrelated: the model starts with more $$k$$ than the tunnel (the inlet $$k$$ of the log-law inflow is about 1.7 times the tunnel's) and has less at the points.
- $$V$$ and $$W$$ carry little. $$V$$'s hit rate of 0.90 scores nothing, because a model with $$V$$ = 0 everywhere hits almost as many points.
- The concentration pattern is correlated and the level is high. The excess at the four near-source points follows from the model's source: the four cells (0.75 m across) that a 0.44 m square cuts, where the tunnel's outlet is 5 mm.
- The ceiling scores of a y-symmetric model are far above the model's, so symmetry does not limit the scores. In Eddy3D's own results a lateral shift of the model by +0.01 m raises R of $$c^\ast$$ at $$\mathrm{Sc_t}$$ 0.5 from 0.951 to 0.975 (not recomputed here).

</details>

## Case G

### Measurement layout

{% include figure.html name="case-g-layout.png" alt="Measurement lines and planes, Case G" caption="<strong>Figure 3.</strong> Case G, measurement lines and planes: A to G vertical profiles, x/H = 0.25, 0.5, 1, 2, 3, 4, 5. Positions in multiples of H." %}

### Measured against modelled

{% include figure.html name="case-g-openfoam-sweep.png" alt="Case G, measured vs modelled, drag sweep" caption="<strong>Figure 4.</strong> Case G, the field's U/U_H and k/U_H² against the modelled |U| and k over the model's own U(7 m), one column per arm of the drag sweep; the dots take the colour of their line in Figure 3." %}

| Arm | Cd·LAD [1/m] | $$U$$ R | $$U$$ FAC2 | $$U$$ FB | $$U$$ hit rate | mean $$U/U_H$$ | RMSE of $$U$$ |
|---|---|---|---|---|---|---|---|
| no belt (control) | 0 | +0.300 | 0.464 | −0.659 | 0.000 | 0.948 | 0.474 |
| pine | 0.30 | +0.503 | 1.000 | −0.425 | 0.036 | 0.735 | 0.262 |
| conifer | 0.625 | +0.489 | 1.000 | −0.248 | 0.286 | 0.613 | 0.145 |
| screen | 0.875 | +0.459 | 1.000 | −0.148 | 0.857 | 0.554 | 0.097 |
| conifer, real belt (half domain) | 0.625 | +0.468 | 1.000 | −0.202 | 0.607 | 0.585 | 0.120 |
{: .scores }

{% include nomenclature-scores.md %}

The field's mean $$U/U_H$$ over the 28 points is 0.478. The model is $$\lvert\mathbf{U}\rvert$$ over its own $$U(7\text{ m})$$; the same scores over the imposed $$U_H$$, and for $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$, are in the files. The same arms for $$k$$:

| Arm | $$k$$ R | $$k$$ FAC2 | $$k$$ FB | mean $$k/U_H^2$$ |
|---|---|---|---|---|
| no belt (control) | −0.087 | 0.714 | +0.300 | 0.023 |
| pine | +0.213 | 0.714 | +0.138 | 0.027 |
| conifer | +0.278 | 0.750 | −0.090 | 0.034 |
| screen | +0.234 | 0.679 | −0.206 | 0.038 |
| conifer, real belt (half domain) | +0.228 | 0.750 | −0.081 | 0.034 |
{: .scores }

{% include nomenclature-scores.md %}

The field's mean $$k/U_H^2$$ is 0.031.

{% include figure.html name="case-g-openfoam-stations.png" alt="Case G, by station" caption="<strong>Figure 5.</strong> Case G, the letters A to G mark the seven lines of Figure 3; the mean U/U_H and the mean k/U_H² over the four heights at each station behind the belt, the field against each arm of the drag sweep." %}

- **Drag.** The mean $$U/U_H$$ falls from 0.948 with no belt to 0.735, 0.613 and 0.554 as Cd·LAD rises, and the RMSE of $$U$$ from 0.474 to 0.097. $$U$$ R stays between +0.46 and +0.50 in every arm with trees (+0.30 with none). The densest crown has mean $$U/U_H$$ 0.554 against 0.478 measured.
- **Factor of two.** In every arm with trees, all 28 points are within a factor of two (FAC2 1.000); with no belt FAC2 is 0.464. For $$U$$, FB is negative in every arm (the model is high).
- **Stations.** The field's station-mean speed is lowest at x/H = 1 (0.435) and recovers to 0.51 at 4 H; the conifer arm has its minimum at the same station (0.586) and recovers to 0.661 at 5 H. The field's mean $$k/U_H^2$$ rises from 0.018 at 1 H to 0.053 at 5 H; in every arm it falls (conifer 0.036 to 0.030). Eddy3D's trees have no canopy $$k$$ or ε source terms.
- **Two dimensions against the real belt.** The real belt on a half domain is slower than the infinite slab by 0.028 of $$U/U(7\text{ m})$$ on average (at most 0.042 over the 28 points; R between the two 0.99). Between the pine and the conifer crown of the sweep the difference is 0.12.
- **Flow structure.** In every arm with trees: a velocity deficit directly behind the belt against the open field, recovery with distance, a speed-up through the 1.2 m gap, and more drag slowing the lee more and pushing more wind through the gap.

<details markdown="block">
<summary>Interpretation: Case G drag sweep</summary>

- Drag changes the level of the mean speed and leaves the pattern (R) where it was.
- The arm nearest the data is the densest one and the edge of the sweep, so the sweep does not bracket the field.
- The streamwise shape is present only in part. For $$k$$ the trend is the other way, and the modelled $$k$$ behind the belt is what the inflow and the shear layer over the belt produce.
- The two-dimensional idealisation costs 0.028 of $$U/U(7\text{ m})$$, against 0.12 between the pine and the conifer crown.

</details>

## Not run

- A second mesh or iteration count, for either case.
- Case G: LAD or Cd other than the three library crowns. The wind direction relative to the belt normal is not published.
- Case K: a finer source.
- OpenLB, FluidX3D and the ML surrogate, on either case.

<details markdown="block">
<summary>Interpretation: Limits of these runs</summary>

- With one mesh per case and the residual control unmet, none of these numbers is mesh- or iteration-independent.
- Case K's concentration near the source depends on a source zone of four cells.
- Case G's two-dimensional slab is an assumption, and the half belt is the only check on it.

</details>
