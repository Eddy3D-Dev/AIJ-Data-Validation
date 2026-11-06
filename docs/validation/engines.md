---
title: "OpenLB and FluidX3D"
parent: Validation
nav_order: 3
summary: "the two lattice-Boltzmann engines: how they are run, and why they are not scored on C to E"
description: "How Eddy3D runs OpenLB and FluidX3D, what limits them near the ground, and the measurements behind their status on Cases C to E."
---

# OpenLB and FluidX3D
{: .no_toc }

Eddy3D's two lattice-Boltzmann engines were scored on Cases A and B, on the same points as OpenFOAM 12; their scores and figures are on the [Case A]({{ '/cases/case-a/validation/' | relative_url }}) and [Case B]({{ '/cases/case-b/validation/' | relative_url }}) Validation pages. They are not scored on Cases C to E: OpenLB is not comparable at the 2 m these cases measure at, and FluidX3D, whose ground wall function holds that height in an empty-domain control, has not been run on them. The measurements are below, and each case's page says it for its own height. They have not been run on Cases F to M.

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
- Eddy3D's OpenLB has had an opt-in ground wall model since 2026-10-20: OpenLB's wall-modelled boundary with a power law, Spalding's law, or a rough log law with the inflow's $$z_0$$. The A and B runs predate it.
- OpenLB's STL reader segfaults when lattice nodes sit exactly on its octree planes, as in Case B at this spacing; Eddy3D moves such a lattice by $$10^{-4}\thinspace\mathrm{d}x$$ (`LBMCaseXml`).

## FluidX3D

