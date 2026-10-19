- A second mesh or iteration count.
- The other eleven of the tunnel's twelve directions, and the field's other fifteen. Which vertical datum the tunnel meant is not settled (both frames are published).
- The published STL is open along the rim of its disc (812 boundary edges) and the mesh fails one checkMesh check (43 highly skew faces, maximum skewness 14.8), so the solve ran on Eddy3D's hardened numerics. The rooftop anemometers' modelled speeds are in the results file and are not scored.
- OpenLB, FluidX3D, UMF and the ML surrogate.

<details markdown="block">
<summary>Interpretation: Limits of this run</summary>

- With one mesh and the residual control unmet, none of these numbers is mesh- or iteration-independent.
- The open STL rim and the failed checkMesh check were not varied, so their effect on the scores is unknown.

</details>
