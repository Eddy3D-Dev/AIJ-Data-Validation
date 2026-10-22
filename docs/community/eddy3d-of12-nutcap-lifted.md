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
| inlet | the served fitted log law |
| mesh | snappyHexMesh, 1:100 scale, the served runs\' mesh and numerics level 3 |
| turbulence\_model | realizable k-epsilon, nutMaxCoeff 1e8 |
| compute | 3000 iterations, steady, 5-6 ranks (Case A on an Apple M-series laptop, B and H on PACE Phoenix) |
| units | normalised |
| notes | Case D is the 0 degree heading only (the fixture stopped at its mirrored-plane probe before the other headings; PACE ICE job 6465404). Case G is the conifer crown of the drag sweep, where lifting the cap makes the result worse (a worse score, submitted all the same). Case C (all nine configurations, scalar speed sampled from the solved fields of the ICE re-solves), Cases F (wind from NNW) and M (WD 180, $$\mathrm{Sc_t}$$ 0.5) are the Eddy3D fixtures re-solved by another session on PACE ICE with the same cap change, scored here from their probe files. Same fixtures as the served runs (Eddy3D docs/VALIDATION.md) with only the cap changed. Case H cstar is the $$\mathrm{Sc_t}$$ = 0.5 species. Case B is the served set-up with the cap lifted (the capped control of the same fixture reproduces the served B scores to the third digit). |

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
| $$U$$ | +0.957 | 0.719 | +0.113 | 0.540 | 224 | 224/224 |
| $$V$$ | +0.919 | 0.272 | — | 0.638 | 224 | 224/224 |
| $$W$$ | +0.916 | 0.473 | +0.549 | 0.723 | 224 | 224/224 |
| $$\lvert\mathbf{U}\rvert$$ | +0.943 | 0.857 | +0.063 | 0.634 | 224 | 224/224 |
| $$k$$ | +0.291 | 0.554 | +0.305 | 0.201 | 224 | 224/224 |
{: .scores }

## Case C — 3 × 3 block array

### config 0D, wind\_direction\_deg 0.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.839 | 0.917 | +0.270 | 0.583 | 120 | 120/120 |
| $$\lvert\mathbf{U}\rvert$$ | +0.816 | 0.658 | +0.476 | 0.292 | 120 | 120/120 |
{: .scores }

### config 0D, wind\_direction\_deg 22.5

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.860 | 0.983 | +0.119 | 0.733 | 120 | 120/120 |
| $$\lvert\mathbf{U}\rvert$$ | +0.848 | 0.808 | +0.320 | 0.425 | 120 | 120/120 |
{: .scores }

### config 0D, wind\_direction\_deg 45.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.840 | 0.933 | +0.130 | 0.800 | 120 | 120/120 |
| $$\lvert\mathbf{U}\rvert$$ | +0.808 | 0.783 | +0.323 | 0.533 | 120 | 120/120 |
{: .scores }

### config 1D, wind\_direction\_deg 0.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.794 | 0.867 | +0.340 | 0.408 | 120 | 120/120 |
| $$\lvert\mathbf{U}\rvert$$ | +0.729 | 0.558 | +0.553 | 0.317 | 120 | 120/120 |
{: .scores }

### config 1D, wind\_direction\_deg 22.5

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.904 | 0.967 | +0.198 | 0.667 | 120 | 120/120 |
| $$\lvert\mathbf{U}\rvert$$ | +0.888 | 0.692 | +0.408 | 0.342 | 120 | 120/120 |
{: .scores }

### config 1D, wind\_direction\_deg 45.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.879 | 0.925 | +0.212 | 0.725 | 120 | 120/120 |
| $$\lvert\mathbf{U}\rvert$$ | +0.879 | 0.800 | +0.374 | 0.392 | 120 | 120/120 |
{: .scores }

