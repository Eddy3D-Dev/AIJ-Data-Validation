---
title: "Validation"
parent: "Case M"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case M — TPU Atsugi campus: Eddy3D's scores against the measurements, engine by engine."
---

# Case M: validation
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

## Measurement locations

{% include validation/case-m/layout.md %}

## Explore the points

{% include explorer.html case="M" %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-m/openfoam.md %}

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration sct03

Quantity: $$U$$, $$V$$, $$W$$ and $$k$$ at the 15 points of the tunnel\'s WD 180 run over the tunnel\'s $$U_R$$ = 4.08 m/s (measured) and over the solved speed at the reference mast (modelled; $$U_R$$ is defined at the mast), and the dimensionless concentration $$c^\ast = C/c_0$$ ($$c_0 = \dfrac{q}{U_R H_R^2}$$ = 132.5 ppm) against the model\'s $$c\thinspace U_R H_R^2/Q$$ for turbulent Schmidt number 0.3; the 18-run field campaign is compared as well.

<details markdown="block">
  <summary>All 16 headline scores</summary>

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$c^\ast$$ | +0.412 | 0.170 | 0.200 | +1.396 | 0.133 | 15 |
| $$c^\ast$$, over the imposed speed at the mast\'s height (3.934 m/s) | +0.412 | 0.170 | 0.200 | +1.480 | 0.067 | 15 |
| $$c^\ast$$, over the tunnel\'s $$U_R$$ = 4.08 m/s | +0.412 | 0.170 | 0.200 | +1.464 | 0.067 | 15 |
| $$c^\ast$$, points turned 180° about the source (control) | -0.050 | 0.002 | 0.071 | +2.000 | 0.071 | 14 |
| $$c^\ast$$, points mirrored across the plume axis (control) | +0.675 | 0.456 | 0.467 | +0.321 | 0.133 | 15 |
| $$c^\ast$$, tunnel WD 175 as a model of its WD 180 (control) | +0.932 | 0.868 | 0.733 | +0.401 | 0.267 | 15 |
| $$c^\ast$$, tunnel WD 185 as a model of its WD 180 (control) | +0.976 | 0.952 | 0.800 | -0.117 | 0.533 | 15 |
| $$c^\ast$$, mean of the tunnel\'s WD 175 and WD 185 as a model of its WD 180 (control) | +0.998 | 0.995 | 1.000 | +0.111 | 0.867 | 15 |
| $$c^\ast$$ against the field\'s geometric mean (10 runs) | +0.464 | 0.215 | 0.067 | +1.012 | 0.000 | 15 |
| $$c^\ast$$, tunnel WD 180 as a model of the field\'s geometric mean (control) | +0.984 | 0.969 | 0.600 | -0.593 | 0.000 | 15 |
| $$U$$ | +0.708 | 0.502 | 0.267 | +1.460 | 0.267 | 15 |
| $$V$$ | +0.731 | 0.534 | 0.333 | — | 0.133 | 15 |
| $$V$$, sign flipped (control) | -0.731 | 0.534 | 0.067 | -0.616 | 0.133 | 15 |
| $$W$$ | +0.181 | 0.033 | 0.267 | — | 0.733 | 15 |
| $$\lvert\mathbf{U}\rvert$$ | +0.601 | 0.362 | 0.733 | +0.185 | 0.400 | 15 |
| $$k$$ | +0.446 | 0.199 | 0.133 | +1.131 | 0.067 | 15 |
{: .scores }

{% include nomenclature-scores.md %}

</details>

- Normalisation: $$U$$, $$V$$, $$W$$ and $$k$$ at the 15 points over the tunnel\'s $$U_R$$ = 4.08 m/s on the measurement and over the solved speed at the reference mast on the model ($$U_R$$ is defined at the mast), $$k$$ over $$U_R^2$$; $$c^\ast = C/c_0$$ ($$c_0 = \dfrac{q}{U_R H_R^2}$$ = 132.5 ppm) against the model\'s $$c\thinspace U_R H_R^2/Q$$ ($$H_R$$ = 0.068 m x 600, $$Q = 1\thinspace\mathrm{kg/s}$$) for turbulent Schmidt number 0.3, with one detection limit of $$10^{-3}$$ of the largest measured value; hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units; the Schmidt numbers are three runs on one flow
- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseMContainerE2E (WD 180, the default) (TPU Atsugi campus, 1:600, tunnel WD 180, turbulent Schmidt number 0.3; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 1,394,053 cells, solved 2026-10-18); figures validation/plot\_cases\_fm\_openfoam.py

