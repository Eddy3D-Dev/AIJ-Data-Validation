### Measured against modelled

{% include figure.html name="case-b-openfoam-agreement.png" alt="Measured vs modelled, Case B" caption="<strong>Figure 2.</strong> Case B, measured vs modelled $$U$$, $$V$$, $$W$$ and $$k$$, with the 1:1 line and, where the quantity does not change sign, the factor-of-two band. The dots take the colour of the line or plane they were measured on, as in Figure 1." %}

- Normalised by $$U_H$$. FB is positive when the model is low.
- Reattachment length behind the building: $$L_r/H$$ = 3.27.
- $$V$$ and $$W$$ change sign.
- The model's $$V$$ is 0 on the centre plane ($$y = 0$$, a symmetry plane); the tunnel measures small non-zero values there.

{% include figure.html name="case-b-openfoam-profiles.png" alt="Centre-plane profiles, Case B" caption="<strong>Figure 3.</strong> Case B, vertical profiles of $$U/U_H$$ on the centre plane at the first three measured stations behind the building, offset per station." %}

<details markdown="block">
<summary>Interpretation: Case B scores and profiles</summary>

- The streamwise field is right: $$R = 0.96$$, FAC2 0.70.
- $$k$$ is under-predicted (FB +0.46, $$R = 0.40$$); Cases A and H show the same under-prediction.
- $$V$$ and $$W$$ change sign, so factor-of-two agreement is a harsh measure near zero and FAC2 is low; R and hit rate carry the comparison there.
- The flat row of model $$V$$ ≈ 0 in the $$V$$ panel is the symmetry plane: a RANS solution is symmetric, so $$V$$ ≡ 0 at $$y = 0$$.
- The model follows the measured profile closely above roof height and in the recovering wake; the near-ground deficit immediately behind the building is where the closure does least well.

</details>
