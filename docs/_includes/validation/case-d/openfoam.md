All three headings: 3.6 million cells at 1:400 on a cylinder domain, 3000 iterations, the 66 measured thermistor points and the 33 split-fibre points at $$z/H = 0.02$$.

### Measured against modelled

{% include figure.html name="case-d-openfoam-agreement.png" alt="Case D, measured vs modelled" caption="<strong>Figure 2.</strong> Case D, wind directions 0°, 22.5° and 45°: measured against modelled speed on the thermistor plane, and at the split-fibre points (0° only). The dots take the colour of their group in Figure 1." %}

<details markdown="block">
  <summary>Scores for all three headings and both instruments</summary>

| | n | FAC2 | FB | hit rate | R |
|---|---|---|---|---|---|
| WD 0° · thermistor $$V_{\mathrm{s}}$$ · $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | 66 | 0.73 | +0.21 | 0.48 | 0.80 |
| WD 0° · thermistor $$V_{\mathrm{s}}$$ · $$\lvert\mathbf{U}\rvert$$ | 66 | 0.67 | +0.36 | 0.39 | 0.81 |
| WD 22.5° · thermistor $$V_{\mathrm{s}}$$ · $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | 66 | 0.92 | +0.05 | 0.67 | 0.80 |
| WD 22.5° · thermistor $$V_{\mathrm{s}}$$ · $$\lvert\mathbf{U}\rvert$$ | 66 | 0.82 | +0.15 | 0.64 | 0.78 |
| WD 22.5° · the same, rotation sense mirrored (control) | 66 | 0.74 | +0.05 | 0.36 | 0.40 |
| WD 45° · thermistor $$V_{\mathrm{s}}$$ · $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | 66 | 0.89 | +0.09 | 0.71 | 0.85 |
| WD 45° · thermistor $$V_{\mathrm{s}}$$ · $$\lvert\mathbf{U}\rvert$$ | 66 | 0.82 | +0.17 | 0.70 | 0.84 |
| WD 45° · the same, rotation sense mirrored (control) | 66 | 0.70 | +0.09 | 0.24 | 0.17 |
| WD 0° · split fibre $$\lvert\mathbf{U}\rvert$$ · $$\lvert\mathbf{U}\rvert$$ | 33 | 0.76 | +0.07 | 0.52 | 0.85 |
| WD 0° · split fibre $$U$$ · $$U$$ | 33 | 0.48 | +0.67 | 0.52 | 0.95 |

{% include nomenclature-scores.md %}

</details>

- Thermistor plane: R 0.80–0.85 at all three headings. Split-fibre $$\lvert\mathbf{U}\rvert$$: R 0.85.
- Split-fibre points (33): $$\lvert\mathbf{U}\rvert$$ FB +0.07. Thermistor (66): FB +0.21 with $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ and +0.36 with $$\lvert\mathbf{U}\rvert$$. In the tunnel the thermistor reads 1.34 times the split-fibre $$\lvert\mathbf{U}\rvert$$ over the same 33 points.
- Split-fibre streamwise $$U$$: FB +0.67, R 0.95.
- Rotation sense at 22.5° and 45°: the array is symmetric about $$y = 0$$, so a wind turned toward $$+y$$ and one turned toward $$-y$$ give mirror-image fields. The data paper's Figure 4 draws $$+y$$.
  - Figure 4's sense: R 0.80 and FAC2 0.92 at 22.5°; R 0.85 and FAC2 0.89 at 45°.
  - Mirrored sense (control): R 0.40 at 22.5°, 0.17 at 45°.
  - FB against the thermistor with $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$: +0.05 and +0.09.
- At 0° the 66 thermistor values are 33 mirror pairs (33 independent values); the mirror control is equal to the score there.
- FB is positive when the model is low.

<details markdown="block">
<summary>Interpretation: Case D pattern, instruments and rotation sense</summary>

- The pattern is right. The frame check (R above 0.5 at 0°) passes with room to spare; a prior Eddy3D attempt at this case scored R 0.10 ([Known data issues]({{ '/known-data-issues/' | relative_url }})).
- Against the instrument that measures what RANS computes, the model is nearly unbiased (split-fibre $$\lvert\mathbf{U}\rvert$$, FB +0.07).
- Most of the thermistor gap is the instrument: the thermistor reads 1.34 times the split-fibre $$\lvert\mathbf{U}\rvert$$ in the tunnel itself.
- The model's streamwise component is low ($$U$$ FB +0.67, R 0.95) while its $$\lvert\mathbf{U}\rvert$$ is not: more of the model's near-ground speed is in the lateral and vertical components than the tunnel's.
- At 22.5° and 45° the solved fields corroborate the rotation sense that the measurements alone cannot decide. At both headings the model is also nearly unbiased against the thermistor (FB +0.05 and +0.09 with $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$).

</details>
