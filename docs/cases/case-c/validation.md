---
title: "Validation"
parent: "Case C"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case C — 3 × 3 block array: Eddy3D's scores against the measurements, engine by engine."
redirect_from:
  - /validation/case-c/
---

# Case C: validation
{: .no_toc }

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-grey status">not comparable</span> · FluidX3D <span class="label label-grey status">not comparable</span> · ML surrogate <span class="label label-green status">scored</span>

{% include nomenclature.md %}

## Measurement locations

{% include validation/case-c/layout.md %}

## Explore the points

{% include explorer.html case="C" %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-c/openfoam.md %}

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration 0D

Quantity: $$V_{\mathrm{s}}$$ (thermistor) scored against $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ \[scalar\] and $$\lvert\mathbf{U}\rvert$$ \[vector\]; both normalised by $$U_H$$ = $$U(z = D)$$ = 3.654 m/s.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| WD 0° $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.824 | 0.679 | 0.908 | +0.266 | 0.567 |
| WD 0° $$\lvert\mathbf{U}\rvert$$ | +0.804 | 0.647 | 0.658 | +0.466 | 0.308 |
| WD 22.5° $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.857 | 0.735 | 0.983 | +0.106 | 0.750 |
| WD 22.5° $$\lvert\mathbf{U}\rvert$$ | +0.846 | 0.715 | 0.833 | +0.295 | 0.433 |
| WD 45° $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.831 | 0.690 | 0.942 | +0.121 | 0.783 |
| WD 45° $$\lvert\mathbf{U}\rvert$$ | +0.801 | 0.642 | 0.800 | +0.307 | 0.533 |
{: .scores }

Every score is over the same 120 points.

- Per-point values: [`/api/cases/C/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/C/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseC0DContainerE2E; figures validation/plot\_case\_c\_openfoam.py

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration 1D

Quantity: $$V_{\mathrm{s}}$$ (thermistor) scored against $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ \[scalar\] and $$\lvert\mathbf{U}\rvert$$ \[vector\]; both normalised by $$U_H$$ = $$U(z = D)$$ = 3.654 m/s.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| WD 0° $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.801 | 0.642 | 0.858 | +0.341 | 0.433 |
| WD 0° $$\lvert\mathbf{U}\rvert$$ | +0.741 | 0.549 | 0.550 | +0.551 | 0.292 |
| WD 22.5° $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.896 | 0.804 | 0.975 | +0.192 | 0.675 |
| WD 22.5° $$\lvert\mathbf{U}\rvert$$ | +0.882 | 0.777 | 0.725 | +0.394 | 0.367 |
| WD 45° $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.872 | 0.760 | 0.942 | +0.198 | 0.733 |
| WD 45° $$\lvert\mathbf{U}\rvert$$ | +0.873 | 0.761 | 0.850 | +0.353 | 0.433 |
{: .scores }

Every score is over the same 120 points.

- Per-point values: [`/api/cases/C/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/C/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseC1DContainerE2E; figures validation/plot\_case\_c\_openfoam.py

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration 2D

Quantity: $$V_{\mathrm{s}}$$ (thermistor) scored against $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ \[scalar\] and $$\lvert\mathbf{U}\rvert$$ \[vector\]; both normalised by $$U_H$$ = $$U(z = D)$$ = 3.654 m/s.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| WD 0° $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.857 | 0.734 | 0.850 | +0.251 | 0.492 |
| WD 0° $$\lvert\mathbf{U}\rvert$$ | +0.848 | 0.720 | 0.692 | +0.443 | 0.317 |
| WD 22.5° $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.906 | 0.820 | 0.983 | +0.091 | 0.875 |
| WD 22.5° $$\lvert\mathbf{U}\rvert$$ | +0.894 | 0.799 | 0.900 | +0.240 | 0.633 |
| WD 45° $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.909 | 0.826 | 0.958 | +0.103 | 0.883 |
| WD 45° $$\lvert\mathbf{U}\rvert$$ | +0.912 | 0.832 | 0.900 | +0.243 | 0.608 |
{: .scores }

Every score is over the same 120 points.

- Per-point values: [`/api/cases/C/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/C/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseC2DContainerE2E; figures validation/plot\_case\_c\_openfoam.py

## OpenLB

Status: <span class="label label-grey status">not comparable</span>

{% include validation/case-c/openlb.md %}

## FluidX3D

Status: <span class="label label-grey status">not comparable</span>

{% include validation/case-c/fluidx3d.md %}

## ML surrogate

Status: <span class="label label-green status">scored</span>

{% include validation/case-c/ml-surrogate.md %}

### Scores

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$V_{\mathrm{s}}$$, 9 configurations | +0.212 | 0.045 | 0.444 | +0.666 | 0.181 | 1080 |
| $$V_{\mathrm{s}}$$, 2D WD 0, lattice cut at ±250 m | +0.075 | 0.006 | 0.875 | +0.192 | 0.400 | 120 |
| wind reversed (control) | -0.441 | 0.194 | 0.725 | +0.367 | 0.392 | 120 |
{: .scores }

- Per-point values: [`/api/cases/C/pairs/ml-surrogate.csv`]({{ '/api/cases/C/pairs/ml-surrogate.csv' | relative_url }})
- Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py

## Notes on every run

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

## Leaderboard

| Rank | Run | Source | Hit rate, $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate | FAC2 | R | $$R^2$$ |
|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-nutcap-lifted]({{ '/community/eddy3d-of12-nutcap-lifted/' | relative_url }})) | community | **0.700** | 0.431 | **0.565** | 0.847 | **+0.858** | **0.739** |
| 2 | OpenFOAM 12 | Eddy3D | 0.688 | **0.436** | 0.562 | **0.850** | +0.853 | 0.730 |
{: .scores }

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. Every run gave values at every measured point. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
