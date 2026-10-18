---
title: "Cases G and K (OpenFOAM)"
parent: Validation
nav_order: 7
summary: "OpenFOAM 12 on the 9 x 9 cube array with a floor source (Case K) and on the tree belt (Case G, a drag sweep): velocity, k and tracer concentration"
description: "OpenFOAM 12 against the wind tunnel for Case K (9 x 9 cube array, floor point source) and against the field for Case G (flow behind a tree belt, with an unknown leaf area density): velocity, turbulent kinetic energy and tracer concentration."
---

# Cases G and K, OpenFOAM 12

The reading of the OpenFOAM 12 runs on the 9 × 9 cube array with a floor point source (Case K) and on the flow behind a black-pine belt (Case G). Every score of each run, with the per-point files and the caveats recorded with the run, is on the [Case K]({{ '/cases/case-k/validation/' | relative_url }}) and [Case G]({{ '/cases/case-g/validation/' | relative_url }}) Validation pages. All runs are Eddy3D production runs solved on 2026-10-18, realizable k-ε at numerics level 3 and 3000 iterations. The solves ran to the iteration limit with the SIMPLE residual control unmet; the initial residual of epsilon at the last iteration was 7 × 10⁻³ in Case K and 2.7 × 10⁻² to 3.6 × 10⁻² in Case G. Each case was solved on one mesh only.

## How these runs are scored

- The measured side of every pair is the cleaned table, the legacy workbook at full precision. Eddy3D's own scores were computed against the published CSVs, which round the workbooks, so they differ from these in the third digit. The scores here are recomputed from the per-point files by `validation/dispersion_metrics.py`, which reproduces Eddy3D's metrics: fed the published CSVs and Eddy3D's probes it gives the fixtures' own scores to 10⁻⁹ (43 scores of Case K, five of each arm of Case G).
- **Case K** is the tunnel at 1:100 (H = 6 m). Measured and modelled velocities are both divided by the dataset's stated U_H = 2.33 m/s and k by U_H². The model is driven by the measured approach profile (3.23 m/s at 0.2 m), which gives 1.97 m/s at z = H, 0.85 of the stated U_H. The concentration is the measured C/c₀ (c₀ = 429.2 ppm) against the model's c\* = c U_H H²/Q at the turbulent Schmidt numbers 0.3, 0.5 and 0.7, three species on one flow; all three are published, none is chosen.
- **Case G** is a field observation at full scale. The measurement is U/U_H and k/U_H² at 28 points, U_H the wind at the tree height (7 m) during each period. Eddy3D models trees as a Darcy-Forchheimer momentum sink only, and the leaf area density (LAD) and drag coefficient (Cd) of the belt are not in the dataset (only its shading rate, 81 %). So Eddy3D solved a **sweep**: no belt, and three crowns from its vegetation library of rising Cd·LAD (0.30, 0.625 and 0.875 1/m), on a two-dimensional slab, and the conifer crown on the real 74 m belt as a half domain. Each arm is a separate run, none is chosen as the result. The model is divided by its own U(7 m) at x = −35 m (the tabulated inlet has a smooth floor, so the approach does not stay the imposed profile); scores over the imposed U_H = 5.299 m/s are in the files too.

## Case K: does the model agree?

{% include figure.html name="case-k-layout.png" alt="Measurement lines and planes, Case K" caption="<strong>Figure 1.</strong> Case K, measurement lines and planes: A vertical profiles, y/H = 0; B vertical profiles, y/H = ±1; C vertical profiles, y/H = ±2; D vertical profiles, y/H = ±3. Positions in multiples of H." %}

{% include figure.html name="case-k-openfoam-agreement.png" alt="Case K, measured vs modelled" caption="<strong>Figure 2.</strong> Case K, measured vs modelled U, W, k and c* at three turbulent Schmidt numbers; the dots take the colour of their line in Figure 1. The concentration panels show the positive pairs within five decades; the four points within one cube height of the source are open." %}

