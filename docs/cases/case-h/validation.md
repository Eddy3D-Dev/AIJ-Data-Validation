---
title: "Validation"
parent: "Case H — 1:1:2 building with a floor point source"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case H — 1:1:2 building with a floor point source: Eddy3D's scores against the measurements, by engine."
---

# Case H: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor)

Reattachment length L<sub>r</sub>/H = 1.36.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| U | +0.897 | 0.609 | +0.355 | 0.446 | 826 |
| V | +0.935 | 0.355 | -0.432 | 0.682 | 826 |
| W | +0.887 | 0.314 | — | 0.713 | 826 |
| k | +0.107 | 0.570 | +0.514 | 0.305 | 826 |
| c\*, Sct 0.3 | +0.954 | 0.694 | -0.597 | 0.493 | 826 |
| c\*, Sct 0.5 | +0.951 | 0.615 | -0.825 | 0.507 | 826 |
| c\*, Sct 0.7 | +0.946 | 0.588 | -0.934 | 0.493 | 826 |
{: .scores }

- Normalisation: velocities by U\_H, k by U\_H^2 (the benchmark\'s own convention; Case E by U at 15.9 m, as it is published); hit rate D = 0.25, W = 0.05 in those units
- Per-point values: [`/api/cases/H/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/H/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseHContainerE2E (realizable k-ε, 1:100) (numerics level 3, 3000 iterations); figures validation/plot\_cases\_hi\_openfoam.py

- Scores recomputed from the pairs by validation/dispersion\_metrics.py.

## Figures

Figures: [Cases H and I (OpenFOAM)]({{ '/validation/cases-hi/' | relative_url }}).
