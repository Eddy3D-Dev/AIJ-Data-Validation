FluidX3D (Eddy3D's GPU lattice-Boltzmann engine: D3Q19 with Smagorinsky LES) solved the experiment at $$\mathrm{d}x = H/64$$ (3.125 mm, 121 million cells) with the same fitted log-law inflow, averaging over 500 $$H/U_H$$ after 100 of spin-up. The run has an empty-domain control on the same lattice, and a point is scored only at a height where that control holds the imposed log law within 5 %: 88 of the 224 points. Its row is in Figure 4.

| Quantity, comparable heights | n | FAC2 | FB | hit rate | R | OpenFOAM on the same points: FAC2 / hit rate / R |
|---|---|---|---|---|---|---|
| $$U/U_H$$ | 88 | 0.64 | +0.26 | 0.57 | 0.95 | 0.78 / 0.68 / 0.97 |
| $$W/U_H$$ | 88 | 0.48 | — | 0.32 | 0.85 | 0.78 / 0.69 / 0.95 |

- FluidX3D meets the ground with a bounce-back wall and no roughness wall function. In the empty domain the three lowest heights read 0.77, 0.58 and 0.93 of the imposed log law. Those points are scored separately (`velocity.*.excluded`) and drawn hollow in Figure 4.
- Empty-domain control, $$U$$: FAC2 0.56, R 0.81. The solved field: FAC2 0.64, R 0.95.
- $$V$$ is not a headline score: all 88 comparable points lie on the centre plane, where the mean $$V$$ is zero by symmetry.

<details markdown="block">
<summary>Interpretation: FluidX3D on Case B</summary>

- The excluded points are the floor again.
- The solved field beats its approach flow on every $$U$$ statistic.
- Its frame is right.

</details>
