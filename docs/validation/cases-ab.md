---
title: "Cases A and B (OpenFOAM)"
parent: Validation
nav_order: 2
summary: "OpenFOAM 12 on the 1:1:2 building and the 1:4:4 slab"
description: "OpenFOAM 12 against the tunnel for Case A (1:1:2 building) and Case B (1:4:4 slab)."
---

# Cases A and B, OpenFOAM 12

OpenFOAM 12 runs on the 1:1:2 building (Case A) and the 1:4:4 slab (Case B). Per-run scores and per-point files: [Case A]({{ '/cases/case-a/validation/' | relative_url }}) and [Case B]({{ '/cases/case-b/validation/' | relative_url }}) Validation pages.

## Measurement layout

{% include figure.html name="case-a-layout.png" alt="Measurement lines and planes, Case A" caption="<strong>Figure 1.</strong> Case A, measurement lines and planes: A vertical profiles, y/b = 0; B plane z/b = 0.125; C plane z/b = 1.25. Positions in multiples of b." %}

{% include figure.html name="case-b-layout.png" alt="Measurement lines and planes, Case B" caption="<strong>Figure 2.</strong> Case B, measurement lines and planes: A vertical profiles, y/H = 0; B plane z/H = 0.0625. Positions in multiples of H." %}

## Measured against modelled

{% include figure.html name="cases-ab-openfoam-agreement.png" alt="Measured vs modelled, Cases A and B" caption="<strong>Figure 3.</strong> Measured vs modelled, Cases A and B. The dots take the colour of the line or plane they were measured on, as in Figures 1 and 2." %}

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

## Centre-plane profiles

{% include figure.html name="cases-ab-openfoam-profiles.png" alt="Centre-plane profiles, Cases A and B" caption="<strong>Figure 4.</strong> Centre-plane profiles, Cases A and B." %}

Vertical profiles of U/U_H on the centre plane at the first three measured stations behind the building, offset per station.

<details markdown="block">
<summary>Interpretation: Cases A and B scores and profiles</summary>

- The streamwise field is right: R ≈ 0.96 in both cases, FAC2 0.82 and 0.70.
- k is under-predicted in both (FB ≈ +0.47, R ≈ 0.4); Case H shows the same under-prediction (FB +0.51).
- V and W change sign, so factor-of-two agreement is a harsh measure near zero and FAC2 is low on both; R and hit rate carry the comparison there.
- The flat row of model V ≈ 0 in Case B's panel is the symmetry plane: a RANS solution is symmetric, so V ≡ 0 at y = 0.
- Case A's W FB of −1.50 and its NMSE follow from a near-zero mean; the correlation is R = +0.71.
- The model follows the measured profile closely above roof height and in the recovering wake; the near-ground deficit immediately behind the building is where the closure does least well.

</details>
