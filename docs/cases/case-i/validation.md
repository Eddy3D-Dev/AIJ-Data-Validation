---
title: "Validation"
parent: "Case I — cube with a roof point source"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case I — cube with a roof point source: Eddy3D's scores against the measurements, by engine."
---

# Case I: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenFOAM 12 k-ε <span class="label label-green status">scored</span> · OpenFOAM 12 k-ω SST <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor)

Reattachment length L<sub>r</sub>/H = 2.51.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| U | +0.998 | 0.879 | +0.020 | 0.813 | 91 |
| V | +0.985 | 0.895 | — | 1.000 | 38 |
| W | +0.972 | 0.659 | -0.049 | 0.967 | 91 |
| k | +0.905 | 0.923 | +0.106 | 0.582 | 91 |
| c\*, Sct 0.3 | +0.922 | 0.360 | +0.398 | 0.106 | 539 |
| c\*, Sct 0.5 | +0.940 | 0.475 | +0.083 | 0.284 | 539 |
| c\*, Sct 0.7 | +0.946 | 0.477 | -0.100 | 0.291 | 539 |
{: .scores }

- Per-point values: [`/api/cases/I/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/I/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCubeContainerE2E (realizable k-ε, 1:60) (numerics level 3, 3000 iterations); figures validation/plot\_cases\_hi\_openfoam.py

## OpenFOAM 12, standard k-epsilon (Eddy3D Outdoor)

Reattachment length L<sub>r</sub>/H = 2.23.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| U | +0.990 | 0.846 | -0.003 | 0.769 | 91 |
| V | +0.966 | 0.789 | — | 0.895 | 38 |
| W | +0.943 | 0.615 | +0.080 | 0.901 | 91 |
| k | +0.870 | 0.912 | -0.037 | 0.637 | 91 |
| c\*, Sct 0.3 | +0.938 | 0.442 | +0.308 | 0.134 | 539 |
| c\*, Sct 0.5 | +0.955 | 0.519 | -0.035 | 0.378 | 539 |
| c\*, Sct 0.7 | +0.954 | 0.519 | -0.248 | 0.288 | 539 |
{: .scores }

- Per-point values: [`/api/cases/I/pairs/openfoam12-kEpsilon.csv`]({{ '/api/cases/I/pairs/openfoam12-kEpsilon.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCubeContainerE2E (standard k-ε, 1:60) (numerics level 3, 3000 iterations); figures validation/plot\_cases\_hi\_openfoam.py

## OpenFOAM 12, k-omega SST (Eddy3D Outdoor)

Reattachment length L<sub>r</sub>/H = 2.68.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| U | +0.992 | 0.879 | +0.091 | 0.802 | 91 |
| V | +0.968 | 0.789 | -2.000 | 0.921 | 38 |
| W | +0.922 | 0.615 | -0.214 | 0.868 | 91 |
| k | +0.880 | 0.396 | +0.495 | 0.264 | 91 |
| c\*, Sct 0.3 | +0.514 | 0.432 | -0.047 | 0.236 | 539 |
| c\*, Sct 0.5 | +0.466 | 0.403 | -0.153 | 0.202 | 539 |
| c\*, Sct 0.7 | +0.439 | 0.380 | -0.221 | 0.195 | 539 |
{: .scores }

- Per-point values: [`/api/cases/I/pairs/openfoam12-kOmegaSST.csv`]({{ '/api/cases/I/pairs/openfoam12-kOmegaSST.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCubeContainerE2E (k-ω SST, 1:60) (numerics level 3, 3000 iterations); figures validation/plot\_cases\_hi\_openfoam.py

## All runs

- Normalisation: velocities by U\_H, k by U\_H^2 (the benchmark\'s own convention; Case E by U at 15.9 m, as it is published); hit rate D = 0.25, W = 0.05 in those units

- Scores recomputed from the pairs by validation/dispersion\_metrics.py.

## Figures

Figures: [Cases H and I (OpenFOAM)]({{ '/validation/cases-hi/' | relative_url }}).
