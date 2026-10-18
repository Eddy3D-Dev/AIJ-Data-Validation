# Open questions for the data collectors (Ilker / Patrick to forward)

Things the published files, readmes and the data paper (Kikumoto et al. 2026, JAR 9(1) e70083)
cannot settle, each with what was measured and what one line from the collector would close.
Contacts are in `manifest.json → cases.<id>.contact`. Numbers below are in `checks.json`.

## Q1 — Case C: which way does the turntable turn? (Nonomura)

In `RS_caseC.csv`'s own frame (+x = the WD = 0 flow, confirmed three ways on the data) the WD = 45°
field is mirror-symmetric about the line **y = −x**: mean |ΔVs| over the 57 mirror pairs is
0.108 / 0.103 / 0.130 m/s for 0D / 1D / 2D — the experiment's own repeatability floor — while the
mirror about y = +x gives 0.52 / 0.77 / 0.80 m/s. So in the CSV the wind rotates from +x **toward
−y** as WD grows. Figure 3 of the data paper draws the 0 / 22.5 / 45° arrows fanning toward **+y**.
The two differ by a sign of y, which is invisible at WD = 0.

This release keeps the CSV frame (`directions.csv`: flow_dir = (cos WD, −sin WD)) because the point
coordinates live in it. **Question:** is the y axis of `RS_caseC.csv` the one in Figure 3, or its
mirror? Equivalently: for WD = 45°, does the wind come from the (−x, +y) quadrant or the (−x, −y)
quadrant of the CSV coordinates?

*Update 2026-10-14 — a second, independent line of evidence.* Eddy3D solved all nine configurations
(OpenFOAM 12, realizable k-ε) and scored the 120 points both ways on the same solutions: in the CSV's
sense R = 0.83–0.91 at 22.5° and 45°; in Figure 3's sense (the y mirror) R = −0.33 … +0.03. A RANS
solution knows nothing about the CSV's convention, so the data's own symmetry and the physics now agree;
the question stays open only for the collector's word on Figure 3.

## Q2 — Case D: rotation sense for 22.5° and 45° (Tominaga)

The 83-block array is exactly symmetric under y → −y, so a wind at +θ and one at −θ give exact mirror
fields and **no measurement can distinguish them**; the 0° thermistor column is itself an exact
y-mirror (33 pairs with ΔVs = 0, i.e. half of it was measured and mirrored). The sense used here
(flow_dir = (cos WD, +sin WD), status `unverified`) is a reading of Figure 4 of the data paper, and
it is the OPPOSITE of what Case C's data show for Case C. The Zenodo readme (now in
`clean/sources/zenodo_caseD/`) does not state it either.

**Question:** at WD = 22.5° and 45°, is the wind turned from +x toward +y or toward −y, in the
coordinates of `RS-T_caseD.csv` / `MP_caseD.png`? (Also: which half of the 0° plane was actually
measured, +y or −y?)

*Update 2026-10-15 — the solved field decides 22.5°.* No measurement alone can, but a solution can: Eddy3D
solved the array at 22.5° (OpenFOAM 12, realizable k-ε, 3.6 million cells) and scored the 66 measured
points in this release's sense and in its y mirror on the same solution. In Figure 4's sense (+x toward
+y) R = 0.80, FAC2 0.92; mirrored R = 0.40, FAC2 0.74. A RANS solution knows nothing about the figure, so
22.5° is corroborated in Figure 4's sense (`directions.csv` says so); 45° stays unverified until it is
solved. The question stays open for the collector's word, and for 45°.

*Update 2026-10-16 — and 45°.* Solved the same way (3000 iterations, the same residual plateau as 0° and
22.5°): in Figure 4's sense R = 0.85, FAC2 0.89; mirrored R = 0.17, FAC2 0.70 — a wider margin than at 22.5°.
Both rotated headings are now corroborated in Figure 4's sense. The question stays open only for the
collector's own word, and for which half of the 0° plane was measured.

## Q3 — Case E: the sensor frame against the two geometries (Tominaga)

1. Point 50 at (−45.5, −45.0) m lies **0.17 m inside a building wall of the official `BD_caseE.stl`**
   (roof at 6.75 m) and 2.06 m clear of the nearest wall in `case-e.3dm`. The other 79 points
   are in open space in both files (median 4.9 m from the nearest vertex). The two files are
   different triangulations of the district (official: 227 shells, 60,101 triangles, 5,253 open
   edges, bbox ±198 m after ×250; the 3dm: 5,015 meshes, bbox −201.5…203 m). Which is the
   measured model, and is point 50 really in the street?
