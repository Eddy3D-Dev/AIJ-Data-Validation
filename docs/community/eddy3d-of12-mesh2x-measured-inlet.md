---
title: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12"
parent: "Community results"
nav_order: 4
has_children: false
generated: true
description: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12: a community submission scored against the AIJ cases by this repository's build."
---

# OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12

Self-reported inputs, scored by this repository's build ([method]({{ '/validation/method/' | relative_url }})). The submitted values are under [`submissions/eddy3d-of12-mesh2x-measured-inlet/`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/tree/main/submissions/eddy3d-of12-mesh2x-measured-inlet) and served as [`/api/submissions/eddy3d-of12-mesh2x-measured-inlet.json`]({{ '/api/submissions/eddy3d-of12-mesh2x-measured-inlet.json' | relative_url }}).

| Field | Value |
|---|---|
| solver | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) |
| version | 12 |
| url | <https://openfoam.org> |
| author | Sustainable Urban Systems Lab |
| licence | CC-BY-4.0 |
| contact | <https://github.com/Eddy3D-Dev/AIJ-Data-Validation/discussions> |
| inlet | the measured approach profile ($$U$$ and $$k$$ of AF\_caseA.csv as fixedProfile tables, epsilon by local equilibrium), rough floor |
| mesh | snappyHexMesh, 1:100 scale, one level finer than the served run on box, building and ground (1,113,756 cells), numerics level 3 |
| turbulence\_model | realizable k-epsilon |
| compute | 3000 iterations, steady, 71 min on 5 ranks of an Apple M-series laptop |
| units | normalised |
| notes | the mesh alone (log-law inlet) moved $$U$$\'s agreement from 0.586 to 0.597 and nothing else; the combination is the sweep\'s best steady set-up. Eddy3D fixture TestAijCaseAContainerE2E with EDDY3D\_VALIDATION\_REFINE=1 EDDY3D\_VALIDATION\_INLET=measured EDDY3D\_VALIDATION\_FLOOR=rough. |

{% include nomenclature.md %}

## Case A — 1:1:2 building

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.958 | 0.812 | +0.150 | 0.651 | 186 | 186/186 |
| $$V$$ | +0.961 | 0.349 | — | 0.887 | 186 | 186/186 |
| $$W$$ | +0.733 | 0.376 | -1.619 | 0.833 | 186 | 186/186 |
| $$\lvert\mathbf{U}\rvert$$ | +0.946 | 0.876 | +0.111 | 0.677 | 186 | 186/186 |
| $$k$$ | +0.460 | 0.688 | +0.374 | 0.317 | 186 | 186/186 |
{: .scores }
