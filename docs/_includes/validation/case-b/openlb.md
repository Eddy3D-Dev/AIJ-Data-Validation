OpenLB (Eddy3D's `eddy3dWind`: Smagorinsky, third-order regularised D3Q19, image `1.9.3-r6`, CPU build) solved the experiment with the same fitted inflow as OpenFOAM 12 and probed the same measured points, at $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$ ($$H/12.5$$), 2.6 million cells, 33 min on 24 threads of one node (55 MLUPS). $$H/20$$ costs about 16 times the cell-steps.

{% include figure.html name="case-b-engine-comparison.png" alt="Measured vs modelled U and V, Case B, one row per engine" caption="<strong>Figure 4.</strong> Case B, measured vs modelled $$U$$ and $$V$$ on the same points, one row per engine: OpenFOAM 12, OpenLB and FluidX3D. FluidX3D's hollow points are the near-ground heights it is not scored on." %}

| Quantity | n | FAC2 | FB | hit rate | R | OpenFOAM FAC2 / hit rate / R |
|---|---|---|---|---|---|---|
| $$U/U_H$$, all points | 224 | 0.42 | +0.22 | 0.28 | 0.85 | 0.70 / 0.56 / 0.96 |
| $$U/U_H$$, points ≥ 2 cells above the floor | 95 | 0.61 | −0.00 | 0.53 | 0.93 | — |
| $$V/U_H$$ | 224 | 0.21 | — | 0.59 | 0.87 | 0.28 / 0.61 / 0.91 |
| $$W/U_H$$ | 224 | 0.32 | — | 0.70 | 0.80 | 0.54 / 0.81 / 0.93 |

- OpenLB meets the ground with a plain no-slip (bounce-back) wall at $$z = 0$$ and carries the roughness only in the inlet profile. In the undisturbed column at the windward face its $$U$$ is 0.61 of the inlet log law at the first node (half a cell up), 0.88 one cell up, 1.14 at 1.5, 1.10 at 2, 1.05 at 3 and 1.01 from 4.
- The slab's wall faces sit at $$z = 0$$ and $$19.2\thinspace\mathrm{m}$$ (the 20 m slab quantised to whole cells, 432 solid nodes). Until image `1.9.3-r6` the solver's lattice started at the domain's floor, which put the wall half a cell up; this run replaces the one made with that lattice.
- The resolved $$k$$ is 13 % of the measured one; $$k$$ is not compared.
- Reattachment length: $$L_r = 2.63\thinspace H$$; the field fits best sampled $$H/4$$ downstream (R 0.86 against 0.85).
- Control: with the lateral sign flipped, $$V$$'s R becomes −0.87; $$U$$ scrambled across the points drops R to 0.08.
- OpenLB's STL reader segfaults when lattice nodes sit on its octree planes; Eddy3D moves such a lattice by $$10^{-4}\thinspace\mathrm{d}x$$ (`LBMCaseXml`). With the ground row half a cell under the floor this case is clear of them as configured.

<details markdown="block">
<summary>Interpretation: OpenLB on Case B</summary>

- The near-zero model $$U$$ near the floor is the no-slip wall; above two cells FAC2 rises to 0.61 and FB vanishes.
- The solve is nearly steady: a steady log-law inflow at $$H/12.5$$ resolves almost no turbulence, so $$k$$ is not compared, and with nothing to entrain the wake runs displaced.
- Its frame is right.

</details>