2. The official STL is **model scale** (z max 0.24 m = 60 m / 250) while the readme calls the
   coordinates "actual scale"; the ×250 is this release's inference from the 60 m high-rise. Please
   confirm, and whether a watertight STL exists.
3. The dataset publishes **only the after-construction geometry**. The before-construction state
   used here (`geometry_bc_3dm.stl`) is the 3dm's `buildings` layer with the three sites empty. Is
   that what stood in the tunnel for the "bc" runs, or were there earlier buildings on the sites?
4. `RS_caseE.csv` on Zenodo is the workbook rounded to 2 dp (max |Δ| 0.00497); the workbook's values
   are exact multiples of 0.0198204 (= U/UR at 0.01 resolution re-normalised by UR / U(15.9 m), which
   gives U(15.9 m) = 3.935 m/s; the paper says 4.0). Which U_ref was used, and is the workbook the
   authoritative precision?

## Q4 — Case B: lateral sign and the seven repeated points (Tominaga)

1. The published V appears positive toward −y: V = +3.630 m/s at (−25, −110, 12.5) mm, just outside
   the y = −100 mm flank where the flow must deflect away from the centreline. Case A (V = −2.893 at
   the equivalent point) and Case D (V = +2.055 on the +y flank) both read positive toward +y. This
   release flips B's V. Please confirm the sign convention of V in `RS_caseB.csv` (or whether the
   published points are on the +y half rather than the −y half of the drawing).
2. Seven locations appear twice with different values: the foot of each vertical-section profile
   (z = 12.5 mm, y = 0; points 12, 43, 56, 69, 82, 95, 108) and the horizontal-plane centreline
   (points 110, 147, 160, 173, 186, 199, 212). |ΔU| = 0.05–0.14 m/s (mean 0.105). Two runs? Which
   is canonical, or should both be kept (as here) as a repeatability estimate?

## Q5 — Case C: what reference speed did the legacy workbook use? (Nonomura)

`LF-caseC.xls` publishes velocity ratios "normalized by the inflow velocity at the same height".
Multiplying by U(0.02 m) = 2.434 m/s from `AF_caseC.csv` reproduces the CSV's Vs only to 0.3 %:
Vs / ratio spans 2.4145–2.4525 m/s across the 1,080 values, so the ratios seem to use a per-run
reference. Is that so, and are the CSV's 2-dp Vs values the raw measurements?

## Q6 — Case D: the split-fibre "Scalar Vel." column (Tominaga)

`RS-S_caseD.csv`'s `Vs` and the workbook's `Scalar Vel.` equal √(U²+V²+W²) to 1e-15 at all 33
points, so they are the vector magnitude, not a thermistor reading, and are dropped here. Is that
right? (The thermistor readings at the same 33 points are in `RS-T_caseD.csv`; their ratio to the
magnitude averages 1.34.)

## Q7 — Cases A, B, C: model scale (Ishihara / Tominaga / Nonomura)

No model:full-scale ratio is stated for A, B or C (D says 1:400, E 1:250). Eddy3D solves them at
1:100 with the tunnel velocities, which only matters for how results are labelled. Is a nominal
scale on record?

## Q8 — Case C: data paper Table 2 vs the CSV point numbering (Nonomura)

The readme lists 1, 2, 3, 34, 35, 36, 37, 46, 55, 100, 101, 102 as missing point numbers and the CSV
agrees (4…132 with those gaps). Were points 1–3 and the nine interior gaps never measured, or
measured and withheld (e.g. inside buildings for one configuration)?

## Questions on Cases F and M

Numbered with the case letter (QF1 …, QM1 …) so that the questions of each case stay together; the numbers
are in `checks.json` and `manifest.json → cases.F / M`. Contacts: Case F, Tsubasa Okaze; Case M, Ryuichiro Yoshie.

## QF1 — Case F: is the field series of point 14 shifted by one direction? (Okaze)

