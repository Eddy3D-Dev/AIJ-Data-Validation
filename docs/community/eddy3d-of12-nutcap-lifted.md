---
title: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12"
parent: "Community results"
nav_order: 5
has_children: false
generated: true
description: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12: a community submission scored against the AIJ cases by this repository's build."
---

# OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12

Self-reported inputs, scored by this repository's build ([method]({{ '/validation/method/' | relative_url }})). The submitted values are under [`submissions/eddy3d-of12-nutcap-lifted/`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/tree/main/submissions/eddy3d-of12-nutcap-lifted) and served as [`/api/submissions/eddy3d-of12-nutcap-lifted.json`]({{ '/api/submissions/eddy3d-of12-nutcap-lifted.json' | relative_url }}).

| Field | Value |
|---|---|
| solver | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) |
| version | 12 |
| url | <https://openfoam.org> |
| author | Sustainable Urban Systems Lab |
| licence | CC-BY-4.0 |
| contact | <https://github.com/Eddy3D-Dev/AIJ-Data-Validation/discussions> |
| inlet | Case A, H and K, the served fitted log law; Case B, the measured approach profile with the rough floor (the measured-inlet run, the only Case B study re-solved) |
| mesh | snappyHexMesh, 1:100 scale, the served runs\' mesh and numerics level 3 |
| turbulence\_model | realizable k-epsilon, nutMaxCoeff 1e8 |
| compute | 3000 iterations, steady, 5-6 ranks (Case A on an Apple M-series laptop, B and H on PACE Phoenix) |
| units | normalised |
| notes | Same fixtures as the served runs (Eddy3D docs/VALIDATION.md) with only the cap changed. Case H cstar is the $$\mathrm{Sc_t}$$ = 0.5 species. Case B\'s baseline is therefore the measured-inlet submission, not the served run. |

{% include nomenclature.md %}

## Case A — 1:1:2 building

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.954 | 0.823 | +0.166 | 0.613 | 186 | 186/186 |
| $$V$$ | +0.962 | 0.360 | — | 0.903 | 186 | 186/186 |
| $$W$$ | +0.709 | 0.403 | -1.362 | 0.833 | 186 | 186/186 |
| $$\lvert\mathbf{U}\rvert$$ | +0.940 | 0.866 | +0.130 | 0.667 | 186 | 186/186 |
| $$k$$ | +0.390 | 0.677 | +0.394 | 0.247 | 186 | 186/186 |
{: .scores }

## Case B — 1:4:4 slab

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.959 | 0.710 | +0.113 | 0.554 | 224 | 224/224 |
| $$V$$ | +0.915 | 0.272 | — | 0.629 | 224 | 224/224 |
| $$W$$ | +0.923 | 0.478 | +0.430 | 0.772 | 224 | 224/224 |
| $$\lvert\mathbf{U}\rvert$$ | +0.948 | 0.857 | +0.059 | 0.670 | 224 | 224/224 |
| $$k$$ | +0.312 | 0.562 | +0.282 | 0.254 | 224 | 224/224 |
{: .scores }

## Case H — 1:1:2 building with a floor point source

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.890 | 0.634 | +0.313 | 0.476 | 826 | 826/826 |
| $$V$$ | +0.938 | 0.369 | -0.400 | 0.702 | 826 | 826/826 |
| $$W$$ | +0.870 | 0.297 | — | 0.714 | 826 | 826/826 |
| $$\lvert\mathbf{U}\rvert$$ | +0.875 | 0.683 | +0.318 | 0.471 | 826 | 826/826 |
| $$k$$ | -0.011 | 0.608 | +0.302 | 0.339 | 826 | 826/826 |
| $$c^\ast$$ | +0.947 | 0.636 | -0.739 | 0.489 | 826 | 826/826 |
{: .scores }

## Case K — 9 x 9 cube array, point source

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.960 | 0.631 | +0.527 | 0.232 | 203 | 203/203 |
| $$V$$ | -0.142 | 0.049 | — | 0.901 | 203 | 203/203 |
| $$W$$ | +0.629 | 0.133 | — | 0.680 | 203 | 203/203 |
| $$\lvert\mathbf{U}\rvert$$ | +0.945 | 0.606 | +0.506 | 0.192 | 203 | 203/203 |
| $$k$$ | +0.357 | 0.261 | +0.955 | 0.039 | 203 | 203/203 |
| $$c^\ast$$ | +0.949 | 0.808 | -0.751 | 0.478 | 203 | 203/203 |
{: .scores }
