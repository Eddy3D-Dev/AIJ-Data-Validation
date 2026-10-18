---
title: "Validation"
parent: "Case G — flow behind a tree belt"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case G — flow behind a tree belt: Eddy3D's scores against the measurements, by engine."
---

# Case G: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

LAD and Cd are not in the dataset (only the shading rate, 81 %). The drag values are crowns of the Eddy3D vegetation library; no optimiser is run against the 28 points.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration open-field

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| \|U\|/U(7 m) (control: no belt) | +0.300 | 0.464 | -0.659 | 0.000 | 28 |
| √(\|U\|²+2k)/U(7 m) (control: no belt) | +0.278 | 0.357 | -0.681 | 0.000 | 28 |
| k/U(7 m)² (control: no belt) | -0.087 | 0.714 | +0.300 | 0.250 | 28 |
| \|U\|/U\_H, imposed (control: no belt) | +0.300 | 0.571 | -0.645 | 0.000 | 28 |
| √(\|U\|²+2k)/U\_H, imposed (control: no belt) | +0.278 | 0.464 | -0.667 | 0.000 | 28 |
{: .scores }

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: no belt, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 90,576 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration pine

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| \|U\|/U(7 m) | +0.503 | 1.000 | -0.425 | 0.036 | 28 |
| √(\|U\|²+2k)/U(7 m) | +0.491 | 1.000 | -0.470 | 0.000 | 28 |
| k/U(7 m)² | +0.213 | 0.714 | +0.138 | 0.143 | 28 |
| \|U\|/U\_H, imposed | +0.503 | 1.000 | -0.407 | 0.036 | 28 |
| √(\|U\|²+2k)/U\_H, imposed | +0.491 | 1.000 | -0.452 | 0.036 | 28 |
{: .scores }

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: pine, Cd·LAD 0.30 1/m, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 90,576 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration conifer

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| \|U\|/U(7 m) | +0.489 | 1.000 | -0.248 | 0.286 | 28 |
| √(\|U\|²+2k)/U(7 m) | +0.504 | 1.000 | -0.329 | 0.071 | 28 |
| k/U(7 m)² | +0.278 | 0.750 | -0.090 | 0.179 | 28 |
| \|U\|/U\_H, imposed | +0.489 | 1.000 | -0.227 | 0.464 | 28 |
| √(\|U\|²+2k)/U\_H, imposed | +0.504 | 1.000 | -0.309 | 0.143 | 28 |
{: .scores }

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: conifer, Cd·LAD 0.625 1/m, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 90,576 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration screen

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| \|U\|/U(7 m) | +0.459 | 1.000 | -0.148 | 0.857 | 28 |
| √(\|U\|²+2k)/U(7 m) | +0.472 | 1.000 | -0.258 | 0.250 | 28 |
| k/U(7 m)² | +0.234 | 0.679 | -0.206 | 0.214 | 28 |
| \|U\|/U\_H, imposed | +0.459 | 1.000 | -0.126 | 0.893 | 28 |
| √(\|U\|²+2k)/U\_H, imposed | +0.472 | 1.000 | -0.237 | 0.321 | 28 |
{: .scores }

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: screen, Cd·LAD 0.875 1/m, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 90,576 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration half-belt-conifer

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| \|U\|/U(7 m) | +0.468 | 1.000 | -0.202 | 0.607 | 28 |
| √(\|U\|²+2k)/U(7 m) | +0.469 | 1.000 | -0.290 | 0.179 | 28 |
| k/U(7 m)² | +0.228 | 0.750 | -0.081 | 0.179 | 28 |
| \|U\|/U\_H, imposed | +0.468 | 1.000 | -0.178 | 0.750 | 28 |
| √(\|U\|²+2k)/U\_H, imposed | +0.469 | 1.000 | -0.266 | 0.286 | 28 |
{: .scores }

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: the real 74 m belt as a half domain, conifer, Cd·LAD 0.625 1/m, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 625,252 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

## All runs

- Quantity: U/U\_H and k/U\_H^2 at the 28 points, U\_H the wind at the tree height (7 m): the measured mean scalar speed against the modelled |U| and sqrt(|U|^2 + 2k), both over the model\'s own U(7 m) at x = -35 m, and over the imposed U\_H = 5.299 m/s; LAD and Cd are not in the dataset
- Normalisation: the field\'s U/U\_H and k/U\_H^2 (U\_H = the wind at the tree height, 7 m, during each period) against the model\'s |U| and k over the model\'s own U(7 m) at x = -35 m (\'own approach\') and, in the second set of scores, over the imposed U\_H = 5.299 m/s (\'imposed\'); the model is also scored as sqrt(|U|^2 + 2k), because the field is the mean of an instantaneous speed; hit rate D = 0.25, W = 0.05
- Per-point values: [`/api/cases/G/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/G/pairs/openfoam12-realizableKE.csv' | relative_url }})

Notes:

- The three crowns are entries of the Eddy3D vegetation library (Cd·LAD 0.30, 0.625 and 0.875 1/m, loss coefficients 1.2, 2.5 and 3.5).
- Eddy3D models trees as a Darcy-Forchheimer momentum sink only: there are no canopy k or epsilon source terms.
- The slab arms idealise the belt as two-dimensional (the belt through both slip planes, infinite width; the data paper\'s Figure 7 draws a two-dimensional tree); the half-belt arm is the real 74 m belt on a half domain with its centre plane on the symmetry plane. Both are scored against the same 28 values.
- The tabulated inlet carries the workbook\'s inflow over a smooth floor (the site\'s roughness is not in the model), so the approach flow does not stay the imposed profile: in the open-field arm it is 1.19 of it at 1.5 m and 0.995 at 7 m at x = -10 m, and the model\'s U(7 m) at x = -35 m is 0.976 to 0.984 of the imposed U\_H. The headline scores divide the model by that own U(7 m).
- The field is the mean of the instantaneous speed of a 3-D sonic anemometer, which exceeds |U| in a turbulent wake: the model is scored as |U| and as sqrt(|U|^2 + 2k), the bracket of Cases C to E.
- The approach profile and the wake were measured on different days (28 and 26 December 2000), and the approach k does not match the workbook\'s own inflow note (k/U\_b^2 = 0.20 at 9 m against the note\'s constant 3.02 m^2/s^2, 0.096 U\_b^2). The files do not explain the mismatch.
- Every arm ran to the 3000-iteration limit with the residualControl unmet; the epsilon initial residual at the last iteration was 2.7e-2 to 3.6e-2 in the slab arms and 3.2e-2 in the half belt.
- Every arm with trees shows a velocity deficit directly behind the belt against the open field, recovery with distance, a speed-up through the 1.2 m gap, and more drag slowing the lee more and pushing more wind through the gap.

<details markdown="block">
<summary>Interpretation: Case G drag sweep</summary>

The arm nearest the 28 values says which library crown the belt resembles. The modelled k behind the belt follows from the inflow and the shear layer over the belt.

</details>

<details markdown="block">
  <summary>How the scores are computed</summary>

- Scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

</details>

## Figures

Figures: [Cases G and K (OpenFOAM)]({{ '/validation/cases-gk/' | relative_url }}).
