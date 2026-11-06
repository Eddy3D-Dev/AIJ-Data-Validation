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

{% include nomenclature.md %}

## Measurement locations

{% include validation/case-b/layout.md %}

## Explore the points

{% include explorer.html case="B" %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-b/openfoam.md %}

### Scores

Reattachment length $$L_r/H$$ = 3.27.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| $$U$$ | +0.959 | 0.920 | 0.701 | +0.240 | 0.562 |
| $$V$$ | +0.910 | 0.828 | 0.281 | +0.370 | 0.612 |
| $$W$$ | +0.929 | 0.863 | 0.536 | +0.263 | 0.808 |
| $$k$$ | +0.399 | 0.159 | 0.562 | +0.463 | 0.223 |
{: .scores }

Every score is over the same 224 points.

- Per-point values: [`/api/cases/B/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/B/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseBContainerE2E; figures validation/plot\_cases\_ab\_openfoam.py

## OpenLB

Status: <span class="label label-green status">scored</span>

{% include validation/case-b/openlb.md %}

### Scores

Reattachment length $$L_r/H$$ = 2.63.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.849 | 0.721 | 0.424 | +0.220 | 0.277 | 224 |
| $$U$$, points ≥ 2 dx | +0.929 | 0.864 | 0.611 | -0.001 | 0.526 | 95 |
| $$V$$ | +0.869 | 0.755 | 0.214 | +1.046 | 0.594 | 224 |
| $$W$$ | +0.796 | 0.634 | 0.321 | +0.549 | 0.701 | 224 |
| $$k$$ (resolved) | +0.449 | 0.202 | 0.049 | +1.533 | 0.018 | 224 |
| $$V$$, lateral sign flipped (control) | -0.869 | 0.755 | 0.179 | +3.823 | 0.509 | 224 |
{: .scores }

- Per-point values: [`/api/cases/B/pairs/openlb.csv`]({{ '/api/cases/B/pairs/openlb.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseBOpenLbContainerE2E (OpenLB eddy3dWind, image 1.9.3-r6, CPU build, $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$); figure validation/plot\_cases\_ab\_engines.py

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

- Per-point values: [`/api/cases/B/pairs/fluidx3d.csv`]({{ '/api/cases/B/pairs/fluidx3d.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseBFluidX3DE2E (Eddy3DCli.Tests/Validation/TestAijVelocityFluidX3DE2E; FluidX3D GPU lattice Boltzmann, D3Q19 Smagorinsky LES, $$\mathrm{d}x = H/64$$, 100 + 500 $$H/U_H$$ spin-up + averaging, with an empty-domain control on the same lattice); figure validation/plot\_cases\_ab\_engines.py

## ML surrogate

Status: <span class="label label-green status">scored</span>

{% include validation/case-b/ml-surrogate.md %}

### Scores

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert$$ ($$z = H/16$$ plane) | -0.236 | 0.055 | 0.361 | +0.821 | 0.172 |
| $$\lvert\mathbf{U}\rvert$$, lattice cut at ±250 m | +0.010 | 0.000 | 0.459 | +0.463 | 0.189 |
| wind reversed (control) | -0.236 | 0.055 | 0.361 | +0.821 | 0.172 |
{: .scores }

Every score is over the same 122 points.

- Per-point values: [`/api/cases/B/pairs/ml-surrogate.csv`]({{ '/api/cases/B/pairs/ml-surrogate.csv' | relative_url }})
- Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py

## Notes on every run

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

## Leaderboard

| Rank | Run | Source | Hit rate, $$U$$ | Hit rate, $$V$$ | Hit rate, $$W$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate | FAC2 | R | $$R^2$$ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-measured-inlet]({{ '/community/eddy3d-of12-measured-inlet/' | relative_url }})) | community | **0.571** | 0.607 | **0.821** | 0.625 | **0.656** | 0.578 | **+0.936** | **0.876** |
| 2 | OpenFOAM 12 | Eddy3D | 0.562 | 0.612 | 0.808 | 0.625 | 0.652 | **0.585** | **+0.936** | **0.876** |
| 3 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-nutcap-lifted]({{ '/community/eddy3d-of12-nutcap-lifted/' | relative_url }})) | community | 0.540 | **0.638** | 0.723 | **0.634** | 0.634 | 0.580 | +0.934 | 0.872 |
| 4 | FluidX3D | Eddy3D | 0.411 | 0.545 | 0.527 | 0.424 | 0.477 | 0.491 | +0.875 | 0.766 |
| 5 | OpenLB | Eddy3D | 0.277 | 0.594 | 0.701 | 0.321 | 0.473 | 0.376 | +0.837 | 0.701 |
{: .scores }

All runs scored by `validation/score_submissions.py`. Ranked by mean hit rate (VDI 3783) over the tasks; bold: best per column. Not ranked: the ML surrogate (no point ids) and negative controls. Community rows are self-reported ([Validate your own solver]({{ '/byos/' | relative_url }})).
