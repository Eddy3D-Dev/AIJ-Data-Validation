---
title: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12"
parent: "Community results"
nav_order: 3
has_children: false
generated: true
description: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12: a community submission scored against the AIJ cases by this repository's build."
---

# OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12

Self-reported inputs, scored by this repository's build ([method]({{ '/validation/method/' | relative_url }})). The submitted values are under [`submissions/eddy3d-of12-measured-inlet/`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/tree/main/submissions/eddy3d-of12-measured-inlet) and served as [`/api/submissions/eddy3d-of12-measured-inlet.json`]({{ '/api/submissions/eddy3d-of12-measured-inlet.json' | relative_url }}).

| Field | Value |
|---|---|
| solver | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) |
| version | 12 |
| url | <https://openfoam.org> |
| author | Sustainable Urban Systems Lab |
| licence | CC-BY-4.0 |
| contact | <https://github.com/Eddy3D-Dev/AIJ-Data-Validation/discussions> |
| inlet | the measured approach profile ($$U$$ and $$k$$ of AF\_caseA/B/H.csv as fixedProfile tables, epsilon by local equilibrium), rough floor (nutkAtmRoughWallFunction, $$z_0$$ of the log-law fit) |
| mesh | snappyHexMesh, 1:100 scale, the served runs\' mesh (Case A 280k cells, $$H/26$$ at the building), numerics level 3 |
| turbulence\_model | realizable k-epsilon |
| compute | 3000 iterations, steady, 5 ranks of an Apple M-series laptop; 38 min (A), 31 min (B), 50 min (H) |
| units | normalised |
| notes | Eddy3D fixtures TestAijCaseA/B/HContainerE2E with EDDY3D\_VALIDATION\_INLET=measured EDDY3D\_VALIDATION\_FLOOR=rough (Eddy3D docs/VALIDATION.md 3c-ii). Case H cstar is the $$\mathrm{Sc_t}$$ = 0.5 species. |

{% include nomenclature.md %}

## Case A — 1:1:2 building

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.956 | 0.812 | +0.152 | 0.624 | 186 | 186/186 |
| $$V$$ | +0.961 | 0.344 | — | 0.876 | 186 | 186/186 |
| $$W$$ | +0.717 | 0.414 | -1.543 | 0.828 | 186 | 186/186 |
| $$\lvert\mathbf{U}\rvert$$ | +0.942 | 0.871 | +0.114 | 0.667 | 186 | 186/186 |
| $$k$$ | +0.414 | 0.688 | +0.380 | 0.344 | 186 | 186/186 |
{: .scores }

## Case B — 1:4:4 slab

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.958 | 0.688 | +0.215 | 0.571 | 224 | 224/224 |
| $$V$$ | +0.908 | 0.286 | — | 0.607 | 224 | 224/224 |
| $$W$$ | +0.931 | 0.522 | +0.252 | 0.821 | 224 | 224/224 |
| $$\lvert\mathbf{U}\rvert$$ | +0.945 | 0.817 | +0.081 | 0.625 | 224 | 224/224 |
| $$k$$ | +0.405 | 0.571 | +0.440 | 0.263 | 224 | 224/224 |
{: .scores }

## Case H — 1:1:2 building with a floor point source

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.897 | 0.608 | +0.357 | 0.447 | 826 | 826/826 |
| $$V$$ | +0.935 | 0.362 | -0.425 | 0.684 | 826 | 826/826 |
| $$W$$ | +0.887 | 0.308 | — | 0.713 | 826 | 826/826 |
| $$\lvert\mathbf{U}\rvert$$ | +0.884 | 0.650 | +0.358 | 0.435 | 826 | 826/826 |
| $$k$$ | +0.118 | 0.576 | +0.522 | 0.311 | 826 | 826/826 |
| $$c^\ast$$ | +0.951 | 0.619 | -0.825 | 0.508 | 826 | 826/826 |
{: .scores }