FluidX3D (Eddy3D's GPU lattice-Boltzmann engine: D3Q19 with Smagorinsky LES) solved both experiments at $$\mathrm{d}x = H/64$$ (2.5 mm and 3.125 mm; 117 and 121 million cells) with the same fitted log-law inflow, averaging over 200 $$H/U_H$$ after 40 of spin-up (A) and over 500 after 100 (B). Each run has an empty-domain control on the same lattice, and a point is scored only at a height where that control holds the imposed log law within 5 %: 116 of Case A's 186 points and 88 of Case B's 224.

- In these runs FluidX3D meets the ground with a bounce-back wall and no roughness wall function. In the empty domain the flow at Case A's lowest plane ($$z = 0.01\thinspace\mathrm{m}$$, 4 cells up) reads 0.52 of the imposed log law on average, and 0.86 at $$z = 0.04\thinspace\mathrm{m}$$; Case B's three lowest heights read 0.77, 0.58 and 0.93. Those points are scored separately (`velocity.*.excluded`).
- Eddy3D's FluidX3D has had an opt-in ground wall function since 2026-11-05: the velocity three cells up gives, through the rough log law with the inflow's $$z_0$$, the shear stress the floor takes and the velocity the first fluid node is relaxed toward. The A and B runs predate it.

## Why OpenLB is not scored on C to E

Cases C, D and E measure only at 2 m full scale ($$z = 0.1\thinspace D$$ at 1:100, $$z/H = 0.02$$ at 1:400, 2 m in the Niigata district): 1.25 cells above the ground at the A and B runs' $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$. A point is scored only where every point at its height in an empty-domain control is within 5 % of the imposed log law, the bar FluidX3D's points meet.

The control: an empty domain 32 m wide and 80 m tall, $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$, each case's own inflow at full scale (Case E: a log law fitted to its approach-flow profile below 60 m), the CPU image `openlb-wind:1.9.3-r4`, read on three lines every 16 m where the case's points would sit. $$U$$ at 2 m over the imposed log law, mean (range over the points), and the lowest height at which every point is within 5 %:

| | Case C | Case D | Case E |
|---|---|---|---|
| distance from the inlet | 80–320 m | 770–1010 m | 350–650 m |
| bounce-back | 0.30 (0.23–0.39) | 0.26 (0.10–0.41) | 0.23 (0.16–0.35) |
| wall model, power law | 1.00 (0.92–1.06) | 1.03 (0.95–1.11) | 0.87 (0.80–1.04) |
| wall model, rough law | 0.99 (0.91–1.05) | 1.01 (0.93–1.08) | 0.94 (0.87–1.07) |
| lowest height with every point within 5 %, bounce-back | 19.2 m (12 cells) | 64 m (40 cells) | 48 m (30 cells) |
| lowest height with every point within 5 %, either wall law | 12.8 m (8 cells) | none | 32 m (20 cells) |

{% include nomenclature.md %}

- With either wall law the 2 m layer runs up to 6 % over the log law in the first 100 m and 7–14 % under it 300–600 m in, in all three cases; in Case D the rough law is back within 4 % beyond 750 m.
- Beyond about 450 m from the inlet the control varies across its span at every height: at 12.8 m in Case D, 0.69–1.07 with bounce-back and 0.84–1.09 with the rough law.
- On 24 threads the wall model takes 6.7–6.9 times the bounce-back run's wall time. The CUDA build carries it.
- Scripts, probes and run times: Eddy3D, `testing/aij-openlb-ground-wall/`.

<details markdown="block">
<summary>Interpretation: OpenLB on Cases C to E</summary>

- The wall model removes the collapsed floor: the 2 m mean goes from a quarter of the log law to within 1 % of it in Cases C and D.
- What keeps the cases unscored is the wall-modelled layer's adjustment along the fetch, about ±10 % at 1.25 cells.
- In Case C every point clears the bar from 8 cells up. If the layer behaves the same in cells at a finer lattice, a 2 m plane needs $$\mathrm{d}x \le 0.25\thinspace\mathrm{m}$$, a GPU lattice for these domains.
- The Case D and E controls do not isolate the ground at their distance from the inlet; a control as wide and tall as the case's own domain would.

</details>

## Why FluidX3D is not yet scored on C to E

The OpenLB control above, on FluidX3D (Eddy3D's pinned commit 8986874e, FP16S, an Apple M2 Max): open faces (slip sides and top, a pressure outlet) and a steady log-law inflow, the kind the A and B runs use, in the 32 m wide domain and in one 96 m wide. $$U$$ at 2 m over the imposed log law, mean (range over the points):

| | Case C | Case D | Case E |
|---|---|---|---|
| distance from the inlet | 80–320 m | 770–1010 m | 350–650 m |
| bounce-back, 32 m wide | 0.48 (0.38–0.60) | 0.53 (0.47–0.60) | 0.42 (0.30–0.52) |
| ground wall function, 32 m wide | 1.00 (0.98–1.01) | 1.02 (0.95–1.06) | 0.98 (0.92–1.01) |
| bounce-back, 96 m wide | 0.44 (0.38–0.55) | 0.46 (0.20–0.74) | 0.36 (0.20–0.56) |
| ground wall function, 96 m wide | 1.00 (0.99–1.01) | 0.96 (0.954–0.969) | 0.99 (0.98–0.99) |

{% include nomenclature.md %}

- With the ground wall function every 2 m point is within 5 % of the log law in all three cases in the 96 m wide domain. In the 32 m wide one only Case C's are: the D and E points stray beyond about 450 m from the inlet, where the three lines drift apart, as OpenLB's do in that domain.
- With synthetic turbulence at the inlet, Eddy3D's default for FluidX3D, the 2 m layer runs fast: 1.14 (1.12–1.18) and 1.18 (1.13–1.24) in Case D's two domains, 1.05 (0.99–1.10) in Case C's narrow one. Only Case E's wide domain holds every point within 5 % (0.96–1.03).
- The 2 m means at the averaging's halfway point and at its end agree within 0.003 in every steady run. With the steady inflow the wall-function runs took 2–6 % longer than their bounce-back twins (whole runs of 17–76 s, the compile included).
- The Niigata district fits on the GPU of the A and B runs at up to about 1.6 cells per 2 m (an estimate from the lattice sizes); $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$ is 1.25.
- FluidX3D has not been run on Cases C to E.
- Scripts, probes and run times: Eddy3D, `testing/aij-fluidx3d-ground-wall/`.

<details markdown="block">
<summary>Interpretation: FluidX3D on Cases C to E</summary>

- The ground wall function removes the collapsed floor: with the steady inflow the 2 m mean goes from 0.36–0.53 of the log law to 0.96–1.02.
- With the steady inflow the ground no longer keeps these cases unscored; a run at $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$ with the wall function is scored wherever its own control holds the bar.
- The 32 m domain's drift in Cases D and E is the domain, not the ground: 96 m wide, the same ground holds.

</details>
