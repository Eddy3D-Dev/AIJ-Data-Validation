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
- Eddy3D's OpenLB has had an opt-in ground wall model since 2026-10-20: OpenLB's wall-modelled boundary with a power law, Spalding's law, or a rough log law with the inflow's $$z_0$$. The A and B runs predate it.
- OpenLB's STL reader segfaults when lattice nodes sit exactly on its octree planes, as in Case B at this spacing; Eddy3D moves such a lattice by $$10^{-4}\thinspace\mathrm{d}x$$ (`LBMCaseXml`).

## FluidX3D

FluidX3D (Eddy3D's GPU lattice-Boltzmann engine: D3Q19 with Smagorinsky LES) solved both experiments at $$\mathrm{d}x = H/64$$ (2.5 mm and 3.125 mm; 117 and 121 million cells) with the same fitted log-law inflow, averaging over 200 $$H/U_H$$ after 40 of spin-up (A) and over 500 after 100 (B). Each run has an empty-domain control on the same lattice, and a point is scored only at a height where that control holds the imposed log law within 5 %: 116 of Case A's 186 points and 88 of Case B's 224.

- FluidX3D meets the ground with a bounce-back wall and no roughness wall function. In the empty domain the flow at Case A's lowest plane ($$z = 0.01\thinspace\mathrm{m}$$, 4 cells up) reads 0.52 of the imposed log law on average, and 0.86 at $$z = 0.04\thinspace\mathrm{m}$$; Case B's three lowest heights read 0.77, 0.58 and 0.93. Those points are scored separately (`velocity.*.excluded`).

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