| Quantity | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| U | +0.958 | 0.586 | +0.594 | 0.123 | 203 |
| V | −0.151 | 0.054 | — | 0.901 | 203 |
| W | +0.573 | 0.143 | — | 0.685 | 203 |
| k | +0.330 | 0.044 | +1.201 | 0.005 | 203 |
| c\*, Sct 0.3 | +0.953 | 0.793 | −0.690 | 0.458 | 203 |
| c\*, Sct 0.5 | +0.951 | 0.685 | −0.875 | 0.163 | 203 |
| c\*, Sct 0.7 | +0.950 | 0.394 | −0.983 | 0.099 | 203 |
| c\*, Sct 0.3, without the 4 near-source points | +0.923 | 0.799 | −0.218 | 0.467 | 199 |
| c\*, Sct 0.5, without the 4 near-source points | +0.941 | 0.698 | −0.430 | 0.161 | 199 |
| c\*, Sct 0.7, without the 4 near-source points | +0.923 | 0.402 | −0.561 | 0.101 | 199 |
| U, y-symmetric ceiling (control) | +1.000 | 1.000 | +0.000 | 1.000 | 203 |
| c\*, y-symmetric ceiling (control) | +0.997 | 0.995 | +0.000 | 0.793 | 203 |
{: .scores }

FB is positive when the model is low, and is left out (—) for a signed component whose measured and modelled means are not both positive. What the numbers say:

- **The modelled velocity is under the measured mean.** U has R = 0.96 and FAC2 0.59; the mean U/U_H is 0.272 modelled against 0.502 measured (FB +0.59). The deficit is in every region: FB +0.35 over the roofs (31 points, FAC2 1.00, but R +0.06), +0.79 in the streets along the wind (44 points, R +0.997, FAC2 0.34) and +0.78 in the streets across it (128 points, R +0.95, FAC2 0.57). Part of it is the inflow: both sides are divided by 2.33 m/s, and the solved U at z = H is 0.85 of that.
- **k is a factor of four low and uncorrelated.** The mean k/U_H² is 0.027 modelled against 0.107 measured; R is 0.33 and FAC2 0.04. Eddy3D notes that the inlet k of the log-law inflow is about 1.7 times the tunnel's: the model starts with more k than the tunnel and has less at the points.
- **V and W carry little.** V has a constant offset in the tunnel and almost no antisymmetric part: a model with V = 0 everywhere hits 0.91 of the points (W = 0.05 U_H), so V's hit rate of 0.90 scores nothing and its R is −0.15. W has R = +0.57 and FAC2 0.14.
- **The concentration pattern is correlated and the level is high.** R is 0.95 at every Schmidt number. FAC2 falls from 0.79 to 0.39 and FB from −0.69 to −0.98 as the Schmidt number rises: the mean c\* is 0.374 measured against 0.768, 0.956 and 1.097 modelled. The modelled peak at the measured points is 44, 57 and 66 against a measured peak of 8.73, and the four points within one cube height of the source (the first point *is* the source location) are 3.7, 4.5 and 5.1 times too high on average: the model's source is the four cells (0.75 m across) that a 0.44 m square cuts, not the 5 mm outlet. Without those four, FB is −0.22, −0.43 and −0.56, FAC2 0.80, 0.70 and 0.40, R 0.92, 0.94 and 0.92. The comparison with Case H (also over-predicted at all three) is on the [Cases H and I]({{ '/validation/cases-hi/' | relative_url }}) page.
- **The ceiling of a symmetric model is not what limits the scores.** The measured plume is not y-symmetric (C at −y exceeds C at +y at 74 of 74 mirror pairs; Eddy3D puts its lateral centroid 0.011 to 0.017 m toward −y), and the solve is. Scored against the mean of each mirror pair, the measurement has R = 1.00 for U and R = 0.997, FAC2 0.995 for c\*, far above the model's scores. In Eddy3D's own results a lateral shift of the model by +0.01 m raises R of c\* at Sct 0.5 from 0.951 to 0.975 (not recomputed here).
- **47 of the 203 points** (the z = 4 mm plane) are inside the first ground cell, so their modelled values are that cell's, pulled toward the wall's zero by the interpolation.

Eddy3D's structure checks on this solve passed: the air over the roofs outruns the street along the wind, which outruns the cavity across it; the plume leaves the source, is clean 1 to 1.5 H ahead of the array, decays through four cavities and is cleaner over the roofs than in them; the solved velocity is y-symmetric to twice the tunnel's own mirror-pair difference. They set no band on the statistics above.

## Case G: what does the unknown drag do?

{% include figure.html name="case-g-layout.png" alt="Measurement lines and planes, Case G" caption="<strong>Figure 3.</strong> Case G, measurement lines and planes: A to G vertical profiles, x/H = 0.25, 0.5, 1, 2, 3, 4, 5. Positions in multiples of H." %}

