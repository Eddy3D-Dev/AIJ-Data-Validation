OpenLB (Eddy3D's `eddy3dWind`: Smagorinsky, third-order regularised D3Q19, CPU image) solved the experiment with the same fitted inflow as OpenFOAM 12 and probed the same measured points, at $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$ ($$H/12.5$$), 2.6 million cells, 4.1 h on four threads. $$H/20$$ costs about 16 times the cell-steps on this image.

{% include figure.html name="case-b-engine-comparison.png" alt="Measured vs modelled U and V, Case B, one row per engine" caption="<strong>Figure 6.</strong> Case B, measured vs modelled $$U$$ and $$V$$ on the same points, one row per engine: OpenFOAM 12, OpenLB and FluidX3D. FluidX3D's hollow points are the near-ground heights it is not scored on." %}

| Quantity | n | FAC2 | FB | hit rate | R | OpenFOAM FAC2 / hit rate / R |
|---|---|---|---|---|---|---|
| $$U/U_H$$, all points | 224 | 0.38 | +0.28 | 0.29 | 0.79 | 0.70 / 0.56 / 0.96 |
| $$U/U_H$$, points ≥ 2 cells above the floor | 95 | 0.64 | −0.07 | 0.52 | 0.90 | — |
| $$V/U_H$$ | 224 | 0.13 | — | 0.55 | 0.83 | 0.28 / 0.61 / 0.91 |
| $$W/U_H$$ | 224 | 0.24 | — | 0.65 | 0.77 | 0.54 / 0.81 / 0.93 |

{% include nomenclature-scores.md %}

- OpenLB meets the ground with a plain no-slip (bounce-back) wall and carries the roughness only in the inlet profile. In the undisturbed column at the windward face its $$U$$ is 0.29 of the inlet log law one cell up, 0.69 at two, 0.95 at three and 1.02–1.07 from four. 
- The resolved $$k$$ is 10 % of the measured one; $$k$$ is not compared.
- The wake is displaced: the field fits best sampled $$H/2$$ downstream.
- Control: with the lateral sign flipped, $$V$$'s R becomes −0.83; $$U$$ scrambled across the points drops R to 0.10.
- OpenLB's STL reader segfaults when lattice nodes sit exactly on its octree planes, as here at this spacing; Eddy3D moves such a lattice by $$10^{-4}\thinspace\mathrm{d}x$$ (`LBMCaseXml`).

<details markdown="block">
<summary>Interpretation: OpenLB on Case B</summary>

- The near-zero model $$U$$ near the floor is the no-slip wall; above two cells FAC2 rises to 0.64 and FB falls to −0.07.
- The solve is nearly steady: a steady log-law inflow at $$H/12.5$$ resolves almost no turbulence, so $$k$$ is not compared, and with nothing to entrain the wake runs displaced.
- Its frame is right.

</details>
