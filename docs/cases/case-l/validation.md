---
title: "Validation"
parent: "Case L"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case L — 9 x 14 cube array, line source, non-isothermal: Eddy3D's scores against the measurements, engine by engine."
---

# Case L: validation
{: .no_toc }

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Engine status: OpenFOAM 12 (UMF) <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

## Measurement locations

{% include validation/case-l/layout.md %}

## Explore the points

{% include explorer.html case="L" %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-l/openfoam.md %}

### Scores

Quantity: $$U$$, $$V$$, $$W$$, the speed $$\lvert\mathbf{U}\rvert$$ over $$U_H$$ = 1.3394 m/s and $$k$$ over $$U_H^2$$ (the tunnel\'s units, 344 points); theta = ($$T_f - T$$)/($$T_f - T_H$$) with $$T_f$$ = 45.01 degC and $$T_f - T_H$$ = 30.26 K; $$c^\ast = C/c_0$$ ($$c_0$$ = 1728 ppm) against the model\'s ethylene mass fraction as ppm over the same $$c_0$$, for turbulent Schmidt numbers 0.3, 0.5 and 0.7; also the 242 points at or above 30 mm, the first four fine cells above the floor. The scene is the tunnel at Froude scale 100.

<details markdown="block">
  <summary>All 19 headline scores</summary>

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.918 | 0.843 | 0.608 | +0.268 | 0.506 | 344 |
| $$V$$ | -0.037 | 0.001 | 0.291 | -0.795 | 0.747 | 344 |
| $$W$$ | -0.027 | 0.001 | 0.183 | — | 0.762 | 344 |
| $$\lvert\mathbf{U}\rvert$$ | +0.898 | 0.807 | 0.674 | +0.206 | 0.515 | 344 |
| $$k$$ | +0.145 | 0.021 | 0.584 | +0.635 | 0.244 | 344 |
| $$\theta$$, floor-referenced temperature | +0.936 | 0.876 | 1.000 | +0.049 | 0.985 | 344 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.798 | 0.637 | 0.759 | -0.498 | 0.468 | 344 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.766 | 0.587 | 0.683 | -0.649 | 0.387 | 344 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.746 | 0.556 | 0.602 | -0.731 | 0.358 | 344 |
| $$U$$, points at or above 30 mm | +0.902 | 0.814 | 0.798 | +0.147 | 0.669 | 242 |
| $$k$$, points at or above 30 mm | +0.468 | 0.219 | 0.802 | +0.364 | 0.343 | 242 |
| $$\theta$$, points at or above 30 mm | +0.944 | 0.892 | 1.000 | +0.041 | 1.000 | 242 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, points at or above 30 mm | +0.814 | 0.663 | 0.715 | -0.495 | 0.430 | 242 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, points at or above 30 mm | +0.821 | 0.675 | 0.636 | -0.583 | 0.351 | 242 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, points at or above 30 mm | +0.816 | 0.667 | 0.541 | -0.624 | 0.302 | 242 |
| $$V$$, lateral sign flipped (control) | +0.037 | 0.001 | 0.110 | — | 0.695 | 344 |
| $$U$$, approach column alone (control) | +0.861 | 0.741 | 0.846 | -0.205 | 0.599 | 344 |
| $$\theta$$, approach column alone (control) | +0.925 | 0.856 | 1.000 | -0.117 | 0.837 | 344 |
| $$U$$, y-symmetric ceiling (control) | +0.984 | 0.968 | 0.986 | +0.000 | 0.860 | 292 |
{: .scores }

{% include nomenclature-scores.md %}

</details>

- Normalisation: the tunnel\'s units: velocities by $$U_H$$ (1.3394 m/s measured, the Froude-scaled 13.39 m/s modelled), $$k$$ by $$U_H^2$$, temperature as theta = ($$T_f - T$$)/($$T_f - T_H$$) ($$T_f$$ = 45.01 degC, $$T_f - T_H$$ = 30.26 K), $$c^\ast = C/c_0$$ ($$c_0$$ = 1728 ppm) against the modelled ethylene mass fraction as ppm over the same $$c_0$$; hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units, concentration with one detection limit of $$10^{-3}$$ of the largest measured value
- Per-point values: [`/api/cases/L/pairs/umf-realizableKE.csv`]({{ '/api/cases/L/pairs/umf-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture MetaFOAM.Lib.Tests/TestAijCaseLUmfContainerE2E (9 x 14 cubes, heated floor, floor line source; urbanMicroclimateFoam, realizable k-ε, 754,940 air cells at Froude scale 100, 1500 air iterations, solved 2026-10-18); figures validation/plot\_cases\_jl\_umf.py

Notes:

- The scene is the tunnel at Froude scale 100 (lengths times 100, velocities times 10, temperatures unchanged), which keeps the bulk Richardson number (-0.034) and the tunnel\'s Kelvin values and does not keep Re.
- What the model does not represent: the gas\'s own heat and the buried slot (a mass rate into 624 whole cells, a strip 3 m wide), the tunnel\'s near-floor temperature drop (below the first cell), the measured velocity profile (UMF\'s inlet is a log law), the tunnel\'s no-slip side walls and ceiling (slip here), radiation (emissivity 0.01, effectively off) and the 10 mm raised block floor.
- 51 of the 344 points ($$z = 4\thinspace\mathrm{mm}$$, 0.4 m here) lie inside the first fine cell (0.75 m), a wall-function cell. The 242 points at or above 30 mm are scored separately.
- The street air is nearly stagnant in the model: the mean $$U/U_H$$ in the streets is 0.045 below 30 mm and 1.11 above 110 mm, against the tunnel\'s 0.297 and 1.068; the model\'s approach column differs from the tunnel\'s AF profile by up to 39 % above 30 mm (UMF\'s inlet is a log law, the tunnel\'s profile is not).
- The tracer is solved steady beside the flow, as three species of one flow. The outlet carried 0.86, 0.73 and 0.70 of the emission for $$\mathrm{Sc_t}$$ 0.3, 0.5 and 0.7, within the factor of two accepted as a check on the wiring. The largest modelled $$c^\ast$$ over the 344 points is in the source street for every species, at $$y = -0.12\thinspace\mathrm{m}$$ ($$\mathrm{Sc_t}$$ 0.3) and $$y = +0.18\thinspace\mathrm{m}$$ ($$\mathrm{Sc_t}$$ 0.5 and 0.7), against the tunnel\'s 1.929 at (-0.15, -0.12, 0.004).
- The air region ended at its 1500-iteration cap with the residualControl unmet (no \'solution converged\' line); at the last iteration the initial residuals were 2.6e-2 ($$U_y$$), 3.0e-2 (`p_rgh`) and 1.1e-3 to 2.0e-3 (the tracers).
- The tunnel is not y-symmetric although the array is: over 110 mirror pairs the mean \|U(y) - $$U$$(-y)\| is 0.143 $$U_H$$ in the tunnel and 0.058 $$U_H$$ in the model. $$V$$ is barely antisymmetric in the tunnel, so it cannot be scored as a pattern; the sign-flipped control shows what a wrong sign scores.
- The inlet\'s $$U_H$$ reaches the array within 20 %; the approach air is warmest at the floor; the street air near the floor is warmer than the approach air at H and cools with height; the street flow is slower than the flow above the array; every species emits and its largest value is in the source street.

## Not run

{% include validation/case-l/not-run.md %}

<details markdown="block">
  <summary>How the scores are computed</summary>

- Scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

</details>

## Leaderboard

| Rank | Run | Source | Hit rate, $$U$$ | Hit rate, $$V$$ | Hit rate, $$W$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate, $$k$$ | Hit rate, $$c^\ast$$ | Hit rate, $$\theta$$ | Hit rate | FAC2 | R | $$R^2$$ | Points scored |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM 12 (UMF) · $$\mathrm{Sc_t}$$ 0.3 | Eddy3D | **0.506** | **0.747** | **0.762** | **0.515** | **0.244** | **0.468** | **0.985** | **0.604** | **0.586** | **+0.519** | **0.455** | 100 % |
| 2 | OpenFOAM 12 (UMF) · $$\mathrm{Sc_t}$$ 0.5 | Eddy3D | **0.506** | **0.747** | **0.762** | **0.515** | **0.244** | 0.387 | **0.985** | 0.592 | 0.575 | +0.514 | 0.448 | 100 % |
| 3 | OpenFOAM 12 (UMF) · $$\mathrm{Sc_t}$$ 0.7 | Eddy3D | **0.506** | **0.747** | **0.762** | **0.515** | **0.244** | 0.358 | **0.985** | 0.588 | 0.563 | +0.511 | 0.444 | 100 % |
{: .scores }

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. *Points scored* is the share of the measured points a run gave values at. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
