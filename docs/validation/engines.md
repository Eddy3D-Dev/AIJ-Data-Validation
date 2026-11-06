---
title: "OpenLB and FluidX3D"
parent: Validation
nav_order: 3
summary: "the two lattice-Boltzmann engines: how they are run, and why they are not scored on C to E"
description: "How Eddy3D runs OpenLB and FluidX3D, what limits them near the ground, and the measurements behind their status on Cases C to E."
---

# OpenLB and FluidX3D
{: .no_toc }

Eddy3D's two lattice-Boltzmann engines were scored on Cases A and B, on the same points as OpenFOAM 12; their scores and figures are on the [Case A]({{ '/cases/case-a/validation/' | relative_url }}) and [Case B]({{ '/cases/case-b/validation/' | relative_url }}) Validation pages. They are not scored on Cases C to E, which measure at 2 m. In empty-domain controls on `openlb-wind:1.9.3-r4` and `-r5`, OpenLB's ground wall model brings the mean at that height to within 4 % of the log law but holds every point within 5 % in none of the three, and FluidX3D's ground wall function holds every point in all three; neither engine has been run on these cases. The measurements are below, and each case's page says it for its own height. They have not been run on Cases F to M.

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

The first control: an empty domain 32 m wide and 80 m tall, $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$, each case's own inflow at full scale (Case E: a log law fitted to its approach-flow profile below 60 m), the CPU image `openlb-wind:1.9.3-r4`, read on three lines every 16 m where the case's points would sit, after twice the time the 2 m layer takes to cross the domain and averaged over half of it. $$U$$ at 2 m over the imposed log law, mean (range over the points), and the lowest height at which every point is within 5 %:

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

The second control: the same on the image's CUDA build, in a domain 256 m wide and 320 m tall read on seven lines, 1100 m long for Cases C and E and 1600 m for Case D (warmed up for 1.5 crossings), so that the outlet stays clear of the points:

| | Case C | Case D | Case E |
|---|---|---|---|
| distance from the inlet | 80–320 m | 770–1010 m | 350–650 m |
| bounce-back | 0.26 (0.05–0.44) | 0.25 (0.18–0.32) | 0.23 (0.11–0.34) |
| wall model, rough law | 1.04 (1.02–1.07) | 1.00 (0.949–1.055) | 1.03 (1.012–1.046) |
| lowest height with every point within 5 %, bounce-back | 19.2 m (12 cells) | 19.2 m (12 cells) | 32 m (20 cells) |
| lowest height with every point within 5 %, rough law | 2.4 m (1.5 cells) | 8 m (5 cells) | 2 m (1.25 cells) |

- In this domain the rough law's 2 m layer does not sink under the log law along the fetch: Case C's reads 1.06 at the inlet and 0.99 at 750 m. Width and height changed together, so which of the two does it is not measured.
- Case C: the 9 points over 5 % (of 112) all sit within 144 m of the inlet, where the layer is still coming down from its overshoot at the inlet (1.068 at 80 m); 160–400 m from the inlet every point is within 5 % (1.014–1.047).
- Case E: every point is within 5 %, the highest (1.046) at the window's upstream end, and `1.9.3-r5` reproduces that within 0.0004. Averaged over two crossings instead of half of one, five points are just over 5 % (0.985–1.0504): over the second crossing the 2 m mean was 1.008 against 1.028 over the first, and the points spread from 0.94 to 1.06 (32 of 133 over 5 %, 14 under).
- Case D: 4 points over 5 % and 1 under (of 105; 0.949–1.055), on a pattern across the span that holds along the whole window and is symmetric about the centre line: the centre line reads 0.956, the lines 64 m either side 1.027. At any distance in the window the seven lines span 6.6–10.0 %. The outlet's rise starts about 1450 m from the inlet.
- A pressure outlet speeds the 2 m layer up over its last 260–380 m (0.8–1.2 domain heights): 400 m and 720 m long, as in the first control, this domain read up to 1.43 at Case C's points and 1.25 at Case E's.
- Across the span the flow is symmetric about the centre line; at any distance in Case C's and Case E's windows the seven lines span at most 2.1 %.
- The CUDA build (fp32) reproduces the CPU's fp64 run of Case C's narrow domain within $$2.1 \times 10^{-4}$$ in $$U$$ at all 1080 points.
- On `1.9.3-r4` and `-r5` OpenLB's bounce-back wall sat half a cell (0.8 m) above $$z = 0$$, where the inflow and the probes start, and the wall model's wall at $$z = 0$$; the bounce-back rows above are read at $$z = 2\thinspace\mathrm{m}$$, 1.2 m above their wall. `1.9.3-r6` (2026-11-06) moves the lattice's ground row half a cell down, so both walls are at $$z = 0$$: on Case C's first control, 200–400 m from the inlet, the 2 m mean goes from 0.30 to 0.48 with bounce-back and from 0.955 to 0.80 with the rough law (Eddy3D, `docs/domain/lbm-gpu-ml.md`). The controls above predate it.
- With `1.9.3-r4` the wall model took 6.7–6.9 times the bounce-back run's wall time on 24 CPU threads and 3.6–4.3 times on one GPU; `1.9.3-r5` (2026-11-06) keeps its collision on the boundary row, and Case E's wide control took 2.6 times on the same GPU (4268 s against 1611 s).
- Scripts, probes, figures and run times: Eddy3D, `testing/aij-openlb-ground-wall/`.

<details markdown="block">
<summary>Interpretation: OpenLB on Cases C to E</summary>

- The wall model removes the collapsed floor: in the wide domain the 2 m mean goes from a quarter of the log law to within 4 % of it.
- The narrow domain's ±10 % along the fetch was the domain's, not the ground's.
- An OpenLB run of these cases ends at least 1.2 domain heights past its last scored point, and its own control is the one that counts.
- Case E: the half-crossing average met the bar, and nothing in it warned of the change: no point moved more than 0.003 over its second half. The layer changed after three crossings, so a control that can admit a 2 m point averages over several crossings after that, and so does the case run it admits.
- Case C: over half a crossing, what keeps it unscored is the first 64 m of its window, where the wall-modelled layer is still settling from the inlet; whether the rest of the window holds over several crossings is not measured.
- Case D: with the outlet clear of its points, what keeps it unscored is the pattern across the span; being symmetric about the centre, it is the 256 m domain's, and a domain as wide as the case's (about 1 km) is not measured.

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
