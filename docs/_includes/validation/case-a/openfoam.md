### Measured against modelled

{% include figure.html name="case-a-openfoam-agreement.png" alt="Measured vs modelled, Case A" caption="<strong>Figure 2.</strong> Case A, measured vs modelled $$U$$, $$V$$, $$W$$ and $$k$$, with the 1:1 line and, where the quantity does not change sign, the factor-of-two band. The dots take the colour of the line or plane they were measured on, as in Figure 1." %}

- Normalised by $$U_H$$. FB is positive when the model is low.
- Reattachment length behind the building: $$L_r/H$$ = 1.49.
- $$V$$ and $$W$$ change sign. The mean measured $$W$$ is ~0.01 m/s.
- The scores table shows the served steady run (RANS) beside the same solver run transient (URANS: SST k-omega, PIMPLE, 1000 s of flow time on the measured inlet, scored on the time means with $$k$$ as the modelled mean plus the resolved part). The URANS run reattaches at $$L_r/H$$ = 1.29 and resolves 27 % of the wake's $$k$$ (3 % upstream); its inlet is the tunnel's measured profile, the RANS run's the fitted log law.

{% include figure.html name="case-a-openfoam-profiles.png" alt="Centre-plane profiles, Case A" caption="<strong>Figure 3.</strong> Case A, vertical profiles of $$U/U_H$$ on the centre plane at the first three measured stations behind the building, offset per station." %}

<details markdown="block">
<summary>Interpretation: Case A scores and profiles</summary>

- The streamwise field is right: $$R = 0.96$$, FAC2 0.82.
- $$k$$ is under-predicted (FB +0.48, $$R = 0.48$$); Cases B and H show the same under-prediction.
- $$V$$ and $$W$$ change sign, so factor-of-two agreement is a harsh measure near zero and FAC2 is low; R and hit rate carry the comparison there.
- $$W$$'s FB of −1.50 and its NMSE follow from a near-zero mean; the correlation is $$R = +0.71$$.
- The model follows the measured profile closely above roof height and in the recovering wake; the near-ground deficit immediately behind the building is where the closure does least well.

</details>
