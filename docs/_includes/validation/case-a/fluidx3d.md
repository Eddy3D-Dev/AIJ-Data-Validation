FluidX3D (Eddy3D's GPU lattice-Boltzmann engine: D3Q19 with Smagorinsky LES) solved the experiment at $$\mathrm{d}x = H/64$$ (2.5 mm, 117 million cells) with the same fitted log-law inflow, averaging over 200 $$H/U_H$$ after 40 of spin-up. The run has an empty-domain control on the same lattice, and a point is scored only at a height where that control holds the imposed log law within 5 %: 116 of the 186 points. Its row is in Figure 7.

| Quantity, comparable heights | n | FAC2 | FB | hit rate | R | OpenFOAM on the same points: FAC2 / hit rate / R |
|---|---|---|---|---|---|---|
| $$U/U_H$$ | 116 | 0.60 | +0.41 | 0.57 | 0.84 | 0.85 / 0.73 / 0.95 |
| $$V/U_H$$ | 116 | 0.26 | — | 0.75 | 0.85 | 0.27 / 0.90 / 0.95 |
| $$W/U_H$$ | 116 | 0.22 | — | 0.41 | 0.59 | 0.49 / 0.79 / 0.93 |

{% include nomenclature-scores.md %}

- FluidX3D meets the ground with a bounce-back wall and no roughness wall function. In the empty domain the flow at the lowest plane ($$z = 0.01\thinspace\mathrm{m}$$, 4 cells up) reads 0.52 of the imposed log law on average, and 0.86 at $$z = 0.04\thinspace\mathrm{m}$$. Those points are scored separately (`velocity.*.excluded`) and drawn hollow in Figure 7.
- Empty-domain control on the comparable points, $$U$$: FAC2 0.77, FB −0.26, hit rate 0.59, R 0.51. The solved field: FAC2 0.60, FB +0.41, hit rate 0.57, R 0.84.
- Control: with the lateral sign flipped, the $$V$$ correlation becomes −0.85.

<details markdown="block">
<summary>Interpretation: FluidX3D on Case A</summary>

- The excluded points are the floor again.
- The approach flow alone scores better on $$U$$ (FAC2, FB and hit rate); only the correlation shows the building's effect.
- Its frame is right.

</details>
