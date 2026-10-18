---
title: "Validation"
parent: "Case C — 3 × 3 block array"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case C — 3 × 3 block array: Eddy3D's scores against the tunnel data, by engine."
---

# Case C: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-grey status">not comparable</span> · FluidX3D <span class="label label-grey status">not comparable</span> · ML surrogate <span class="label label-green status">scored</span>

*Scored* means a run exists and its scores are below, not that it agrees. How to read them is on [the reading page]({{ '/validation/case-c/' | relative_url }}); the [Validation]({{ '/validation/' | relative_url }}) overview says what each status means and why an engine is *not comparable*.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration 0D

Quantity: Vs (thermistor) scored against sqrt(|U|^2 + 2k) \[scalar\] and |U| \[vector\]; both normalised by U\_H = U(z = D) = 3.654 m/s.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| WD 0° √(\|U\|²+2k) | +0.824 | 0.908 | +0.266 | 0.567 | 120 |
| WD 0° \|U\| | +0.804 | 0.658 | +0.466 | 0.308 | 120 |
| WD 22.5° √(\|U\|²+2k) | +0.857 | 0.983 | +0.106 | 0.750 | 120 |
| WD 22.5° \|U\| | +0.846 | 0.833 | +0.295 | 0.433 | 120 |
| WD 45° √(\|U\|²+2k) | +0.831 | 0.942 | +0.121 | 0.783 | 120 |
| WD 45° \|U\| | +0.801 | 0.800 | +0.307 | 0.533 | 120 |
{: .scores }

velocities by U\_H, k by U\_H^2 (the benchmark\'s own convention; Case E by U at 15.9 m, as it is published); hit rate D = 0.25, W = 0.05 in those units. Per-point values: [`/api/cases/C/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/C/pairs/openfoam12-realizableKE.csv' | relative_url }}). Reproduce: Eddy3D fixture TestAijCaseC0DContainerE2E; figures validation/plot\_case\_c\_openfoam.py.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration 1D

Quantity: Vs (thermistor) scored against sqrt(|U|^2 + 2k) \[scalar\] and |U| \[vector\]; both normalised by U\_H = U(z = D) = 3.654 m/s.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| WD 0° √(\|U\|²+2k) | +0.801 | 0.858 | +0.341 | 0.433 | 120 |
| WD 0° \|U\| | +0.741 | 0.550 | +0.551 | 0.292 | 120 |
| WD 22.5° √(\|U\|²+2k) | +0.896 | 0.975 | +0.192 | 0.675 | 120 |
| WD 22.5° \|U\| | +0.882 | 0.725 | +0.394 | 0.367 | 120 |
| WD 45° √(\|U\|²+2k) | +0.872 | 0.942 | +0.198 | 0.733 | 120 |
| WD 45° \|U\| | +0.873 | 0.850 | +0.353 | 0.433 | 120 |
{: .scores }

velocities by U\_H, k by U\_H^2 (the benchmark\'s own convention; Case E by U at 15.9 m, as it is published); hit rate D = 0.25, W = 0.05 in those units. Per-point values: [`/api/cases/C/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/C/pairs/openfoam12-realizableKE.csv' | relative_url }}). Reproduce: Eddy3D fixture TestAijCaseC1DContainerE2E; figures validation/plot\_case\_c\_openfoam.py.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration 2D

Quantity: Vs (thermistor) scored against sqrt(|U|^2 + 2k) \[scalar\] and |U| \[vector\]; both normalised by U\_H = U(z = D) = 3.654 m/s.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| WD 0° √(\|U\|²+2k) | +0.857 | 0.850 | +0.251 | 0.492 | 120 |
| WD 0° \|U\| | +0.848 | 0.692 | +0.443 | 0.317 | 120 |
| WD 22.5° √(\|U\|²+2k) | +0.906 | 0.983 | +0.091 | 0.875 | 120 |
| WD 22.5° \|U\| | +0.894 | 0.900 | +0.240 | 0.633 | 120 |
| WD 45° √(\|U\|²+2k) | +0.909 | 0.958 | +0.103 | 0.883 | 120 |
| WD 45° \|U\| | +0.912 | 0.900 | +0.243 | 0.608 | 120 |
{: .scores }

velocities by U\_H, k by U\_H^2 (the benchmark\'s own convention; Case E by U at 15.9 m, as it is published); hit rate D = 0.25, W = 0.05 in those units. Per-point values: [`/api/cases/C/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/C/pairs/openfoam12-realizableKE.csv' | relative_url }}). Reproduce: Eddy3D fixture TestAijCaseC2DContainerE2E; figures validation/plot\_case\_c\_openfoam.py.

## Eddy3D ML wind surrogate (pedestrian height)

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| Vs, 9 configurations | +0.212 | 0.444 | +0.666 | 0.181 | 1080 |
| Vs, 2D WD 0, lattice cut at ±250 m | +0.075 | 0.875 | +0.192 | 0.400 | 120 |
| wind reversed (control) | -0.441 | 0.725 | +0.367 | 0.392 | 120 |
{: .scores }

velocities by U\_H, k by U\_H^2 (the benchmark\'s own convention; Case E by U at 15.9 m, as it is published); hit rate D = 0.25, W = 0.05 in those units. Per-point values: [`/api/cases/C/pairs/ml-surrogate.csv`]({{ '/api/cases/C/pairs/ml-surrogate.csv' | relative_url }}). Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py.

## Figures

The figures for these runs are shown once, beside their reading: [Case C (OpenFOAM)]({{ '/validation/case-c/' | relative_url }}); [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}).
