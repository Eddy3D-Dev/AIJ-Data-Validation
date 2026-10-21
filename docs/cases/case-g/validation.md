---
title: "Validation"
parent: "Case G"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case G — flow behind a tree belt: Eddy3D's scores against the measurements, engine by engine."
redirect_from:
  - /validation/cases-gk/
---

# Case G: validation
{: .no_toc }

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

LAD and Cd are not in the dataset (only the shading rate, 81 %). The drag values are crowns of the Eddy3D vegetation library.

## Measurement locations

{% include validation/case-g/layout.md %}

## Explore the points

{% include explorer.html case="G" %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-g/openfoam.md %}

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration open-field

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert/U(7\text{ m})$$ (control: no belt) | +0.300 | 0.090 | 0.464 | -0.659 | 0.000 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U(7\text{ m})$$ (control: no belt) | +0.278 | 0.077 | 0.357 | -0.681 | 0.000 |
| $$k/U(7\text{ m})^2$$ (control: no belt) | -0.087 | 0.008 | 0.714 | +0.300 | 0.250 |
| $$\lvert\mathbf{U}\rvert/U_H$$, imposed (control: no belt) | +0.300 | 0.090 | 0.571 | -0.645 | 0.000 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U_H$$, imposed (control: no belt) | +0.278 | 0.077 | 0.464 | -0.667 | 0.000 |
{: .scores }

{% include nomenclature-scores.md %}

Every score is over the same 28 points.

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: no belt, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 90,576 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration pine

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert/U(7\text{ m})$$ | +0.503 | 0.253 | 1.000 | -0.425 | 0.036 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U(7\text{ m})$$ | +0.491 | 0.241 | 1.000 | -0.470 | 0.000 |
| $$k/U(7\text{ m})^2$$ | +0.213 | 0.046 | 0.714 | +0.138 | 0.143 |
| $$\lvert\mathbf{U}\rvert/U_H$$, imposed | +0.503 | 0.253 | 1.000 | -0.407 | 0.036 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U_H$$, imposed | +0.491 | 0.241 | 1.000 | -0.452 | 0.036 |
{: .scores }

{% include nomenclature-scores.md %}

Every score is over the same 28 points.

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: pine, Cd·LAD 0.30 1/m, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 90,576 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration conifer

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert/U(7\text{ m})$$ | +0.489 | 0.239 | 1.000 | -0.248 | 0.286 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U(7\text{ m})$$ | +0.504 | 0.254 | 1.000 | -0.329 | 0.071 |
| $$k/U(7\text{ m})^2$$ | +0.278 | 0.077 | 0.750 | -0.090 | 0.179 |
| $$\lvert\mathbf{U}\rvert/U_H$$, imposed | +0.489 | 0.239 | 1.000 | -0.227 | 0.464 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U_H$$, imposed | +0.504 | 0.254 | 1.000 | -0.309 | 0.143 |
{: .scores }

{% include nomenclature-scores.md %}

Every score is over the same 28 points.

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: conifer, Cd·LAD 0.625 1/m, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 90,576 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration screen

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert/U(7\text{ m})$$ | +0.459 | 0.211 | 1.000 | -0.148 | 0.857 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U(7\text{ m})$$ | +0.472 | 0.223 | 1.000 | -0.258 | 0.250 |
| $$k/U(7\text{ m})^2$$ | +0.234 | 0.055 | 0.679 | -0.206 | 0.214 |
| $$\lvert\mathbf{U}\rvert/U_H$$, imposed | +0.459 | 0.211 | 1.000 | -0.126 | 0.893 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U_H$$, imposed | +0.472 | 0.223 | 1.000 | -0.237 | 0.321 |
{: .scores }

{% include nomenclature-scores.md %}

Every score is over the same 28 points.

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: screen, Cd·LAD 0.875 1/m, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 90,576 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration half-belt-conifer

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert/U(7\text{ m})$$ | +0.468 | 0.219 | 1.000 | -0.202 | 0.607 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U(7\text{ m})$$ | +0.469 | 0.220 | 1.000 | -0.290 | 0.179 |
| $$k/U(7\text{ m})^2$$ | +0.228 | 0.052 | 0.750 | -0.081 | 0.179 |
| $$\lvert\mathbf{U}\rvert/U_H$$, imposed | +0.468 | 0.219 | 1.000 | -0.178 | 0.750 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}/U_H$$, imposed | +0.469 | 0.220 | 1.000 | -0.266 | 0.286 |
{: .scores }

{% include nomenclature-scores.md %}

