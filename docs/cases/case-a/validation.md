---
title: "Validation"
parent: "Case A — 1:1:2 building"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case A — 1:1:2 building: Eddy3D's scores against the measurements, by engine."
redirect_from:
  - /validation/cases-ab/
---

# Case A: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-green status">scored</span> · FluidX3D <span class="label label-green status">scored</span> · ML surrogate <span class="label label-green status">scored</span>

{% include validation/case-a.md %}

## Scores, run by run

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor)

Reattachment length $$L_r/H$$ = 1.49.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.955 | 0.817 | +0.185 | 0.586 | 186 |
| $$V$$ | +0.961 | 0.349 | -0.207 | 0.892 | 186 |
| $$W$$ | +0.708 | 0.398 | -1.501 | 0.801 | 186 |
| $$k$$ | +0.480 | 0.667 | +0.478 | 0.177 | 186 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/A/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/A/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseAContainerE2E; figures validation/plot\_cases\_ab\_openfoam.py

### OpenLB (Eddy3D LBM)

Reattachment length $$L_r/H$$ = 3.39.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.758 | 0.425 | +0.395 | 0.371 | 186 |
| $$U$$, points ≥ 2 dx | +0.812 | 0.645 | +0.169 | 0.562 | 121 |
| $$V$$ | +0.646 | 0.172 | +0.041 | 0.624 | 186 |
| $$W$$ | +0.540 | 0.124 | -1.759 | 0.586 | 186 |
| $$k$$ (resolved) | +0.200 | 0.000 | +1.971 | 0.000 | 186 |
| $$V$$, lateral sign flipped (control) | -0.646 | 0.118 | +98.234 | 0.570 | 186 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/A/pairs/openlb.csv`]({{ '/api/cases/A/pairs/openlb.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseAOpenLbContainerE2E (OpenLB eddy3dWind, CPU image, $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$); figure validation/plot\_cases\_ab\_engines.py

### FluidX3D (Eddy3D GPU LBM)

Reattachment length $$L_r/H$$ = 0.05.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$, comparable heights | +0.840 | 0.603 | +0.405 | 0.569 | 116 |
| $$V$$, comparable heights | +0.845 | 0.259 | -0.692 | 0.750 | 116 |
| $$W$$, comparable heights | +0.591 | 0.224 | -1.678 | 0.414 | 116 |
| $$U$$, all points | +0.806 | 0.597 | +0.372 | 0.452 | 186 |
| $$U$$, approach flow alone (control) | +0.510 | 0.767 | -0.256 | 0.586 | 116 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/A/pairs/fluidx3d.csv`]({{ '/api/cases/A/pairs/fluidx3d.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseAFluidX3DE2E (Eddy3DCli.Tests/Validation/TestAijVelocityFluidX3DE2E; FluidX3D GPU lattice Boltzmann, D3Q19 Smagorinsky LES, $$\mathrm{d}x = H/64$$, 40 + 200 $$H/U_H$$ spin-up + averaging, with an empty-domain control on the same lattice); figure validation/plot\_cases\_ab\_engines.py

### Eddy3D ML wind surrogate (pedestrian height)

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert$$ ($$z = 0.01\thinspace\mathrm{m}$$ plane) | -0.125 | 0.262 | +0.772 | 0.092 | 65 |
| $$\lvert\mathbf{U}\rvert$$, lattice cut at ±250 m | +0.434 | 0.615 | +0.401 | 0.338 | 65 |
| wind reversed (control) | -0.125 | 0.262 | +0.772 | 0.092 | 65 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/A/pairs/ml-surrogate.csv`]({{ '/api/cases/A/pairs/ml-surrogate.csv' | relative_url }})
- Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py

### All runs

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

## Figures

Figures: [OpenLB and FluidX3D]({{ '/validation/engines/' | relative_url }}); [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}).
