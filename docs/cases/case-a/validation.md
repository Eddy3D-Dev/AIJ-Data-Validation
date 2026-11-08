---
title: "Validation"
parent: "Case A"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case A — 1:1:2 building: Eddy3D's scores against the measurements, engine by engine."
redirect_from:
  - /validation/cases-ab/
---

# Case A: validation
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

{% include validation/case-a/layout.md %}

## Explore the points

{% include explorer.html case="A" %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-a/openfoam.md %}

### Scores

Reattachment length $$L_r/H$$ = 1.49.

| Score | Run | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|---|
| $$U$$ | RANS | +0.955 | 0.912 | 0.817 | +0.185 | 0.586 |
|  | URANS | +0.953 | 0.908 | 0.763 | +0.181 | 0.683 |
| $$V$$ | RANS | +0.961 | 0.923 | 0.349 | -0.207 | 0.892 |
|  | URANS | +0.953 | 0.909 | 0.360 | — | 0.817 |
| $$W$$ | RANS | +0.708 | 0.502 | 0.398 | -1.501 | 0.801 |
|  | URANS | +0.675 | 0.456 | 0.414 | -1.352 | 0.699 |
| $$k$$ | RANS | +0.480 | 0.230 | 0.667 | +0.478 | 0.177 |
|  | URANS | +0.626 | 0.392 | 0.694 | +0.453 | 0.392 |
{: .scores }

Every score is over the same 186 points.

