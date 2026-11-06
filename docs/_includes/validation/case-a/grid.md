OpenFOAM on four meshes (edge ratio $$\sqrt{2}$$, 151,210 to 1,411,566 cells), eddy-viscosity cap lifted as in [eddy3d-of12-nutcap-lifted]({{ '/community/eddy3d-of12-nutcap-lifted/' | relative_url }}). The served run keeps the cap.

{% include figure.html name="case-a-openfoam-grid.png" alt="Grid uncertainty, OpenFOAM, Case A" caption="<strong>Figure 9.</strong> Case A, second mesh of four: measured vs modelled, bar = grid uncertainty. Hollow: no band." %}

- Median band: $$U$$ 0.011 $$U_H$$ (p90 0.051); $$V$$, $$W$$, $$k$$ about 0.001. 140 of 186 points within the hit rate's 0.05 $$U_H$$; 30 without a band.
- Across the meshes: $$U$$ FAC2 0.79–0.82, hit rate 0.58–0.63; $$k$$ $$R$$ 0.28–0.44.
- $$L_r/H$$ 1.49, 1.44, 1.50, 1.51; extrapolated 1.51, measured 0.38–0.75. The long wake is the closure, not the mesh.
- Bands: [`grid/openfoam12-realizableKE.csv`]({{ '/api/cases/A/grid/openfoam12-realizableKE.csv' | relative_url }}). Method: [Grid uncertainty]({{ '/validation/method/' | relative_url }}#grid-uncertainty).
