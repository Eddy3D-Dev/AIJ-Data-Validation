OpenLB (Eddy3D's `eddy3dWind`: Smagorinsky, third-order regularised D3Q19, image `1.9.3-r6`, CPU build) solved the experiment with the same fitted inflow as OpenFOAM 12 and probed the same measured points, at $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$ ($$H/10$$), 1.3 million cells, 13 min on 24 threads of one node (54 MLUPS). $$H/20$$ costs about 16 times the cell-steps.

{% include figure.html name="case-a-engine-comparison.png" alt="Measured vs modelled U and V, Case A, one row per engine" caption="<strong>Figure 7.</strong> Case A, measured vs modelled $$U$$ and $$V$$ on the same points, one row per engine: OpenFOAM 12, OpenLB and FluidX3D. FluidX3D's hollow points are the near-ground heights it is not scored on." %}

| Quantity | n | FAC2 | FB | hit rate | R | OpenFOAM FAC2 / hit rate / R |
|---|---|---|---|---|---|---|
| $$U/U_H$$, all points | 186 | 0.47 | +0.38 | 0.38 | 0.78 | 0.82 / 0.59 / 0.96 |
| $$U/U_H$$, points ≥ 2 cells above the floor | 121 | 0.65 | +0.22 | 0.56 | 0.80 | — |
| $$V/U_H$$ | 186 | 0.25 | — | 0.66 | 0.77 | 0.35 / 0.89 / 0.96 |
| $$W/U_H$$ | 186 | 0.18 | — | 0.56 | 0.57 | 0.40 / 0.80 / 0.71 |

- OpenLB meets the ground with a plain no-slip (bounce-back) wall at $$z = 0$$ and carries the roughness only in the inlet profile. In the undisturbed column at the windward face its $$U$$ is 0.60 of the inlet log law at the first node (half a cell up), 0.88 one cell up, 1.14 at 1.5, 1.10 at 2, 1.04 at 3 and 1.01 from 4. Case A's lowest plane sits 0.6 cells up.
- The building's wall faces sit at $$z = 0$$ and $$16\thinspace\mathrm{m}$$ (250 solid nodes). Until image `1.9.3-r6` the solver's lattice started at the domain's floor, which put the wall half a cell up and the roof a row short (14.4 m); this run replaces the one made with that lattice.
- The resolved $$k$$ is 1 % of the measured one; $$k$$ is not compared.
- Reattachment length: $$L_r = 2.80\thinspace H$$ against OpenFOAM's 1.49; the field fits best sampled $$H/2$$ downstream (R 0.81 against 0.78).
- Control: with the lateral sign flipped, $$V$$'s R becomes −0.77; $$U$$ scrambled across the points drops R to 0.10.

<details markdown="block">
<summary>Interpretation: OpenLB on Case A</summary>

- The near-zero model $$U$$ at the floor in the OpenLB row of Figure 7 is the no-slip wall; above two cells FAC2 rises to 0.65 and FB falls to +0.22.
- The solve is nearly steady: a steady log-law inflow at $$H/10$$ resolves almost no turbulence, so $$k$$ is not compared, and with nothing to entrain the wake runs long.
- Its frame is right.

</details>