Every score is over the same 28 points.

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E (arm: the real 74 m belt as a half domain, conifer, Cd·LAD 0.625 1/m, full scale; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 625,252 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

## Not run

{% include validation/case-g/not-run.md %}

## Notes on every run

- Quantity: $$U/U_H$$ and $$k/U_H^2$$ at the 28 points, $$U_H$$ the wind at the tree height (7 m): the measured mean scalar speed against the modelled $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$, both over the model\'s own $$U(7\text{ m})$$ at $$x = -35\thinspace\mathrm{m}$$, and over the imposed $$U_H$$ = 5.299 m/s; LAD and Cd are not in the dataset
- Normalisation: the field\'s $$U/U_H$$ and $$k/U_H^2$$ ($$U_H$$ = the wind at the tree height, 7 m, during each period) against the model\'s $$\lvert\mathbf{U}\rvert$$ and $$k$$ over the model\'s own $$U(7\text{ m})$$ at $$x = -35\thinspace\mathrm{m}$$ (\'own approach\') and, in the second set of scores, over the imposed $$U_H$$ = 5.299 m/s (\'imposed\'); the model is also scored as $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$, because the field is the mean of an instantaneous speed; hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$
- Per-point values: [`/api/cases/G/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/G/pairs/openfoam12-realizableKE.csv' | relative_url }})

Notes:

- The three crowns are entries of the Eddy3D vegetation library (Cd·LAD 0.30, 0.625 and 0.875 1/m, loss coefficients 1.2, 2.5 and 3.5).
- Eddy3D models trees as a Darcy-Forchheimer momentum sink only: there are no canopy $$k$$ or epsilon source terms.
- The slab arms idealise the belt as two-dimensional (the belt through both slip planes, infinite width; the data paper\'s Figure 7 draws a two-dimensional tree); the half-belt arm is the real 74 m belt on a half domain with its centre plane on the symmetry plane. Both are scored against the same 28 values.
- The tabulated inlet carries the workbook\'s inflow over a smooth floor (the site\'s roughness is not in the model), so the approach flow does not stay the imposed profile: in the open-field arm it is 1.19 of it at 1.5 m and 0.995 at 7 m at $$x = -10\thinspace\mathrm{m}$$, and the model\'s $$U(7\text{ m})$$ at $$x = -35\thinspace\mathrm{m}$$ is 0.976 to 0.984 of the imposed $$U_H$$. The headline scores divide the model by that own $$U(7\text{ m})$$.
- The field is the mean of the instantaneous speed of a 3-D sonic anemometer, which exceeds $$\lvert\mathbf{U}\rvert$$ in a turbulent wake: the model is scored as $$\lvert\mathbf{U}\rvert$$ and as $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$, the bracket of Cases C to E.
- The approach profile and the wake were measured on different days (28 and 26 December 2000), and the approach $$k$$ does not match the workbook\'s own inflow note ($$k/U_b^2$$ = 0.20 at 9 m against the note\'s constant 3.02 m²/s², 0.096 $$U_b^2$$). The files do not explain the mismatch.
- Every arm ran to the 3000-iteration limit with the residualControl unmet; the epsilon initial residual at the last iteration was 2.7e-2 to 3.6e-2 in the slab arms and 3.2e-2 in the half belt.
- Every arm with trees shows a velocity deficit directly behind the belt against the open field, recovery with distance, a speed-up through the 1.2 m gap, and more drag slowing the lee more and pushing more wind through the gap.

<details markdown="block">
<summary>Interpretation: Case G drag sweep</summary>

The arm nearest the 28 values says which library crown the belt resembles. The modelled $$k$$ behind the belt follows from the inflow and the shear layer over the belt.

</details>

<details markdown="block">
  <summary>How the scores are computed</summary>

- Scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

</details>

## Leaderboard

| Rank | Run | Source | Hit rate, $$k$$ | Hit rate, $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate | FAC2 | R | $$R^2$$ | Points scored |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM 12 · screen | Eddy3D | 0.214 | **0.250** | **0.857** | **0.440** | 0.893 | +0.388 | 0.163 | 100 % |
| 2 | OpenFOAM 12 · half-belt-conifer | Eddy3D | 0.179 | 0.179 | 0.607 | 0.321 | **0.917** | +0.388 | 0.164 | 100 % |
| 3 | OpenFOAM 12 · conifer | Eddy3D | 0.179 | 0.071 | 0.286 | 0.179 | **0.917** | **+0.423** | **0.190** | 100 % |
| 4 | OpenFOAM 12 · open-field | Eddy3D | **0.250** | 0.000 | 0.000 | 0.083 | 0.512 | +0.164 | 0.058 | 100 % |
| 5 | OpenFOAM 12 · pine | Eddy3D | 0.143 | 0.000 | 0.036 | 0.060 | 0.905 | +0.403 | 0.180 | 100 % |
{: .scores }

{% include nomenclature-scores.md %}

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. *Points scored* is the share of the measured points a run gave values at. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
