## Measurement layout

{% include figure.html name="case-a-layout.png" alt="Measurement lines and planes, Case A" caption="<strong>Figure 1.</strong> Case A, measurement lines and planes: A vertical profiles, $$y/b = 0$$; B plane $$z/b = 0.125$$; C plane $$z/b = 1.25$$. Positions in multiples of $$b$$." %}

## OpenFOAM 12: measured against modelled

{% include figure.html name="case-a-openfoam-agreement.png" alt="Measured vs modelled, Case A" caption="<strong>Figure 2.</strong> Case A, measured vs modelled $$U$$, $$V$$, $$W$$ and $$k$$, with the 1:1 line and, where the quantity does not change sign, the factor-of-two band. The dots take the colour of the line or plane they were measured on, as in Figure 1." %}

- Normalised by $$U_H$$. FB is positive when the model is low.
- Reattachment length behind the building: $$L_r/H$$ = 1.49.
- $$V$$ and $$W$$ change sign. The mean measured $$W$$ is ~0.01 m/s.

{% include figure.html name="case-a-openfoam-profiles.png" alt="Centre-plane profiles, Case A" caption="<strong>Figure 3.</strong> Case A, vertical profiles of $$U/U_H$$ on the centre plane at the first three measured stations behind the building, offset per station." %}

<details markdown="block">
<summary>Interpretation: Case A scores and profiles</summary>

- The streamwise field is right: $$R = 0.96$$, FAC2 0.82.
- $$k$$ is under-predicted (FB +0.48, $$R = 0.48$$); Cases B and H show the same under-prediction.
- $$V$$ and $$W$$ change sign, so factor-of-two agreement is a harsh measure near zero and FAC2 is low; R and hit rate carry the comparison there.
- $$W$$'s FB of −1.50 and its NMSE follow from a near-zero mean; the correlation is $$R = +0.71$$.
- The model follows the measured profile closely above roof height and in the recovering wake; the near-ground deficit immediately behind the building is where the closure does least well.

</details>

The OpenLB and FluidX3D runs below are drawn beside OpenFOAM 12 on the [OpenLB and FluidX3D]({{ '/validation/engines/' | relative_url }}) page, the ML surrogate on the [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}) page.
