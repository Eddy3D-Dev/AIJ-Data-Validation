---
title: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12"
parent: "Community results"
nav_order: 2
has_children: false
generated: true
description: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12: a community submission scored against the AIJ cases by this repository's build."
---

# OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12

Self-reported inputs, scored by this repository's build ([method]({{ '/validation/method/' | relative_url }})). The submitted values are under [`submissions/eddy3d-of12-casek-workbook-inflow/`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/tree/main/submissions/eddy3d-of12-casek-workbook-inflow) and served as [`/api/submissions/eddy3d-of12-casek-workbook-inflow.json`]({{ '/api/submissions/eddy3d-of12-casek-workbook-inflow.json' | relative_url }}).

| Field | Value |
|---|---|
| solver | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) |
| version | 12 |
| url | <https://openfoam.org> |
| author | Sustainable Urban Systems Lab |
| licence | CC-BY-4.0 |
| contact | <https://github.com/Eddy3D-Dev/AIJ-Data-Validation/discussions> |
| inlet | log law with Uref = 4.94009 m/s at 0.2 m (the workbook\'s $$U_H$$), $$z_0$$ = 13.5 mm (the fit to the shipped profile), atmBoundaryLayer inlets |
| mesh | snappyHexMesh, 1:100 scale, the served run\'s mesh (972,637 cells), numerics level 3 |
| turbulence\_model | realizable k-epsilon |
| compute | 3000 iterations, steady, 1 h 32 min on 5 ranks of an Apple M-series laptop |
| units | normalised |
| notes | cstar is the $$\mathrm{Sc_t}$$ = 0.5 species (0.3 and 0.7 were solved too). The three stated speeds of the package (readme 2.33 m/s at 0.06 m, workbook 4.94009 m/s at 0.2 m, the shipped profile\'s 3.23 m/s at 0.2 m) are not one log law; the measured above-roof plane runs 20 percent above the shipped profile. Eddy3D fixture TestAijCaseKContainerE2E with EDDY3D\_AIJ\_K\_INFLOW=4.94009. |

{% include nomenclature.md %}

## Case K — 9 x 9 cube array, point source

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.956 | 0.650 | +0.228 | 0.562 | 203 | 203/203 |
| $$V$$ | -0.151 | 0.049 | — | 0.877 | 203 | 203/203 |
| $$W$$ | +0.557 | 0.217 | — | 0.670 | 203 | 203/203 |
| $$\lvert\mathbf{U}\rvert$$ | +0.947 | 0.621 | +0.222 | 0.507 | 203 | 203/203 |
| $$k$$ | +0.314 | 0.488 | +0.670 | 0.103 | 203 | 203/203 |
| $$c^\ast$$ | +0.952 | 0.759 | -0.577 | 0.399 | 203 | 203/203 |
{: .scores }
