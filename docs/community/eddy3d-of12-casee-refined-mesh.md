---
title: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12"
parent: "Community results"
nav_order: 1
has_children: false
generated: true
description: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12: a community submission scored against the AIJ cases by this repository's build."
---

# OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12

Self-reported inputs, scored by this repository's build ([method]({{ '/validation/method/' | relative_url }})). The submitted values are under [`submissions/eddy3d-of12-casee-refined-mesh/`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/tree/main/submissions/eddy3d-of12-casee-refined-mesh) and served as [`/api/submissions/eddy3d-of12-casee-refined-mesh.json`]({{ '/api/submissions/eddy3d-of12-casee-refined-mesh.json' | relative_url }}).

| Field | Value |
|---|---|
| solver | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) |
| version | 12 |
| url | <https://openfoam.org> |
| author | Sustainable Urban Systems Lab |
| licence | CC-BY-4.0 |
| contact | <https://github.com/Eddy3D-Dev/AIJ-Data-Validation/discussions> |
| inlet | the workbook\'s tabulated inflow ($$z/Z_R$$, $$U/U_R$$, $$k/U_R^2$$ with $$Z_R$$ = 250 m, $$U_R$$ = 7.8 m/s) as fixedProfile tables, the served run\'s inlet |
| mesh | snappyHexMesh at full scale, 504 m cylinder, 16 m background, 4 m box, 2 m ground and 1 m buildings (1,414,688 cells); numerics level 3 on the hardened preset the checkMesh verdict selects |
| turbulence\_model | realizable k-epsilon |
| compute | 2000 iterations per state, steady, about 80 min per state on 5 ranks of an Apple M-series laptop |
| units | normalised |
| notes | ratios over the model\'s own solved $$U$$ at 15.9 m, 400 m upwind, as the served run; SW only. Eddy3D fixture TestAijCaseEContainerE2E with EDDY3D\_VALIDATION\_REFINE=1, one state per run (EDDY3D\_AIJ\_E\_STATES). |

{% include nomenclature.md %}

## Case E — Niigata district

### config ac, wind\_direction\_deg 225.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.877 | 0.912 | +0.133 | 0.562 | 80 | 80/80 |
| $$\lvert\mathbf{U}\rvert$$ | +0.869 | 0.762 | +0.237 | 0.388 | 80 | 80/80 |
{: .scores }

{% include nomenclature-scores.md %}

### config bc, wind\_direction\_deg 225.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.700 | 0.950 | +0.065 | 0.562 | 80 | 80/80 |
| $$\lvert\mathbf{U}\rvert$$ | +0.708 | 0.812 | +0.208 | 0.388 | 80 | 80/80 |
{: .scores }

{% include nomenclature-scores.md %}
