---
title: "OpenLB and FluidX3D"
parent: Validation
nav_order: 3
summary: "the two lattice-Boltzmann engines: how they are run, and why they are not scored on C to E"
description: "How Eddy3D runs OpenLB and FluidX3D, what limits them near the ground, and the measurements that make them not comparable on Cases C to E."
---

# OpenLB and FluidX3D
{: .no_toc }

Eddy3D's two lattice-Boltzmann engines were scored on Cases A and B, on the same points as OpenFOAM 12; their scores and figures are on the [Case A]({{ '/cases/case-a/validation/' | relative_url }}) and [Case B]({{ '/cases/case-b/validation/' | relative_url }}) Validation pages. They are not scored on Cases C to E; the measurements behind that are below, and each case's page says it for its own height. They have not been run on Cases F to M.

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## OpenLB

OpenLB (Eddy3D's `eddy3dWind`: Smagorinsky, third-order regularised D3Q19, CPU image) solved the same two experiments with the same fitted inflow and probed the same measured points, at $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$: $$H/10$$ for A, $$H/12.5$$ for B, 1.3 and 2.6 million cells, 1.8 h and 4.1 h on four threads. $$H/20$$ costs about 16 times the cell-steps on this image.

- OpenLB meets the ground with a plain no-slip (bounce-back) wall and carries the roughness only in the inlet profile. In the undisturbed column at the windward face its $$U$$ is 0.29 of the inlet log law one cell up, 0.69 at two, 0.95 at three and 1.02–1.07 from four. Case A's lowest plane sits 0.6 cells up.
- OpenLB's STL reader segfaults when lattice nodes sit exactly on its octree planes, as in Case B at this spacing; Eddy3D moves such a lattice by $$10^{-4}\thinspace\mathrm{d}x$$ (`LBMCaseXml`).

## FluidX3D

FluidX3D (Eddy3D's GPU lattice-Boltzmann engine: D3Q19 with Smagorinsky LES) solved both experiments at $$\mathrm{d}x = H/64$$ (2.5 mm and 3.125 mm; 117 and 121 million cells) with the same fitted log-law inflow, averaging over 200 $$H/U_H$$ after 40 of spin-up (A) and over 500 after 100 (B). Each run has an empty-domain control on the same lattice, and a point is scored only at a height where that control holds the imposed log law within 5 %: 116 of Case A's 186 points and 88 of Case B's 224.

- FluidX3D meets the ground with a bounce-back wall and no roughness wall function. In the empty domain the flow at Case A's lowest plane ($$z = 0.01\thinspace\mathrm{m}$$, 4 cells up) reads 0.52 of the imposed log law on average, and 0.86 at $$z = 0.04\thinspace\mathrm{m}$$; Case B's three lowest heights read 0.77, 0.58 and 0.93. Those points are scored separately (`velocity.*.excluded`).

## Why OpenLB is not scored on C to E

Cases C, D and E measure only at pedestrian height. A point is scoreable on OpenLB only once it sits three to four cells above its no-slip floor. On the A and B runs at $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$, read in the undisturbed column at the heights the other cases measure at:

| the other case's height | cells above the floor | $$U$$ / inlet log law (A run, B run) |
|---|---|---|
| Case D, $$z/H = 0.02$$ | below the first fluid node | 0.11, 0.13 — no prediction |
| Case C, $$z = 0.1\thinspace D$$ | 1–1.25 | 0.29, 0.40 |
| Case E, 2 m among ~6 m buildings ($$z/H \approx 0.33$$) | 3.3–4.1 | 1.00, 1.06 |

{% include nomenclature.md %}

A 2 m pedestrian plane needs $$\mathrm{d}x \le 0.5\thinspace\mathrm{m}$$: 3.2 times finer in every direction, about 33 times the cells and 105 times the cell-steps over the same domain. The Case C array and the Niigata district are larger domains than Case A's. This CPU image does not run that in useful time; a GPU run at $$\mathrm{d}x \le 0.5\thinspace\mathrm{m}$$ would decide it.

## Why FluidX3D is not scored on C to E

In the empty-domain run at $$H/64$$, $$4\text{–}6\thinspace H$$ downstream of the inlet (where the buildings stand), the flow at the heights the other cases measure at reads, as a fraction of the imposed log law (mean across a span of $$\pm H$$):

| the other case's height | cells above the floor at $$H/64$$ | $$U$$ / log law |
|---|---|---|
| Case D, $$z/H = 0.02$$ | 1.3 | 0.37–0.53 |
| Case C, $$z/H = 0.10$$ | 6.4 | 0.58–0.68 |
| Case E, 2 m among ~6 m buildings ($$z/H \approx 0.33$$) | 21 | 0.91–0.99 |

{% include nomenclature.md %}

- At $$H/32$$ the same height reads 0.74–0.80 (3.2 cells up).
- At $$H/64$$ the near-wall flow forms stationary streaks, and across the span the ratio at $$z/H = 0.10$$ runs from 0.24 to 0.88 ($$4\thinspace H$$ downstream).
- Case E's height reads 0.91–0.99 at Case A's lattice. The Niigata district fits on this GPU only at about 1.6 cells per 2 m (an estimate from the lattice sizes).

FluidX3D has no ground wall function; scoring Cases C to E needs one in the engine.

<details markdown="block">
<summary>Interpretation: FluidX3D on Cases C to E</summary>

- The ground causes the low ratios, and refining the lattice lowers them: the ratio at $$z/H = 0.10$$ is 0.74–0.80 at $$H/32$$ and 0.58–0.68 at $$H/64$$.
- Case E's height comes closest (0.91–0.99).

</details>
