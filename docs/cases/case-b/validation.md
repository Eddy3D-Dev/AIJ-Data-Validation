---
title: "Validation"
parent: "Case B"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case B — 1:4:4 slab: Eddy3D's scores against the measurements, engine by engine."
---

# Case B: validation
{: .no_toc }

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-green status">scored</span> · FluidX3D <span class="label label-green status">scored</span> · ML surrogate <span class="label label-green status">scored</span>

## Measurement locations

{% include validation/case-b/layout.md %}

## Explore the points

{% include explorer.html case="B" %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-b/openfoam.md %}

### Scores

Reattachment length $$L_r/H$$ = 3.27.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.959 | 0.920 | 0.701 | +0.240 | 0.562 | 224 |
| $$V$$ | +0.910 | 0.828 | 0.281 | +0.370 | 0.612 | 224 |
| $$W$$ | +0.929 | 0.863 | 0.536 | +0.263 | 0.808 | 224 |
| $$k$$ | +0.399 | 0.159 | 0.562 | +0.463 | 0.223 | 224 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/B/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/B/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseBContainerE2E; figures validation/plot\_cases\_ab\_openfoam.py

## OpenLB

Status: <span class="label label-green status">scored</span>

{% include validation/case-b/openlb.md %}

### Scores

Reattachment length $$L_r/H$$ = 2.71.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.790 | 0.625 | 0.375 | +0.280 | 0.290 | 224 |
| $$U$$, points ≥ 2 dx | +0.900 | 0.810 | 0.642 | -0.072 | 0.516 | 95 |
| $$V$$ | +0.831 | 0.691 | 0.129 | +1.392 | 0.549 | 224 |
| $$W$$ | +0.774 | 0.599 | 0.237 | +0.376 | 0.652 | 224 |
| $$k$$ (resolved) | +0.486 | 0.236 | 0.045 | +1.641 | 0.004 | 224 |
| $$V$$, lateral sign flipped (control) | -0.831 | 0.691 | 0.138 | +2.873 | 0.491 | 224 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/B/pairs/openlb.csv`]({{ '/api/cases/B/pairs/openlb.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseBOpenLbContainerE2E (OpenLB eddy3dWind, CPU image, $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$); figure validation/plot\_cases\_ab\_engines.py

## FluidX3D

Status: <span class="label label-green status">scored</span>

{% include validation/case-b/fluidx3d.md %}

### Scores

Reattachment length $$L_r/H$$ = 2.63.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$, comparable heights | +0.947 | 0.896 | 0.636 | +0.260 | 0.568 | 88 |
| $$W$$, comparable heights | +0.845 | 0.714 | 0.477 | +0.114 | 0.318 | 88 |
| $$U$$, all points | +0.905 | 0.820 | 0.638 | +0.172 | 0.411 | 224 |
| $$U$$, approach flow alone (control) | +0.807 | 0.651 | 0.557 | -0.541 | 0.398 | 88 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/B/pairs/fluidx3d.csv`]({{ '/api/cases/B/pairs/fluidx3d.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseBFluidX3DE2E (Eddy3DCli.Tests/Validation/TestAijVelocityFluidX3DE2E; FluidX3D GPU lattice Boltzmann, D3Q19 Smagorinsky LES, $$\mathrm{d}x = H/64$$, 100 + 500 $$H/U_H$$ spin-up + averaging, with an empty-domain control on the same lattice); figure validation/plot\_cases\_ab\_engines.py

## ML surrogate

Status: <span class="label label-green status">scored</span>

{% include validation/case-b/ml-surrogate.md %}

### Scores

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert$$ ($$z = H/16$$ plane) | -0.236 | 0.055 | 0.361 | +0.821 | 0.172 | 122 |
| $$\lvert\mathbf{U}\rvert$$, lattice cut at ±250 m | +0.010 | 0.000 | 0.459 | +0.463 | 0.189 | 122 |
| wind reversed (control) | -0.236 | 0.055 | 0.361 | +0.821 | 0.172 | 122 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/B/pairs/ml-surrogate.csv`]({{ '/api/cases/B/pairs/ml-surrogate.csv' | relative_url }})
- Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py

## Notes on every run

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

## Leaderboard

| Rank | Run | Source | Hit rate, $$U$$ | Hit rate, $$V$$ | Hit rate, $$W$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate | FAC2 | R | $$R^2$$ | Points scored |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-measured-inlet]({{ '/community/eddy3d-of12-measured-inlet/' | relative_url }})) | community | **0.571** | 0.607 | **0.821** | **0.625** | **0.656** | 0.578 | **+0.936** | **0.876** | 100 % |
| 2 | OpenFOAM 12 | Eddy3D | 0.562 | **0.612** | 0.808 | **0.625** | 0.652 | **0.585** | **+0.936** | **0.876** | 100 % |
| 3 | FluidX3D | Eddy3D | 0.411 | 0.545 | 0.527 | 0.424 | 0.477 | 0.491 | +0.875 | 0.766 | 100 % |
| 4 | OpenLB | Eddy3D | 0.290 | 0.549 | 0.652 | 0.317 | 0.452 | 0.297 | +0.792 | 0.628 | 100 % |
{: .scores }

{% include nomenclature-scores.md %}

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. *Points scored* is the share of the measured points a run gave values at. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
