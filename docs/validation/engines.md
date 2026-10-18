---
title: "OpenLB and FluidX3D"
parent: Validation
nav_order: 10
summary: "the lattice-Boltzmann engines on Cases A and B, and why they are not scored on C to E"
description: "OpenLB and FluidX3D against the tunnel for Cases A and B, and the measurements that make them not comparable on Cases C to E."
---

# OpenLB and FluidX3D
{: .no_toc }

Eddy3D's two lattice-Boltzmann engines were scored on Cases A and B, on the same points as OpenFOAM 12. They are not scored on Cases C to E; the measurements behind that are below. They have not been run on Cases F to M.

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Cases A and B, every engine on the same points

{% include figure.html name="cases-ab-engine-comparison.png" alt="Measured vs modelled U and V, Cases A and B, one row per engine" caption="<strong>Figure 1.</strong> Measured vs modelled U and V, Cases A and B, one row per engine." %}

## OpenLB

OpenLB (Eddy3D's `eddy3dWind`: Smagorinsky, third-order regularised D3Q19, CPU image) solved the same two experiments with the same fitted inflow and probed the same measured points, at dx = 1.6 m: H/10 for A, H/12.5 for B, 1.3 and 2.6 million cells, 1.8 h and 4.1 h on four threads. H/20 costs about 16 times the cell-steps on this image.

| case · quantity | n | FAC2 | FB | q | R | OpenFOAM FAC2 / q / R |
|---|---|---|---|---|---|---|
| A · U/U_H, all points | 186 | 0.43 | +0.40 | 0.37 | 0.76 | 0.82 / 0.59 / 0.96 |
| A · U/U_H, points ≥ 2 cells above the floor | 121 | 0.65 | +0.17 | 0.56 | 0.81 | — |
| A · V/U_H | 186 | 0.17 | — | 0.62 | 0.65 | 0.35 / 0.89 / 0.96 |
| A · W/U_H | 186 | 0.12 | — | 0.59 | 0.54 | 0.40 / 0.80 / 0.71 |
| B · U/U_H, all points | 224 | 0.38 | +0.28 | 0.29 | 0.79 | 0.70 / 0.56 / 0.96 |
| B · U/U_H, points ≥ 2 cells above the floor | 95 | 0.64 | −0.07 | 0.52 | 0.90 | — |
| B · V/U_H | 224 | 0.13 | — | 0.55 | 0.83 | 0.28 / 0.61 / 0.91 |
| B · W/U_H | 224 | 0.24 | — | 0.65 | 0.77 | 0.54 / 0.81 / 0.93 |

- OpenLB meets the ground with a plain no-slip (bounce-back) wall and carries the roughness only in the inlet profile. In the undisturbed column at the windward face its U is 0.29 of the inlet log law one cell up, 0.69 at two, 0.95 at three and 1.02–1.07 from four. Case A's lowest plane sits 0.6 cells up.
- The resolved k is 0.7 % (A) and 10 % (B) of the measured one; k is not compared.
- Reattachment length, Case A: L_r = 3.39 H against OpenFOAM's 1.49. Case B: the field fits best sampled H/2 downstream.
- Controls: with the lateral sign flipped, V's R becomes −0.65 (A) and −0.83 (B); U scrambled across the points drops R to 0.10.
- OpenLB's STL reader segfaults when lattice nodes sit exactly on its octree planes, as in Case B at this spacing; Eddy3D moves such a lattice by 10⁻⁴ dx (`LBMCaseXml`).

<details markdown="block">
<summary>Interpretation: OpenLB on Cases A and B</summary>

- The flat band of near-zero model U in the OpenLB row is the floor; above two cells FAC2 rises to 0.65 and FB falls to +0.17 (Case A).
- The solve is nearly steady: a steady log-law inflow at H/10 resolves almost no turbulence, so k is not compared, and with nothing to entrain the wakes run long (A) or displaced (B).
- Its frame is right.

</details>

## FluidX3D

FluidX3D (Eddy3D's GPU lattice-Boltzmann engine: D3Q19 with Smagorinsky LES) solved both experiments at dx = H/64 (2.5 mm and 3.125 mm; 117 and 121 million cells) with the same fitted log-law inflow, averaging over 200 H/U_H after 40 of spin-up (A) and over 500 after 100 (B). Each run has an empty-domain control on the same lattice, and a point is scored only at a height where that control holds the imposed log law within 5 %: 116 of Case A's 186 points and 88 of Case B's 224.

| case · quantity, comparable heights | n | FAC2 | FB | q | R | OpenFOAM on the same points: FAC2 / q / R |
|---|---|---|---|---|---|---|
| A · U/U_H | 116 | 0.60 | +0.41 | 0.57 | 0.84 | 0.85 / 0.73 / 0.95 |
| A · V/U_H | 116 | 0.26 | — | 0.75 | 0.85 | 0.27 / 0.90 / 0.95 |
| A · W/U_H | 116 | 0.22 | — | 0.41 | 0.59 | 0.49 / 0.79 / 0.93 |
| B · U/U_H | 88 | 0.64 | +0.26 | 0.57 | 0.95 | 0.78 / 0.68 / 0.97 |
| B · W/U_H | 88 | 0.48 | — | 0.32 | 0.85 | 0.78 / 0.69 / 0.95 |

- FluidX3D meets the ground with a bounce-back wall and no roughness wall function. In the empty domain the flow at Case A's lowest plane (z = 0.01 m, 4 cells up) reads 0.52 of the imposed log law on average, and 0.86 at z = 0.04 m; Case B's three lowest heights read 0.77, 0.58 and 0.93. Those points are scored separately (`velocity.*.excluded`) and drawn hollow in the figure.
- Empty-domain control on the comparable points, Case A, U: FAC2 0.77, FB −0.26, hit rate 0.59, R 0.51. The solved field: FAC2 0.60, FB +0.41, hit rate 0.57, R 0.84.
- Empty-domain control, Case B, U: FAC2 0.56, R 0.81. The solved field: FAC2 0.64, R 0.95.
- Case B's V is not a headline score: all 88 comparable points lie on the centre plane, where the mean V is zero by symmetry.
- Control: with the lateral sign flipped, Case A's V correlation becomes −0.85.

<details markdown="block">
<summary>Interpretation: FluidX3D on Cases A and B</summary>

- The excluded points are the floor again.
- On Case A, the approach flow alone scores better on U (FAC2, FB and hit rate); only the correlation shows the building's effect.
- On Case B the solved field beats its approach flow on every U statistic.
- Its frame is right.

</details>

## Why OpenLB is not scored on C to E

Cases C, D and E measure only at pedestrian height. A point is scoreable on OpenLB only once it sits three to four cells above its no-slip floor. On the A and B runs at dx = 1.6 m, read in the undisturbed column at the heights the other cases measure at:

| the other case's height | cells above the floor | U / inlet log law (A run, B run) |
|---|---|---|
| Case D, z/H = 0.02 | below the first fluid node | 0.11, 0.13 — no prediction |
| Case C, z = 0.1 D | 1–1.25 | 0.29, 0.40 |
| Case E, 2 m among ~6 m buildings (z/H ≈ 0.33) | 3.3–4.1 | 1.00, 1.06 |

A 2 m pedestrian plane needs dx ≤ 0.5 m: 3.2 times finer in every direction, about 33 times the cells and 105 times the cell-steps over the same domain. The Case C array and the Niigata district are larger domains than Case A's. This CPU image does not run that in useful time; a GPU run at dx ≤ 0.5 m would decide it.

## Why FluidX3D is not scored on C to E

In the empty-domain run at H/64, 4–6 H downstream of the inlet (where the buildings stand), the flow at the heights the other cases measure at reads, as a fraction of the imposed log law (mean across a span of ±H):

| the other case's height | cells above the floor at H/64 | U / log law |
|---|---|---|
| Case D, z/H = 0.02 | 1.3 | 0.37–0.53 |
| Case C, z/H = 0.10 | 6.4 | 0.58–0.68 |
| Case E, 2 m among ~6 m buildings (z/H ≈ 0.33) | 21 | 0.91–0.99 |

- At H/32 the same height reads 0.74–0.80 (3.2 cells up).
- At H/64 the near-wall flow forms stationary streaks, and across the span the ratio at z/H = 0.10 runs from 0.24 to 0.88 (4 H downstream).
- Case E's height reads 0.91–0.99 at Case A's lattice. The Niigata district fits on this GPU only at about 1.6 cells per 2 m (an estimate from the lattice sizes, not a run).

FluidX3D has no ground wall function; scoring Cases C to E needs one in the engine.

<details markdown="block">
<summary>Interpretation: FluidX3D on Cases C to E</summary>

- The ground causes the low ratios, and refining the lattice lowers them: the ratio at z/H = 0.10 is 0.74–0.80 at H/32 and 0.58–0.68 at H/64.
- Case E's height comes closest (0.91–0.99).

</details>
