---
title: "OpenFOAM pimpleFoam (Eddy3D Outdoor case writer) 12"
parent: "Community results"
nav_order: 5
has_children: false
generated: true
description: "OpenFOAM pimpleFoam (Eddy3D Outdoor case writer) 12: a community submission scored against the AIJ cases by this repository's build."
---

# OpenFOAM pimpleFoam (Eddy3D Outdoor case writer) 12

Self-reported inputs, scored by this repository's build ([method]({{ '/validation/method/' | relative_url }})). The submitted values are under [`submissions/eddy3d-of12-sst-urans/`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/tree/main/submissions/eddy3d-of12-sst-urans) and served as [`/api/submissions/eddy3d-of12-sst-urans.json`]({{ '/api/submissions/eddy3d-of12-sst-urans.json' | relative_url }}).

| Field | Value |
|---|---|
| solver | OpenFOAM pimpleFoam (Eddy3D Outdoor case writer) |
| version | 12 |
| url | <https://openfoam.org> |
| author | Sustainable Urban Systems Lab |
| licence | CC-BY-4.0 |
| contact | <https://github.com/Eddy3D-Dev/AIJ-Data-Validation/discussions> |
| inlet | the measured approach profile ($$U$$ and $$k$$ of AF\_caseA.csv as fixedProfile tables, epsilon by local equilibrium, omega = epsilon/($$C_\mu$$ $$k$$)), rough floor |
| mesh | snappyHexMesh, 1:100 scale, the served run\'s mesh (280k cells), numerics level 3 |
| turbulence\_model | SST k-omega, URANS |
| compute | 1000 s of flow time (about 280 $$H/U_H$$) at max Co 2 (dt about 0.045 s), fieldAverage with an exponential window of 500 s; 3 h 20 min on 5 ranks of an Apple M-series laptop |
| units | normalised |
| notes | $$k$$ is the modelled mean plus the resolved part; 27 % of the wake\'s $$k$$ is resolved, 3 % upstream. Eddy3D fixture TestAijCaseAContainerE2E with EDDY3D\_VALIDATION\_TURB=kOmegaSST EDDY3D\_VALIDATION\_INLET=measured EDDY3D\_VALIDATION\_FLOOR=rough EDDY3D\_VALIDATION\_ALGO=PIMPLE EDDY3D\_VALIDATION\_DURATION=1000. |

{% include nomenclature.md %}

## Case A — 1:1:2 building

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.953 | 0.763 | +0.181 | 0.683 | 186 | 186/186 |
| $$V$$ | +0.953 | 0.360 | — | 0.817 | 186 | 186/186 |
| $$W$$ | +0.675 | 0.414 | -1.352 | 0.699 | 186 | 186/186 |
| $$\lvert\mathbf{U}\rvert$$ | +0.924 | 0.823 | +0.099 | 0.720 | 186 | 186/186 |
| $$k$$ | +0.626 | 0.694 | +0.453 | 0.392 | 186 | 186/186 |
{: .scores }