Notes:

- $$U_R$$ is the solved speed at the reference mast, 4.686 m/s, which is 1.19 of the tabulated inlet\'s speed at the mast\'s elevation (3.934 m/s) and 1.15 of the tunnel\'s 4.08 m/s. Over the imposed speed $$c^\ast$$ scores FB +1.48 and over 4.08 m/s FB +1.46, against +1.40 over the solved speed.
- Controls on the same solution: the points turned 180° about the source score R -0.05, FAC2 0.07, FB +2.00 (14 of the 15 lie in the fluid; the model\'s mean over those points is 7.3e-06 against 0.186 at the real ones), and the points mirrored across the plume axis score R +0.68, FAC2 0.47, FB +0.32 (the real points: R +0.41, FAC2 0.20, FB +1.40).
- Field campaign (18 runs): the 10 runs within 10° of 180 at 3 m/s or more, each with its own $$U_R$$ and q and $$H_R$$ = 41 m as the cleaned table states (the scores divide by 40.8 m, a 1 % difference). The model against the field\'s geometric mean scores R +0.46, FAC2 0.07, FB +1.01, and lies inside the field\'s minimum-maximum range at 2 of 15 points; the tunnel\'s WD 180 against the same mean scores R +0.98, FAC2 0.60, FB -0.59; the spread of the field at point 1 is a factor of 4.5.

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration sct05

Quantity: $$U$$, $$V$$, $$W$$ and $$k$$ at the 15 points of the tunnel\'s WD 180 run over the tunnel\'s $$U_R$$ = 4.08 m/s (measured) and over the solved speed at the reference mast (modelled; $$U_R$$ is defined at the mast), and the dimensionless concentration $$c^\ast = C/c_0$$ ($$c_0 = \dfrac{q}{U_R H_R^2}$$ = 132.5 ppm) against the model\'s $$c\thinspace U_R H_R^2/Q$$ for turbulent Schmidt number 0.5; the 18-run field campaign is compared as well.

<details markdown="block">
  <summary>All 16 headline scores</summary>

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$c^\ast$$ | +0.251 | 0.063 | 0.200 | +1.524 | 0.133 | 15 |
| $$c^\ast$$, over the imposed speed at the mast\'s height (3.934 m/s) | +0.251 | 0.063 | 0.133 | +1.592 | 0.067 | 15 |
| $$c^\ast$$, over the tunnel\'s $$U_R$$ = 4.08 m/s | +0.251 | 0.063 | 0.200 | +1.579 | 0.133 | 15 |
| $$c^\ast$$, points turned 180° about the source (control) | -0.058 | 0.003 | 0.071 | +2.000 | 0.071 | 14 |
| $$c^\ast$$, points mirrored across the plume axis (control) | +0.655 | 0.429 | 0.400 | +0.220 | 0.333 | 15 |
| $$c^\ast$$, tunnel WD 175 as a model of its WD 180 (control) | +0.932 | 0.868 | 0.733 | +0.401 | 0.267 | 15 |
| $$c^\ast$$, tunnel WD 185 as a model of its WD 180 (control) | +0.976 | 0.952 | 0.800 | -0.117 | 0.533 | 15 |
| $$c^\ast$$, mean of the tunnel\'s WD 175 and WD 185 as a model of its WD 180 (control) | +0.998 | 0.995 | 1.000 | +0.111 | 0.867 | 15 |
| $$c^\ast$$ against the field\'s geometric mean (10 runs) | +0.285 | 0.081 | 0.067 | +1.202 | 0.000 | 15 |
| $$c^\ast$$, tunnel WD 180 as a model of the field\'s geometric mean (control) | +0.984 | 0.969 | 0.600 | -0.593 | 0.000 | 15 |
| $$U$$ | +0.708 | 0.502 | 0.267 | +1.460 | 0.267 | 15 |
| $$V$$ | +0.731 | 0.534 | 0.333 | — | 0.133 | 15 |
| $$V$$, sign flipped (control) | -0.731 | 0.534 | 0.067 | -0.616 | 0.133 | 15 |
| $$W$$ | +0.181 | 0.033 | 0.267 | — | 0.733 | 15 |
| $$\lvert\mathbf{U}\rvert$$ | +0.601 | 0.362 | 0.733 | +0.185 | 0.400 | 15 |
| $$k$$ | +0.446 | 0.199 | 0.133 | +1.131 | 0.067 | 15 |
{: .scores }

{% include nomenclature-scores.md %}

</details>

- Normalisation: $$U$$, $$V$$, $$W$$ and $$k$$ at the 15 points over the tunnel\'s $$U_R$$ = 4.08 m/s on the measurement and over the solved speed at the reference mast on the model ($$U_R$$ is defined at the mast), $$k$$ over $$U_R^2$$; $$c^\ast = C/c_0$$ ($$c_0 = \dfrac{q}{U_R H_R^2}$$ = 132.5 ppm) against the model\'s $$c\thinspace U_R H_R^2/Q$$ ($$H_R$$ = 0.068 m x 600, $$Q = 1\thinspace\mathrm{kg/s}$$) for turbulent Schmidt number 0.5, with one detection limit of $$10^{-3}$$ of the largest measured value; hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units; the Schmidt numbers are three runs on one flow
- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseMContainerE2E (WD 180, the default) (TPU Atsugi campus, 1:600, tunnel WD 180, turbulent Schmidt number 0.5; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 1,394,053 cells, solved 2026-10-18); figures validation/plot\_cases\_fm\_openfoam.py

Notes:

- $$U_R$$ is the solved speed at the reference mast, 4.686 m/s, which is 1.19 of the tabulated inlet\'s speed at the mast\'s elevation (3.934 m/s) and 1.15 of the tunnel\'s 4.08 m/s. Over the imposed speed $$c^\ast$$ scores FB +1.59 and over 4.08 m/s FB +1.58, against +1.52 over the solved speed.
- Controls on the same solution: the points turned 180° about the source score R -0.06, FAC2 0.07, FB +2.00 (14 of the 15 lie in the fluid; the model\'s mean over those points is 9.2e-06 against 0.143 at the real ones), and the points mirrored across the plume axis score R +0.65, FAC2 0.40, FB +0.22 (the real points: R +0.25, FAC2 0.20, FB +1.52).
- Field campaign (18 runs): the 10 runs within 10° of 180 at 3 m/s or more, each with its own $$U_R$$ and q and $$H_R$$ = 41 m as the cleaned table states (the scores divide by 40.8 m, a 1 % difference). The model against the field\'s geometric mean scores R +0.28, FAC2 0.07, FB +1.20, and lies inside the field\'s minimum-maximum range at 2 of 15 points; the tunnel\'s WD 180 against the same mean scores R +0.98, FAC2 0.60, FB -0.59; the spread of the field at point 1 is a factor of 4.5.

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration sct07

Quantity: $$U$$, $$V$$, $$W$$ and $$k$$ at the 15 points of the tunnel\'s WD 180 run over the tunnel\'s $$U_R$$ = 4.08 m/s (measured) and over the solved speed at the reference mast (modelled; $$U_R$$ is defined at the mast), and the dimensionless concentration $$c^\ast = C/c_0$$ ($$c_0 = \dfrac{q}{U_R H_R^2}$$ = 132.5 ppm) against the model\'s $$c\thinspace U_R H_R^2/Q$$ for turbulent Schmidt number 0.7; the 18-run field campaign is compared as well.

<details markdown="block">
  <summary>All 16 headline scores</summary>

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$c^\ast$$ | +0.198 | 0.039 | 0.133 | +1.579 | 0.133 | 15 |
| $$c^\ast$$, over the imposed speed at the mast\'s height (3.934 m/s) | +0.198 | 0.039 | 0.133 | +1.640 | 0.067 | 15 |
| $$c^\ast$$, over the tunnel\'s $$U_R$$ = 4.08 m/s | +0.198 | 0.039 | 0.133 | +1.628 | 0.133 | 15 |
| $$c^\ast$$, points turned 180° about the source (control) | -0.058 | 0.003 | 0.071 | +2.000 | 0.071 | 14 |
| $$c^\ast$$, points mirrored across the plume axis (control) | +0.650 | 0.423 | 0.400 | +0.180 | 0.333 | 15 |
| $$c^\ast$$, tunnel WD 175 as a model of its WD 180 (control) | +0.932 | 0.868 | 0.733 | +0.401 | 0.267 | 15 |
| $$c^\ast$$, tunnel WD 185 as a model of its WD 180 (control) | +0.976 | 0.952 | 0.800 | -0.117 | 0.533 | 15 |
| $$c^\ast$$, mean of the tunnel\'s WD 175 and WD 185 as a model of its WD 180 (control) | +0.998 | 0.995 | 1.000 | +0.111 | 0.867 | 15 |
| $$c^\ast$$ against the field\'s geometric mean (10 runs) | +0.224 | 0.050 | 0.067 | +1.287 | 0.000 | 15 |
| $$c^\ast$$, tunnel WD 180 as a model of the field\'s geometric mean (control) | +0.984 | 0.969 | 0.600 | -0.593 | 0.000 | 15 |
| $$U$$ | +0.708 | 0.502 | 0.267 | +1.460 | 0.267 | 15 |
| $$V$$ | +0.731 | 0.534 | 0.333 | — | 0.133 | 15 |
| $$V$$, sign flipped (control) | -0.731 | 0.534 | 0.067 | -0.616 | 0.133 | 15 |
| $$W$$ | +0.181 | 0.033 | 0.267 | — | 0.733 | 15 |
| $$\lvert\mathbf{U}\rvert$$ | +0.601 | 0.362 | 0.733 | +0.185 | 0.400 | 15 |
| $$k$$ | +0.446 | 0.199 | 0.133 | +1.131 | 0.067 | 15 |
{: .scores }

{% include nomenclature-scores.md %}

</details>

- Normalisation: $$U$$, $$V$$, $$W$$ and $$k$$ at the 15 points over the tunnel\'s $$U_R$$ = 4.08 m/s on the measurement and over the solved speed at the reference mast on the model ($$U_R$$ is defined at the mast), $$k$$ over $$U_R^2$$; $$c^\ast = C/c_0$$ ($$c_0 = \dfrac{q}{U_R H_R^2}$$ = 132.5 ppm) against the model\'s $$c\thinspace U_R H_R^2/Q$$ ($$H_R$$ = 0.068 m x 600, $$Q = 1\thinspace\mathrm{kg/s}$$) for turbulent Schmidt number 0.7, with one detection limit of $$10^{-3}$$ of the largest measured value; hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units; the Schmidt numbers are three runs on one flow
- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseMContainerE2E (WD 180, the default) (TPU Atsugi campus, 1:600, tunnel WD 180, turbulent Schmidt number 0.7; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 1,394,053 cells, solved 2026-10-18); figures validation/plot\_cases\_fm\_openfoam.py

Notes:

- $$U_R$$ is the solved speed at the reference mast, 4.686 m/s, which is 1.19 of the tabulated inlet\'s speed at the mast\'s elevation (3.934 m/s) and 1.15 of the tunnel\'s 4.08 m/s. Over the imposed speed $$c^\ast$$ scores FB +1.64 and over 4.08 m/s FB +1.63, against +1.58 over the solved speed.
- Controls on the same solution: the points turned 180° about the source score R -0.06, FAC2 0.07, FB +2.00 (14 of the 15 lie in the fluid; the model\'s mean over those points is 1.0e-05 against 0.125 at the real ones), and the points mirrored across the plume axis score R +0.65, FAC2 0.40, FB +0.18 (the real points: R +0.20, FAC2 0.13, FB +1.58).
- Field campaign (18 runs): the 10 runs within 10° of 180 at 3 m/s or more, each with its own $$U_R$$ and q and $$H_R$$ = 41 m as the cleaned table states (the scores divide by 40.8 m, a 1 % difference). The model against the field\'s geometric mean scores R +0.22, FAC2 0.07, FB +1.29, and lies inside the field\'s minimum-maximum range at 2 of 15 points; the tunnel\'s WD 180 against the same mean scores R +0.98, FAC2 0.60, FB -0.59; the spread of the field at point 1 is a factor of 4.5.

## Not run

{% include validation/case-m/not-run.md %}

## Notes on every run

- Per-point values: [`/api/cases/M/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/M/pairs/openfoam12-realizableKE.csv' | relative_url }})

Notes:

- One heading and one steady solve: WD 180, the only heading with measured velocities. The tunnel\'s WD 175 scored as a model of its WD 180 gives R +0.93, FAC2 0.73, FB +0.40, its WD 185 R +0.98, FAC2 0.80, FB -0.12, and the mean of the two R +1.00, FAC2 1.00, FB +0.11; 8 of the 15 points change by more than a factor of two between WD 175 and WD 185 (computed from the pairs).
- The turbulent Schmidt number does not change the flow: the three runs of this case are one solve with three passive tracers, so $$U$$, $$V$$, $$W$$ and $$k$$ are the same in all three and only $$c^\ast$$ differs.
- Model set-up: a cylinder of 540 m radius and 240 m height on the terrain sheet; the tabulated approach profile over a smooth floor; no counterpart of the tunnel\'s side walls (at ±360 m) and 600 m ceiling (blockage 5 %). The 6 mm outlet is 3.6 m at 1:600; the source here is a 4 m cube on the ground (a zone of 20 cells, 2 m surface cells), 1 kg/s as a volume source with no exit momentum. The 15 points are 3 m above the ground.
- Mean $$c^\ast$$ over the three points nearest the source: 2.52 (tunnel), 0.26 / 0.11 / 0.05 (model, $$\mathrm{Sc_t}$$ 0.3 / 0.5 / 0.7); over the two far downwind points: 0.21 (tunnel), 0.11 / 0.10 / 0.09 (model). Peak $$c^\ast$$: 3.04 (tunnel), 1.27 / 1.37 / 1.38 (model); 3 / 3 / 3 of the five highest points are shared with the tunnel.
- The velocity at the 15 points: the mean $$U/U_R$$ is 0.026 modelled against 0.164 measured. FB is not defined for $$V$$ and $$W$$ (their means are not both positive); $$V$$ correlates at R +0.73 and flipping its sign gives -0.73.
- The solve ran to its 3000-iteration limit with the residualControl unmet (no \'solution converged\' line); the initial residuals at the last iteration were $$U_x$$ 6.1e-04, $$U_z$$ 6.9e-04, $$p$$ 1.0e-04, $$\varepsilon$$ 1.9e-02, $$k$$ 1.6e-04 and the tracers 8.1e-06 to 1.1e-05. checkMesh: Mesh OK. 1,394,053 cells. The tracer probe prints seven significant digits; a probe at six decimals moved no $$c^\ast$$ value by more than 0.003.

<details markdown="block">
<summary>Interpretation: Case M near-source ordering</summary>

The tunnel\'s three points nearest the source carry about 12 times its two far downwind ones; the modelled plume carries less, and $$\mathrm{Sc_t}$$ 0.7 reverses the order.

</details>

<details markdown="block">
<summary>Interpretation: Case M controls</summary>

The tracer goes downwind: the model\'s mean over the points turned 180° about the source is far below its mean at the real points. The mirrored points score above the real points because the modelled plume is displaced sideways against the tunnel\'s. The tunnel\'s neighbouring headings WD 175 and WD 185 are the noise floor of a single heading.

</details>

<details markdown="block">
  <summary>How the scores are computed</summary>

- Scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

</details>

## Leaderboard

| Rank | Run | Source | Hit rate, $$U$$ | Hit rate, $$V$$ | Hit rate, $$W$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate, $$k$$ | Hit rate, $$c^\ast$$ | Hit rate | FAC2 | R | $$R^2$$ | Points scored |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.3 | Eddy3D | **0.267** | **0.133** | **0.733** | **0.400** | **0.067** | **0.133** | **0.289** | **0.322** | **+0.513** | **0.300** | 100 % |
| 2 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.5 | Eddy3D | **0.267** | **0.133** | **0.733** | **0.400** | **0.067** | **0.133** | **0.289** | **0.322** | +0.487 | 0.282 | 100 % |
| 3 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.7 | Eddy3D | **0.267** | **0.133** | **0.733** | **0.400** | **0.067** | **0.133** | **0.289** | 0.311 | +0.478 | 0.278 | 100 % |
{: .scores }

{% include nomenclature-scores.md %}

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. *Points scored* is the share of the measured points a run gave values at. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