### config 2D, wind\_direction\_deg 0.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.863 | 0.867 | +0.238 | 0.558 | 120 | 120/120 |
| $$\lvert\mathbf{U}\rvert$$ | +0.855 | 0.692 | +0.432 | 0.317 | 120 | 120/120 |
{: .scores }

### config 2D, wind\_direction\_deg 22.5

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.907 | 0.983 | +0.111 | 0.842 | 120 | 120/120 |
| $$\lvert\mathbf{U}\rvert$$ | +0.893 | 0.867 | +0.271 | 0.575 | 120 | 120/120 |
{: .scores }

### config 2D, wind\_direction\_deg 45.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.926 | 1.000 | +0.104 | 0.908 | 120 | 120/120 |
| $$\lvert\mathbf{U}\rvert$$ | +0.927 | 0.900 | +0.248 | 0.633 | 120 | 120/120 |
{: .scores }

## Case D — high-rise among city blocks

### wind\_direction\_deg 0.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\lvert\mathbf{U}\rvert$$ | +0.870 | 0.818 | +0.066 | 0.485 | 33 | 33/33 |
| $$k$$ | -0.194 | 0.273 | +0.452 | 0.091 | 33 | 33/33 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.789 | 0.788 | +0.202 | 0.530 | 66 | 66/66 |
| $$\lvert\mathbf{U}\rvert$$ | +0.805 | 0.682 | +0.355 | 0.409 | 66 | 66/66 |
{: .scores }

## Case F — Shinjuku district

### config default, campaign field, wind\_direction\_deg 337.5

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.853 | 1.000 | +0.008 | 0.538 | 13 | 13/13 |
| $$\lvert\mathbf{U}\rvert$$ | +0.831 | 0.846 | +0.169 | 0.462 | 13 | 13/13 |
{: .scores }

### config default, campaign wind\_tunnel, wind\_direction\_deg 337.5

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.928 | 1.000 | -0.013 | 0.615 | 13 | 13/13 |
| $$\lvert\mathbf{U}\rvert$$ | +0.920 | 0.923 | +0.147 | 0.462 | 13 | 13/13 |
{: .scores }

### config h20, campaign wind\_tunnel, wind\_direction\_deg 337.5

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.754 | 0.923 | -0.002 | 0.769 | 13 | 13/13 |
| $$\lvert\mathbf{U}\rvert$$ | +0.751 | 0.923 | +0.092 | 0.692 | 13 | 13/13 |
{: .scores }

### config h5, campaign wind\_tunnel, wind\_direction\_deg 337.5

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.954 | 1.000 | +0.017 | 0.714 | 7 | 7/7 |
| $$\lvert\mathbf{U}\rvert$$ | +0.936 | 0.857 | +0.201 | 0.714 | 7 | 7/7 |
{: .scores }

## Case G — flow behind a tree belt

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$k$$ | +0.344 | 0.357 | -0.827 | 0.071 | 28 | 28/28 |
| $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.325 | 0.929 | -0.526 | 0.036 | 28 | 28/28 |
| $$\lvert\mathbf{U}\rvert$$ | +0.327 | 1.000 | -0.407 | 0.071 | 28 | 28/28 |
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

## Case M — TPU Atsugi campus

### campaign wind\_tunnel, wind\_direction\_deg 180.0

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.627 | 0.200 | +1.064 | 0.133 | 15 | 15/15 |
| $$V$$ | +0.701 | 0.267 | — | 0.133 | 15 | 15/15 |
| $$W$$ | +0.117 | 0.333 | +1.938 | 0.667 | 15 | 15/15 |
| $$\lvert\mathbf{U}\rvert$$ | +0.540 | 0.667 | +0.169 | 0.533 | 15 | 15/15 |
| $$k$$ | +0.463 | 0.267 | +0.875 | 0.133 | 15 | 15/15 |
| $$c^\ast$$ | +0.354 | 0.133 | +1.083 | 0.067 | 15 | 15/15 |
{: .scores }
