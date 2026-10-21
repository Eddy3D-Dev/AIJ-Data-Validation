OpenLB (Eddy3D's `eddy3dWind`: Smagorinsky, third-order regularised D3Q19, CPU image) solved the experiment with the same fitted inflow as OpenFOAM 12 and probed the same measured points, at $$\mathrm{d}x = 1.6\thinspace\mathrm{m}$$ ($$H/10$$), 1.3 million cells, 1.8 h on four threads. $$H/20$$ costs about 16 times the cell-steps on this image.

{% include figure.html name="case-a-engine-comparison.png" alt="Measured vs modelled U and V, Case A, one row per engine" caption="<strong>Figure 7.</strong> Case A, measured vs modelled $$U$$ and $$V$$ on the same points, one row per engine: OpenFOAM 12, OpenLB and FluidX3D. FluidX3D's hollow points are the near-ground heights it is not scored on." %}

| Quantity | n | FAC2 | FB | hit rate | R | OpenFOAM FAC2 / hit rate / R |
|---|---|---|---|---|---|---|
| $$U/U_H$$, all points | 186 | 0.43 | +0.40 | 0.37 | 0.76 | 0.82 / 0.59 / 0.96 |
| $$U/U_H$$, points ≥ 2 cells above the floor | 121 | 0.65 | +0.17 | 0.56 | 0.81 | — |
| $$V/U_H$$ | 186 | 0.17 | — | 0.62 | 0.65 | 0.35 / 0.89 / 0.96 |
| $$W/U_H$$ | 186 | 0.12 | — | 0.59 | 0.54 | 0.40 / 0.80 / 0.71 |

{% include nomenclature-scores.md %}

- OpenLB meets the ground with a plain no-slip (bounce-back) wall and carries the roughness only in the inlet profile. In the undisturbed column at the windward face its $$U$$ is 0.29 of the inlet log law one cell up, 0.69 at two, 0.95 at three and 1.02–1.07 from four. Case A's lowest plane sits 0.6 cells up.
- The resolved $$k$$ is 0.7 % of the measured one; $$k$$ is not compared.
- Reattachment length: $$L_r = 3.39\thinspace H$$ against OpenFOAM's 1.49.
- Control: with the lateral sign flipped, $$V$$'s R becomes −0.65; $$U$$ scrambled across the points drops R to 0.10.

<details markdown="block">
<summary>Interpretation: OpenLB on Case A</summary>

- The flat band of near-zero model $$U$$ in the OpenLB row of Figure 7 is the floor; above two cells FAC2 rises to 0.65 and FB falls to +0.17.
- The solve is nearly steady: a steady log-law inflow at $$H/10$$ resolves almost no turbulence, so $$k$$ is not compared, and with nothing to entrain the wake runs long.
- Its frame is right.

</details>
