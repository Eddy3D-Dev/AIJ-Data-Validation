---
title: "Cases A and B (OpenFOAM)"
parent: Validation
nav_order: 2
summary: "OpenFOAM 12 on the 1:1:2 building and the 1:4:4 slab"
description: "OpenFOAM 12 against the tunnel for Case A (1:1:2 building) and Case B (1:4:4 slab)."
---

# Cases A and B, OpenFOAM 12

The reading of the OpenFOAM 12 runs on the 1:1:2 building and the 1:4:4 slab. Every score of each run, with the per-point files, is on the [Case A]({{ '/cases/case-a/validation/' | relative_url }}) and [Case B]({{ '/cases/case-b/validation/' | relative_url }}) Validation pages.

## Does the model agree?

<figure class="figure">
<img src="{{ '/assets/figures/cases-ab-openfoam-agreement.png' | relative_url }}" alt="Measured vs modelled, Cases A and B">
<figcaption><strong>Figure 1.</strong> Measured vs modelled, Cases A and B.</figcaption>
</figure>

Measured against modelled for each quantity, with the 1:1 line and, where the quantity does not change sign, the
factor-of-two band.

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

Normalised by U_H throughout. Hit rate uses D = 0.25, W = 0.05 U_H.
Reattachment length behind the building: **L_r/H = 1.49** (Case A), **3.27** (Case B).

Reading these honestly:

- **The streamwise field is right** — R ≈ 0.96 in both cases, FAC2 0.82 / 0.70.
- **k is under-predicted in both** (FB ≈ +0.47, R ≈ 0.4), the familiar realizable k-ε behaviour and consistent with
  what Eddy3D already records for AIJ Case H.
- **FAC2 on V and W is low by construction, not by failure.** Those components change sign, so factor-of-two
  agreement is a harsh measure near zero; R and hit rate are the meaningful columns there. The flat row of model
  V ≈ 0 in Case B's panel is the symmetry plane: a RANS solution is symmetric, so V ≡ 0 at y = 0, while the tunnel
  measures small non-zero values.
- **Case A's W FB of −1.50 and its NMSE are artefacts of a near-zero mean** (mean measured W is ~0.01 m/s), not a
  blow-up. Read R = +0.71 instead.

## Where does it agree?

<figure class="figure">
<img src="{{ '/assets/figures/cases-ab-openfoam-profiles.png' | relative_url }}" alt="Centre-plane profiles, Cases A and B">
<figcaption><strong>Figure 2.</strong> Centre-plane profiles, Cases A and B.</figcaption>
</figure>

Vertical profiles of U/U_H on the centre plane at the first three measured stations behind the building, offset
per station. The model follows the measured profile closely above roof height and in the recovering wake; the
near-ground deficit immediately behind the building is where the closure does least well.