{% include figure.html name="case-g-openfoam-sweep.png" alt="Case G, measured vs modelled, drag sweep" caption="<strong>Figure 4.</strong> Case G, the field's U/U_H and k/U_H² against the modelled |U| and k over the model's own U(7 m), one column per arm of the drag sweep; the dots take the colour of their line in Figure 3." %}

| Arm | Cd·LAD [1/m] | U R | U FAC2 | U FB | U hit rate | mean U/U_H | RMSE of U |
|---|---|---|---|---|---|---|---|
| no belt (control) | 0 | +0.300 | 0.464 | −0.659 | 0.000 | 0.948 | 0.474 |
| pine | 0.30 | +0.503 | 1.000 | −0.425 | 0.036 | 0.735 | 0.262 |
| conifer | 0.625 | +0.489 | 1.000 | −0.248 | 0.286 | 0.613 | 0.145 |
| screen | 0.875 | +0.459 | 1.000 | −0.148 | 0.857 | 0.554 | 0.097 |
| conifer, real belt (half domain) | 0.625 | +0.468 | 1.000 | −0.202 | 0.607 | 0.585 | 0.120 |
{: .scores }

The field's mean U/U_H over the 28 points is 0.478. Here the model is |U| over its own U(7 m); the same scores over the imposed U_H, and for √(|U|² + 2k), are in the files. The same arms for k:

| Arm | k R | k FAC2 | k FB | mean k/U_H² |
|---|---|---|---|---|
| no belt (control) | −0.087 | 0.714 | +0.300 | 0.023 |
| pine | +0.213 | 0.714 | +0.138 | 0.027 |
| conifer | +0.278 | 0.750 | −0.090 | 0.034 |
| screen | +0.234 | 0.679 | −0.206 | 0.038 |
| conifer, real belt (half domain) | +0.228 | 0.750 | −0.081 | 0.034 |
{: .scores }

The field's mean k/U_H² is 0.031.

{% include figure.html name="case-g-openfoam-stations.png" alt="Case G, by station" caption="<strong>Figure 5.</strong> Case G, the letters A to G mark the seven lines of Figure 3; the mean U/U_H and the mean k/U_H² over the four heights at each station behind the belt, the field against each arm of the drag sweep." %}

- **Drag moves the level, not the pattern.** The mean speed falls from 0.948 with no belt to 0.735, 0.613 and 0.554 as Cd·LAD rises, and the root-mean-square error of U from 0.474 to 0.097, but R stays between +0.46 and +0.50 in every arm with trees (+0.30 with none). That the arm nearest the data is the densest one is a calibration against these 28 values, not a validation: LAD and Cd are not in the dataset, and nothing is fitted. It is also the edge of the sweep: even the densest library crown leaves the mean speed above the measured 0.478, so the sweep does not bracket the field.
- **Every tree arm is within a factor of two at all 28 points**, which the no-belt control (FAC2 0.46) is not. For U, FB is negative in every arm: the model is high.
- **The streamwise shape is present only in part.** The field's station-mean speed is lowest at x/H = 1 (0.435) and recovers to 0.51 at 4 H; the conifer arm has its minimum at the same station (0.586) and recovers to 0.661 at 5 H. For k the trend is the other way: the field's mean k/U_H² rises from 0.018 at 1 H to 0.053 at 5 H, and falls in every arm (conifer 0.036 to 0.030). Eddy3D's trees have no canopy k or ε source terms, so the modelled k behind the belt is what the inflow and the shear layer over the belt produce; k is recorded and never asserted.
- **The two-dimensional idealisation costs 0.028.** The real belt on a half domain is slower than the infinite slab by 0.028 of U/U(7 m) on average (at most 0.042 over the 28 points; R between the two 0.99), against the 0.12 between the pine and the conifer crown of the sweep.
- Eddy3D's structure checks passed for every arm with trees: a velocity deficit directly behind the belt against the open field, recovery with distance, a speed-up through the 1.2 m gap, and more drag slowing the lee more and pushing more wind through the gap.

## What was not checked

- No second mesh or iteration count was run for either case, and the residual control was not met, so none of these numbers is mesh- or iteration-independent.
- Case G was not solved with LAD or Cd other than the three library crowns, and the wind direction relative to the belt normal is not published, so the two-dimensional slab is an assumption (the half belt is the only check on it).
- Case K's concentration near the source depends on a source zone of four cells; a finer source was not tried.
- OpenLB, FluidX3D and the ML surrogate have not been run on either case.