In `RS-FO_caseF.csv` the 16 rows of point 14 hold the value that `LF_CaseF.xls` ('Results (No.1-No.15)', block
No.14) gives for the **next** direction clockwise: (14, N) = workbook NNE, (14, NNE) = workbook NE, … (14, NNW) =
workbook N, each times the sector's factor and rounded. The other 12 points match the workbook on all 16 directions
with no shift (192 of 192 rows reproduced). The R between the 12 tunnel directions and the field at point 14 is 0.55
as published (every other point: 0.63 … 0.93) and 0.72 with the workbook's alignment. This release follows the workbook; the published values are in
`manifest.json → cases.F.known_issues`. **Question:** which alignment is the field observation's? One line closes it.

## QF2 — Case F: tunnel value of point 8, SW, 9 m (Okaze)

`RS-WT_caseF.csv` has U/R = 0.474 at (8, SW, z = 0.02375 m). The workbook's 'Results' sheet is blank for it (as for
the 'Other' column), and its flat 'Sheet1' table gives 0.63 (× 0.9629 = 0.607). The 155 other 9 m rows all reproduce
from the workbook within 0.014. Is the value 0.474, 0.607, or was the point not measured at SW?

## QF3 — Case F: what is the 'Other' column of the workbook? (Okaze)

The workbook's wind-tunnel block has 'Other' and 'Target' columns. 'Target' is the 9 m plane (155 of the CSV's 156 rows
reproduce within 0.014 with the sector factors). 'Other' has 109 values, 9 of them at **ESE**, where the readme says the tunnel
did not run (E, ESE, WSW, W), and it reproduces neither the 5 m nor the 20 m rows of the CSV (2 of 79 comparable pairs).
What are they: another model state, another height, or another run? Are the 5 m and 20 m values of the CSV from the original
reports only?

## QF4 — Case F: which ground do the heights refer to? (Okaze)

The readme says the points' z is above the tunnel floor and the ground is at z − 10 m, because the building data were raised
by 10 m; the planes are then 5, 9, 20 m above ground. In `BD_caseF.stl` the terrain under all 13 points is at
**z = 5 m**, so the planes stand 10, 14 and 25 m above it, and the two reference roofs (SMB, KDD) are 15 m above their
stated G.L. elevations (225 against 210 m, 180 against 165 m: 5 m terrain + 10 m). Where was the probe relative to the model's
street surface, and is the STL the model that was in the tunnel?

## QF5 — Case F: size and orientation of the STL (Okaze)

The STL is a disc of radius 725.0 m (0.90625 m model), open along its rim (812 boundary edges, all at z = 0); the readme says
"radius = 800 m equivalent" and the data paper "a diameter of 1,600 m". A 1.8125 m model would not fit the 1.55 m wide tunnel
the paper describes. All its ground and roof facets (and a sample of walls) face down, so the file is wound inward; this release
reverses it. Please confirm the radius that was in the tunnel, and that the file is meant to describe the 1978 configuration.

## QF6 — Case F: which reference point is SMB? (Okaze)

`MP_caseF.csv` gives SMB (0.10725, −0.433875) and KDD (−0.021875, 0.12) m (model); the workbook's 'Points' sheet gives the
Shinjuku-Mitsui Building at (−17.5, 96.0) and the KDD Building at (85.8, −347.1) m, which are the same points with the names
exchanged; `MP_caseF.png` labels (−0.02, 0.12) as D and (0.107, −0.434) as C, as the workbook does. The STL has a 225 m roof at
(−17.5, 96.0) and a 180 m roof at (85.8, −347.1): 45 m apart as SMB (210 m) and KDD (165 m) are. The release takes the workbook's
assignment; please confirm `MP_caseF.csv` is the one that is wrong.

## QF7 — Case F: field anemometer heights (Okaze)

By the readme's rule (z − 10 m) the field anemometers stand 3 m (point 15), 7 m (8), 8 m (11), 9 m (1, 2, 3, 5, 6, 7, 9, 10) and
**11 m** (13, 14) above ground. The data paper says "3 to 9 m". Are 13 and 14 at 11 m or at 9 m, and are the heights the true
heights above the local ground?

## QF8 — Case F: the reference speed and the conversion factors (Okaze)

