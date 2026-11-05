---
title: "Validation"
parent: "Case K"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case K — 9 x 9 cube array, point source: Eddy3D's scores against the measurements, engine by engine."
---

# Case K: validation
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

{% include nomenclature.md %}

## Measurement locations

{% include validation/case-k/layout.md %}

## Explore the points

{% include explorer.html case="K" %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-k/openfoam.md %}

### Scores

Quantity: $$U$$, $$V$$, $$W$$ over the stated $$U_H$$ = 2.33 m/s and $$k$$ over $$U_H^2$$ (split fibre, 203 points); $$c^\ast = C/c_0$$ ($$c_0 = \dfrac{q}{U_H H^2}$$ = 429.2 ppm) against the model\'s $$c\thinspace U_H H^2/Q$$ for turbulent Schmidt numbers 0.3, 0.5 and 0.7; the four points within one cube height of the source are scored with and without.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.958 | 0.917 | 0.586 | +0.594 | 0.123 | 203 |
| $$V$$ | -0.151 | 0.023 | 0.054 | — | 0.901 | 203 |
| $$W$$ | +0.573 | 0.329 | 0.143 | — | 0.685 | 203 |
| $$k$$ | +0.330 | 0.109 | 0.044 | +1.201 | 0.005 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.953 | 0.908 | 0.793 | -0.690 | 0.458 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.951 | 0.905 | 0.685 | -0.875 | 0.163 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.950 | 0.903 | 0.394 | -0.983 | 0.099 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, without the 4 near-source points | +0.923 | 0.853 | 0.799 | -0.218 | 0.467 | 199 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, without the 4 near-source points | +0.941 | 0.886 | 0.698 | -0.430 | 0.161 | 199 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, without the 4 near-source points | +0.923 | 0.851 | 0.402 | -0.561 | 0.101 | 199 |
| $$U$$, y-symmetric ceiling (control) | +1.000 | 1.000 | 1.000 | +0.000 | 1.000 | 203 |
| $$c^\ast$$, y-symmetric ceiling (control) | +0.997 | 0.994 | 0.995 | +0.000 | 0.793 | 203 |
{: .scores }

- Normalisation: $$U$$, $$V$$, $$W$$ by the stated $$U_H$$ = 2.33 m/s and $$k$$ by $$U_H^2$$, the same divisor on both sides; $$c^\ast$$ is the measured $$C/c_0$$ ($$c_0 = \dfrac{q}{U_H H^2}$$ = 429.2 ppm) against the modelled $$c\thinspace U_H H^2/Q$$ (full scale, $$Q = 1\thinspace\mathrm{kg/s}$$) for turbulent Schmidt numbers 0.3, 0.5 and 0.7, with one detection limit of $$10^{-3}$$ of the largest measured value; hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in $$U_H$$
- Per-point values: [`/api/cases/K/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/K/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseKContainerE2E (9 x 9 cubes, floor point source, 1:100; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 972,637 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py

Notes:

- The inflow is the measured approach profile (3.23 m/s at 0.2 m, $$z_0$$ fitted to 13.5 mm). The stated $$U_H$$ = 2.33 m/s is not on that profile: the solved $$U$$ at $$z = H$$ is 1.97 m/s, 0.85 of the stated $$U_H$$. Measured and modelled velocities are both divided by 2.33 m/s.
- The inlet $$k$$ from that log law, $$u_\ast^2/\sqrt{C_\mu}$$ = 0.77 m²/s², is about 1.7 times the tunnel\'s 0.33 to 0.45.
- The first measurement point is the source location: the four points within one cube height of the floor outlet hold the four largest $$c^\ast$$ (8.73, 5.31, 3.02 and 2.86 against 1.03 for the next). The model\'s source is the 4 cells (0.75 m across) that a 0.44 m square cuts; the outlet is 5 mm. Those four points are scored with and without.
- 47 of the 203 points (the $$z = 4\thinspace\mathrm{mm}$$ plane, 0.4 m at 1:100) lie inside the first ground cell (0.735 m): their modelled values are that cell\'s, pulled toward the wall\'s zero by the point interpolation.
- The measured plume is not y-symmetric (C at -y exceeds C at $$+y$$ at 74 of 74 mirror pairs; its lateral centroid lies 0.011 to 0.017 m toward -y at every station) and the solve is. The \'y-symmetric ceiling\' controls score the measurement against the mean of each mirror pair.
- $$V$$ has a constant offset and almost no antisymmetric part; a model with $$V$$ = 0 everywhere hits 0.91 of the points at $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$.
- The solve stopped at the 3000-iteration limit with the residualControl unmet (no \'solution converged\' line); the epsilon initial residual at the last iteration was 7e-3.
- The air over the roofs outruns the street along the wind, which outruns the cavity across it; the plume leaves the source, is clean 1 to $$1.5\thinspace H$$ ahead of the array, decays through four cavities and is cleaner over the roofs than in them; the solved velocity is y-symmetric to twice the tunnel\'s own mirror-pair difference.

<details markdown="block">
<summary>Interpretation: Case K scores</summary>

The modelled velocity sits under the measured mean. The y-symmetric ceiling is the best a y-symmetric model can do on this file. $$V$$ does not score the flow\'s divergence. $$V$$\'s hit rate says nothing.

</details>

## Not run

{% include validation/case-k/not-run.md %}

<details markdown="block">
  <summary>How the scores are computed</summary>

- Scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

</details>

## Leaderboard

| Rank | Run | Source | Hit rate, $$U$$ | Hit rate, $$V$$ | Hit rate, $$W$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate, $$k$$ | Hit rate, $$c^\ast$$ | Hit rate | FAC2 | R | $$R^2$$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-casek-workbook-inflow]({{ '/community/eddy3d-of12-casek-workbook-inflow/' | relative_url }})) | community | **0.562** | 0.877 | 0.670 | **0.507** | **0.103** | 0.399 | **0.520** | **0.464** | +0.596 | 0.525 |
| 2 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-nutcap-lifted]({{ '/community/eddy3d-of12-nutcap-lifted/' | relative_url }})) | community | 0.232 | **0.901** | 0.680 | 0.192 | 0.039 | **0.478** | 0.420 | 0.415 | **+0.616** | **0.543** |
| 3 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.3 | Eddy3D | 0.123 | **0.901** | **0.685** | 0.084 | 0.005 | 0.458 | 0.376 | 0.363 | +0.602 | 0.530 |
| 4 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.5 | Eddy3D | 0.123 | **0.901** | **0.685** | 0.084 | 0.005 | 0.163 | 0.327 | 0.345 | +0.601 | 0.530 |
| 5 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.7 | Eddy3D | 0.123 | **0.901** | **0.685** | 0.084 | 0.005 | 0.099 | 0.316 | 0.296 | +0.601 | 0.530 |
{: .scores }

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. Every run gave values at every measured point. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
