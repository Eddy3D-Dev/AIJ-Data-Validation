---
title: "Validation"
parent: "Case B — 1:4:4 slab"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case B — 1:4:4 slab: Eddy3D's scores against the measurements, by engine."
---

# Case B: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-green status">scored</span> · FluidX3D <span class="label label-green status">scored</span> · ML surrogate <span class="label label-green status">scored</span>

{% include validation/case-b.md %}

## Scores, run by run

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor)

Reattachment length $$L_r/H$$ = 3.27.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.959 | 0.701 | +0.240 | 0.562 | 224 |
| $$V$$ | +0.910 | 0.281 | +0.370 | 0.612 | 224 |
| $$W$$ | +0.929 | 0.536 | +0.263 | 0.808 | 224 |
| $$k$$ | +0.399 | 0.562 | +0.463 | 0.223 | 224 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/B/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/B/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseBContainerE2E; figures validation/plot\_cases\_ab\_openfoam.py

### OpenLB (Eddy3D LBM)

Reattachment length $$L_r/H$$ = 2.71.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.790 | 0.375 | +0.280 | 0.290 | 224 |
| $$U$$, points ≥ 2 dx | +0.900 | 0.642 | -0.072 | 0.516 | 95 |
| $$V$$ | +0.831 | 0.129 | +1.392 | 0.549 | 224 |
| $$W$$ | +0.774 | 0.237 | +0.376 | 0.652 | 224 |
| $$k$$ (resolved) | +0.486 | 0.045 | +1.641 | 0.004 | 224 |
| $$V$$, lateral sign flipped (control) | -0.831 | 0.138 | +2.873 | 0.491 | 224 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/B/pairs/openlb.csv`]({{ '/api/cases/B/pairs/openlb.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseBOpenLbContainerE2E (OpenLB eddy3dWind, CPU image, $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$); figure validation/plot\_cases\_ab\_engines.py

### FluidX3D (Eddy3D GPU LBM)

Reattachment length $$L_r/H$$ = 2.63.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$, comparable heights | +0.947 | 0.636 | +0.260 | 0.568 | 88 |
| $$W$$, comparable heights | +0.845 | 0.477 | +0.114 | 0.318 | 88 |
| $$U$$, all points | +0.905 | 0.638 | +0.172 | 0.411 | 224 |
| $$U$$, approach flow alone (control) | +0.807 | 0.557 | -0.541 | 0.398 | 88 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/B/pairs/fluidx3d.csv`]({{ '/api/cases/B/pairs/fluidx3d.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseBFluidX3DE2E (Eddy3DCli.Tests/Validation/TestAijVelocityFluidX3DE2E; FluidX3D GPU lattice Boltzmann, D3Q19 Smagorinsky LES, $$\mathrm{d}x = H/64$$, 100 + 500 $$H/U_H$$ spin-up + averaging, with an empty-domain control on the same lattice); figure validation/plot\_cases\_ab\_engines.py

### Eddy3D ML wind surrogate (pedestrian height)

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert$$ ($$z = H/16$$ plane) | -0.236 | 0.361 | +0.821 | 0.172 | 122 |
| $$\lvert\mathbf{U}\rvert$$, lattice cut at ±250 m | +0.010 | 0.459 | +0.463 | 0.189 | 122 |
| wind reversed (control) | -0.236 | 0.361 | +0.821 | 0.172 | 122 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/B/pairs/ml-surrogate.csv`]({{ '/api/cases/B/pairs/ml-surrogate.csv' | relative_url }})
- Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py

### All runs

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

## Figures

Figures: [OpenLB and FluidX3D]({{ '/validation/engines/' | relative_url }}); [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}).