- Per-point values: [`/api/cases/A/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/A/pairs/openfoam12-realizableKE.csv' | relative_url }})
- RANS: realizable k-ε, log-law inlet (the served run). URANS: SST k-ω run transient, measured inlet, the submission [`eddy3d-of12-sst-urans`]({{ '/community/eddy3d-of12-sst-urans/' | relative_url }}), scores [`/api/submissions/eddy3d-of12-sst-urans.json`]({{ '/api/submissions/eddy3d-of12-sst-urans.json' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseAContainerE2E; figures validation/plot\_cases\_ab\_openfoam.py

## OpenLB

Status: <span class="label label-green status">scored</span>

{% include validation/case-a/openlb.md %}

### Scores

Reattachment length $$L_r/H$$ = 2.80.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.782 | 0.611 | 0.468 | +0.378 | 0.376 | 186 |
| $$U$$, points ≥ 2 dx | +0.800 | 0.640 | 0.653 | +0.219 | 0.562 | 121 |
| $$V$$ | +0.767 | 0.588 | 0.253 | -0.162 | 0.661 | 186 |
| $$W$$ | +0.574 | 0.329 | 0.177 | -1.711 | 0.559 | 186 |
| $$k$$ (resolved) | +0.162 | 0.026 | 0.000 | +1.958 | 0.000 | 186 |
| $$V$$, lateral sign flipped (control) | -0.767 | 0.588 | 0.124 | -24.677 | 0.554 | 186 |
{: .scores }

- Per-point values: [`/api/cases/A/pairs/openlb.csv`]({{ '/api/cases/A/pairs/openlb.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseAOpenLbContainerE2E (OpenLB eddy3dWind, image 1.9.3-r6, CPU build, $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$); figure validation/plot\_cases\_ab\_engines.py

## FluidX3D

Status: <span class="label label-green status">scored</span>

{% include validation/case-a/fluidx3d.md %}

### Scores

Reattachment length $$L_r/H$$ = 0.05.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$, comparable heights | +0.840 | 0.705 | 0.603 | +0.405 | 0.569 | 116 |
| $$V$$, comparable heights | +0.845 | 0.714 | 0.259 | -0.692 | 0.750 | 116 |
| $$W$$, comparable heights | +0.591 | 0.349 | 0.224 | -1.678 | 0.414 | 116 |
| $$U$$, all points | +0.806 | 0.650 | 0.597 | +0.372 | 0.452 | 186 |
| $$U$$, approach flow alone (control) | +0.510 | 0.260 | 0.767 | -0.256 | 0.586 | 116 |
{: .scores }

- Per-point values: [`/api/cases/A/pairs/fluidx3d.csv`]({{ '/api/cases/A/pairs/fluidx3d.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseAFluidX3DE2E (Eddy3DCli.Tests/Validation/TestAijVelocityFluidX3DE2E; FluidX3D GPU lattice Boltzmann, D3Q19 Smagorinsky LES, $$\mathrm{d}x = H/64$$, 40 + 200 $$H/U_H$$ spin-up + averaging, with an empty-domain control on the same lattice); figure validation/plot\_cases\_ab\_engines.py

## ML surrogate

Status: <span class="label label-green status">scored</span>

{% include validation/case-a/ml-surrogate.md %}

### Scores

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate |
|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert$$ ($$z = 0.01\thinspace\mathrm{m}$$ plane) | -0.125 | 0.016 | 0.262 | +0.772 | 0.092 |
| $$\lvert\mathbf{U}\rvert$$, lattice cut at ±250 m | +0.434 | 0.188 | 0.615 | +0.401 | 0.338 |
| wind reversed (control) | -0.125 | 0.016 | 0.262 | +0.772 | 0.092 |
{: .scores }

Every score is over the same 65 points.

- Per-point values: [`/api/cases/A/pairs/ml-surrogate.csv`]({{ '/api/cases/A/pairs/ml-surrogate.csv' | relative_url }})
- Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py

## Grid uncertainty

{% include validation/case-a/grid.md %}

## Notes on every run

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

## Leaderboard

| Rank | Run | Source | Hit rate, $$U$$ | Hit rate, $$V$$ | Hit rate, $$W$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate | FAC2 | R | $$R^2$$ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-mesh2x-measured-inlet]({{ '/community/eddy3d-of12-mesh2x-measured-inlet/' | relative_url }})) | community | 0.651 | 0.887 | **0.833** | 0.677 | **0.762** | 0.603 | **+0.900** | **0.819** |
| 2 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-nutcap-lifted]({{ '/community/eddy3d-of12-nutcap-lifted/' | relative_url }})) | community | 0.613 | **0.903** | **0.833** | 0.667 | 0.754 | **0.613** | +0.891 | 0.805 |
| 3 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-measured-inlet]({{ '/community/eddy3d-of12-measured-inlet/' | relative_url }})) | community | 0.624 | 0.876 | 0.828 | 0.667 | 0.749 | 0.610 | +0.894 | 0.810 |
| 4 | OpenFOAM pimpleFoam (Eddy3D Outdoor case writer) ([eddy3d-of12-sst-urans]({{ '/community/eddy3d-of12-sst-urans/' | relative_url }})) | community | **0.683** | 0.817 | 0.699 | **0.720** | 0.730 | 0.590 | +0.877 | 0.782 |
| 5 | OpenFOAM 12 | Eddy3D | 0.586 | 0.892 | 0.801 | 0.634 | 0.728 | 0.610 | +0.891 | 0.805 |
| 6 | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) ([example-openfoam12]({{ '/community/example-openfoam12/' | relative_url }})) | example submission | 0.586 | 0.892 | 0.801 | 0.634 | 0.728 | 0.610 | +0.891 | 0.805 |
| 7 | FluidX3D | Eddy3D | 0.452 | 0.618 | 0.441 | 0.554 | 0.516 | 0.462 | +0.717 | 0.546 |
| 8 | OpenLB | Eddy3D | 0.376 | 0.661 | 0.559 | 0.409 | 0.501 | 0.353 | +0.728 | 0.538 |
{: .scores }

All runs scored by `validation/score_submissions.py`. Ranked by mean hit rate (VDI 3783) over the tasks; bold: best per column. Not ranked: the ML surrogate (no point ids) and negative controls. Community rows are self-reported ([Validate your own solver]({{ '/byos/' | relative_url }})).