The ratios are normalised by the approaching speed at 500 m. The data paper gives it as 10 m/s; `AF_caseF.csv` reaches 400 m
at 10.0 m/s, and combined with the workbook's U/UR profile (0.94 at 400 m) the 18 shared heights imply U(500 m) = 10.65 m/s
(10.59 … 10.73). The field values are the workbook's roof-anemometer ratios times 0.9397 (SMB sector, interval
[0.93947, 0.94000]) and 0.9629 (KDD, [0.96250, 0.96324]), which the readme describes without giving. What are U(500 m) in m/s and the two
factors, and what height does AF_caseF.csv's last row stand for?

## QF9 — Case F: direction sense (Okaze)

Are the wind directions the meteorological directions the wind blows **from**, clockwise from north, with +y north in
`MP_caseF.png`? This release assumes so (status `unverified`): the reference-building choice (SMB, the northern building, for
NW to NE) and the upwind roughness of the northern points (higher for S than for N) agree with it.

## QF10 — Case F: the field band of the workbook (Okaze)

In 10 rows of the workbook (2/NW, 6/E, 7/ESE, 7/NW, 9/E, 13/WNW, 14/ENE, 14/SSE, 15/N, 15/SSE) Mean + S.D. and Mean − S.D. are not
symmetric about the mean (differences from −0.11 to +0.10), and the last column equals Mean − (Mean − S.D.). The CSV's σ is that
lower half-width times the factor. Which is the standard deviation: the lower half-width, the upper, or the mean of the two?

## QM1 — Case M: where was the tracer released in the tunnel? (Yoshie)

The readme says ethylene was released "from a 6 mm outlet on a rooftop"; the workbook and `LC_caseM.csv` give the source at the
ground surface (z = 32.39 m full scale = the STL's terrain there, 32.39 m, no roof), and the field release was 1.5 m above ground.
Was the tunnel source at ground level, on a roof, or 1.5 m high (0.0025 m model)?

## QM2 — Case M: what is H_R = 41 m? (Yoshie)

`LC_caseM.csv` puts the reference point R at ground + 41 m (z = 72.90 m). The STL's main-building roof under R is at 64.92 m, 33.0 m
above the same ground, so R is 8.0 m above the roof; Table 1 of the data paper says Hmax = 41 m and the readme "reference building
height", while the tallest surface of the STL is 31.8 m above the origin's ground. Is 41 m the anemometer height (a mast on a 33 m roof)? The
workbook's c0 uses H_R = 0.068 m (41 m / 600 = 0.06833 m would give c0 = 131.2 ppm instead of 132.5, the paper's 1.33 × 10² ppm):
which H_R was meant for the tunnel?

## QM3 — Case M: backgrounds and baselines (Yoshie)

Every field run reads 9 to 11 ppq at point 12 (all 18 runs, whatever the wind) and 8 to 9 ppq at the minimum of points 11, 13, 14, 15; the
values are not zero and not subtracted. Is that the ambient PMCH background, the detection limit, or a blank? The tunnel's hydrocarbon
analyser has two negative means (point 12: −0.021 and −0.230 ppm) and rms of 7.3 to 17.4 ppm where the mean is below 1 ppm. Was a
baseline subtracted, and is the rms at those points noise or intermittency?

## QM4 — Case M: the rounding of the field's run conditions (Yoshie)

`RS-FO_caseM.csv` gives U_R to 0.01 m/s (the workbook's values are multiples of 1/30 m/s, i.e. means of three values), WD_R to 0.1° and q to
three significant digits. The cleaned table carries the workbook's. Are the workbook's the sonic anemometer's 10-minute values averaged
over three periods?

## QM5 — Case M: where was the approach flow measured? (Yoshie)

`AF_caseM.csv` is at x = −0.498 m, y = 0, with z "above the wind-tunnel floor". In `BD_caseM.stl` the model's upwind taper is 0.0521 m high at that
station, so the 10 lowest of the 40 heights (0.005 to 0.05 m) are below the model's ground there. Was the profile measured on the empty floor
(without the model), and is its U(z) the inlet for the ground at z = 0 or for the model's terrain? The profile at the height of R (0.1215 m)
gives 3.94 m/s against U_R = 4.08 m/s measured at R above the model.

## QM6 — Case M: direction convention (Yoshie)

The frame used here is +x north, +y west with WD the direction the wind comes from (the compass rose of `MP_caseM.png` and the plume's
lateral shift with WD in the tunnel and the field agree). Please confirm that WD_R of the field runs and WD of the tunnel are the same
meteorological direction, and that the sign of V in `RS-WT_caseM.csv` is positive toward +y (west).
