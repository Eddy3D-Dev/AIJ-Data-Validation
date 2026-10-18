---
title: "Cases A and B (OpenFOAM)"
parent: Validation
nav_order: 2
summary: "OpenFOAM 12 on the 1:1:2 building and the 1:4:4 slab"
description: "OpenFOAM 12 against the tunnel for Case A (1:1:2 building) and Case B (1:4:4 slab)."
---

# Cases A and B, OpenFOAM 12

OpenFOAM 12 runs on the 1:1:2 building (Case A) and the 1:4:4 slab (Case B). Every score of each run, with the per-point files, is on the [Case A]({{ '/cases/case-a/validation/' | relative_url }}) and [Case B]({{ '/cases/case-b/validation/' | relative_url }}) Validation pages.

## Measured against modelled

{% include figure.html name="cases-ab-openfoam-agreement.png" alt="Measured vs modelled, Cases A and B" caption="<strong>Figure 1.</strong> Measured vs modelled, Cases A and B." %}

Measured against modelled for each quantity, with the 1:1 line and, where the quantity does not change sign, the factor-of-two band.

| Quantity | R | FAC2 | FB | Hit rate |
|---|---|---|---|---|
| A — U | +0.955 | 0.817 | +0.185 | 0.586 |
| A — V | +0.961 | 0.349 | −0.207 | 0.892 |
| A — W | +0.708 | 0.398 | −1.501 | 0.801 |
| A — k | +0.480 | 0.667 | +0.478 | 0.177 |
| B — U | +0.959 | 0.701 | +0.240 | 0.562 |
| B — V | +0.910 | 0.281 | +0.370 | 0.612 |
| B — W | +0.929 | 0.536 | +0.263 | 0.808 |
| B — k | +0.399 | 0.562 | +0.463 | 0.223 |
{: .scores }

- Normalised by U_H. Hit rate: D = 0.25, W = 0.05 U_H. FB is positive when the model is low.
- Reattachment length behind the building: L_r/H = 1.49 (Case A), 3.27 (Case B).
- V and W change sign.
- Case A, W: the mean measured W is ~0.01 m/s.
- Case B, V: the model's V is 0 on the centre plane (y = 0, a symmetry plane); the tunnel measures small non-zero values there.

<details markdown="block">
<summary>Interpretation: Cases A and B, the scores</summary>

- The streamwise field is right: R ≈ 0.96 in both cases, FAC2 0.82 and 0.70.
- k is under-predicted in both (FB ≈ +0.47, R ≈ 0.4). This is the familiar realizable k-ε behaviour and consistent with what Eddy3D already records for AIJ Case H.
- FAC2 on V and W is low by construction, not by failure. Those components change sign, so factor-of-two agreement is a harsh measure near zero; R and hit rate are the meaningful columns there.
- The flat row of model V ≈ 0 in Case B's panel is the symmetry plane: a RANS solution is symmetric, so V ≡ 0 at y = 0.
- Case A's W FB of −1.50 and its NMSE are artefacts of a near-zero mean, not a blow-up. R = +0.71 is the score to read.

</details>

## Centre-plane profiles

{% include figure.html name="cases-ab-openfoam-profiles.png" alt="Centre-plane profiles, Cases A and B" caption="<strong>Figure 2.</strong> Centre-plane profiles, Cases A and B." %}

Vertical profiles of U/U_H on the centre plane at the first three measured stations behind the building, offset per station.

<details markdown="block">
<summary>Interpretation: Cases A and B, the profiles</summary>

The model follows the measured profile closely above roof height and in the recovering wake; the near-ground deficit immediately behind the building is where the closure does least well.

</details>
