"""Tests of validation/layout.py's measurement groups. Standard library only: python -m unittest test_layout (from validation/).

The expected sizes below are not read back from layout.py. They are the structure the tunnel and the data paper state, worked out
from them here: Case A's three sets of points from the MP drawings (a plane holds 5 + 5 + 5 + 9 x 5 = 60 positions of which the 5 at
y = 0 lie on the vertical section), Case L's 27 x 8 + 14 x 4 + 24 x 3 from section 3.12.1, Case G's 7 lines x 4 heights from 3.7.1.
"""
import csv
import io
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L  # noqa: E402

# group sizes by letter, in rows of clean/cases/<X>/points.csv; the instrument rows of H count twice (analyser and sonic probe)
EXPECTED = {
    "A": [186 - 2 * 55, 55, 55],                     # 186 points; planes z/b = 0.125 and 1.25: 60 positions each, 5 of them on y = 0
    "B": [224 - 108, 108],                           # 224 points; plane z/H = 1/16
    "G": [4] * 7,                                    # seven lines (0.25H .. 5H), four sonic heights each
    "H": [2 * 220, 2 * 312, 2 * 147, 2 * 147],       # 826 points per instrument: section y/H = 0, planes z/H = 0.0625 (y +-0.2), 0.25 and 0.5 (y >= 0)
    "I": [266, 273, 53, 38],                         # analyser 539 = 266 + 273; laser Doppler 91 = 53 + 38
    "J": [444 - 97 - 194, 97, 194],                  # section y/H = 0; planes z/H = 0.025 (y <= 0 side) and 0.25 (both sides)
    "K": [55, 100, 18, 30],                          # 203 = y/H 0, +-1, +-2, +-3
    "L": [27 * 8, 14 * 4, 24 * 3],                   # data paper 3.12.1: 344 = 216 + 56 + 72
    # The district cases: places x rows per place. C: 120 places in 9 configurations (3 centre blocks x 3 wind directions): 4 streets of 5 x 3
    # places beside the centre block and 4 crossings of 3 x 4 + 3 places (MP-z-caseC.png). D: 78 thermistor places x 3 directions, split fibre
    # at 33 of them (WD 0): 20 places on the site of the central block, 50 in the two streets along y (5 columns x 10 rows), 8 further out.
    # E: 80 places x 2 states x 16 directions = 32 rows each: 23 within 30 m of the 60 m building, 19 of the two 18 m buildings, 38 others.
    # F: 13 places; the 5, 9 and 20 m planes have 9, 13 and 13 of them (12 directions on the 9 m plane, 29 + 156 + 79 rows) and 16 x 13 field rows.
    # M: 15 places x 22 rows (3 tunnel headings, the split fibre, 18 field runs): 4 within 100 m of the release point, 9 to 300 m, 2 beyond.
    "C": [15 * 9, 15 * 9, 15 * 9, 15 * 9, 60 * 9],
    "D": [33, 20 * 3, 50 * 3, 8 * 3],
    "E": [23 * 32, 19 * 32, 38 * 32],
    "F": [29, 156, 79, 208],
    "M": [4 * 22, 9 * 22, 2 * 22],
}
TOTAL = {"A": 186, "B": 224, "G": 28, "H": 1652, "I": 630, "J": 444, "K": 203, "L": 344, "C": 1080, "D": 267, "E": 2560, "F": 472, "M": 330}   # clean/README.md


class Groups(unittest.TestCase):
    def test_every_case_has_groups(self):
        self.assertEqual(sorted(L.SPECS), sorted(EXPECTED))
        self.assertEqual(sorted(L.SPECS), list("ABCDEFGHIJKLM"))

    def test_each_point_in_exactly_one_group(self):
        for case in L.SPECS:
            tab = L.rows(case)
            gs = L.groups(case)
            self.assertEqual(len(tab), TOTAL[case], case)
            seen = {}
            for g in gs:
                for i in g.members:
                    self.assertNotIn(i, seen, f"case {case}: row {i} is in groups {seen.get(i)} and {g.letter}")
                    seen[i] = g.letter
            self.assertEqual(len(seen), len(tab), f"case {case}: rows without a group")

    def test_group_sizes(self):
        for case, sizes in EXPECTED.items():
            self.assertEqual([g.n for g in L.groups(case)], sizes, case)
            self.assertEqual(sum(sizes), TOTAL[case], case)

    def test_classify_agrees_with_groups(self):
        for case in L.SPECS:
            tab = L.rows(case)
            for g in L.groups(case):
                for i in g.members[::7]:
                    self.assertEqual(L.classify(case, tab[i]), "ABCDEFG".index(g.letter), (case, i))

    def test_letters_and_colours(self):
        for case in L.SPECS:
            gs = L.groups(case)
            self.assertLessEqual(len(gs), L.MAX_GROUPS)
            self.assertEqual([g.letter for g in gs], list("ABCDEFG"[:len(gs)]))
            self.assertEqual(len({g.colour for g in gs}), len(gs), case)
            self.assertEqual(len({g.label for g in gs}), len(gs), case)

    def test_kinds_hold(self):
        """A plane has one height; vertical profiles have the same x, y at several heights; points of a district case may have any."""
        for case in L.SPECS:
            for g in L.groups(case):
                if g.kind == "plane":
                    self.assertEqual(len(g.zs), 1, (case, g.letter))
                elif g.kind == "profiles":
                    self.assertGreater(len(g.zs), 1, (case, g.letter))
                else:
                    self.assertEqual(g.kind, "points")

    def test_agreement_scripts_colour_by_coordinates(self):
        """grouped_colours reads only x, y, z (and the instrument): the pairs files of the agreement figures carry exactly that."""
        self.assertEqual(L.grouped_colours("G", [{"x": 3.5, "z": 1.5}, {"x": 35.0, "z": 6.0}]), [L.GROUP_COLOURS[1], L.GROUP_COLOURS[6]])
        self.assertEqual(L.grouped_colours("I", [{"x": 0.1, "y": 0.0, "z": 0.2}], instrument="ldv"), [L.GROUP_COLOURS[2]])
        with self.assertRaises(ValueError):
            L.classify("A", {"x": 0.0, "y": -0.5, "z": 0.05})      # on no line and in no plane of Case A


class Structure(unittest.TestCase):
    """Facts about the groups that come from the geometry, not from the rules."""

    def test_case_a_sections_and_planes(self):
        gs = L.groups("A")
        self.assertEqual(gs[0].ys, [0.0])
        self.assertEqual(gs[1].zs, [0.01])
        self.assertEqual(gs[2].zs, [0.1])
        self.assertEqual(gs[0].xs, [-0.06, -0.04, -0.02, 0.0, 0.04, 0.06, 0.1, 0.16, 0.26])      # the nine stations of MP-y_caseA.png
        self.assertAlmostEqual(gs[1].zs[0] / L.UNITS["A"][1], 0.125)                                # z/b of the first plane
        self.assertAlmostEqual(gs[2].zs[0] / L.UNITS["A"][1], 1.25)

    def test_case_g_lines_are_multiples_of_the_tree_height(self):
        H = L.UNITS["G"][1]
        self.assertEqual([g.xs[0] / H for g in L.groups("G")], [0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0])
        for g in L.groups("G"):
            self.assertEqual(g.zs, [1.5, 3.0, 4.5, 6.0])                                             # four sonic anemometer heights

    def test_case_h_planes(self):
        H = L.UNITS["H"][1]
        self.assertEqual([round(g.zs[0] / H, 4) for g in L.groups("H")[1:]], [0.0625, 0.25, 0.5])

    def test_case_k_lines(self):
        H = L.UNITS["K"][1]
        self.assertEqual([sorted({round(abs(y) / H) for y in g.ys}) for g in L.groups("K")], [[0], [1], [2], [3]])

    def test_case_l_classes(self):
        """The 14 profiles above roofs stand inside the footprint of a cube; none of the others does (cubes: geometry.json)."""
        boxes = L.geometry("L").boxes
        inside = lambda x, y: any(lo[0] <= x <= hi[0] and lo[1] <= y <= hi[1] for lo, hi in boxes)  # noqa: E731
        tab = L.rows("L")
        locs = {}
        for g in L.groups("L"):
            for i in g.members:
                locs.setdefault(g.letter, set()).add((tab[i]["x"], tab[i]["y"]))
        self.assertEqual([len(locs[k]) for k in "ABC"], [27, 14, 24])
        self.assertTrue(all(inside(*p) for p in locs["B"]))
        self.assertFalse(any(inside(*p) for p in locs["A"] | locs["C"]))
        heights = {g.letter: g.zs for g in L.groups("L")}
        self.assertEqual(len(heights["A"]), 8)
        self.assertEqual(heights["B"], [0.07, 0.09, 0.11, 0.15])
        self.assertEqual(heights["C"], [0.004, 0.01, 0.03])

    def test_case_i_instruments(self):
        tab = L.rows("I")
        for g in L.groups("I"):
            self.assertEqual(len({tab[i]["instrument"] for i in g.members}), 1)
        self.assertEqual([tab[g.members[0]]["instrument"] for g in L.groups("I")], ["hydrocarbon_analyser"] * 2 + ["ldv"] * 2)

    def test_geometry_and_flow_exist(self):
        for case in L.SPECS:
            if case not in ("E", "F", "M"):          # the district meshes publish no boxes
                self.assertTrue(L.geometry(case).boxes, case)
            self.assertTrue(L.approach_flow(case), case)


def places(case, **where):
    """The distinct (x, y) of the rows of `case` that match every key of `where` (config, instrument, wind_direction_deg as a float)."""
    out = set()
    for r in L.rows(case):
        if all(r[k] == v for k, v in where.items()):
            out.add((round(r["x"], 6), round(r["y"], 6)))
    return out


class District(unittest.TestCase):
    """Facts about the district cases (C, D, E, F, M) that come from the tunnel's drawings and files, not from the rules."""

    def test_group_sizes_in_places(self):
        by_places = {"C": [15, 15, 15, 15, 60], "D": [33, 20, 50, 8], "E": [23, 19, 38], "F": [9, 13, 13, 13], "M": [4, 9, 2]}
        for case, want in by_places.items():
            tab = L.rows(case)
            got = [len({(round(tab[i]["x"], 6), round(tab[i]["y"], 6)) for i in g.members}) for g in L.groups(case)]
            self.assertEqual(got, want, case)

    def test_case_c_every_configuration_has_the_120_places(self):
        grid = places("C", config="0D", wind_direction_deg=0.0)
        self.assertEqual(len(grid), 120)
        for config in ("0D", "1D", "2D"):
            for wd in (0.0, 22.5, 45.0):
                self.assertEqual(places("C", config=config, wind_direction_deg=wd), grid, (config, wd))
        h = L.UNITS["C"][1] / 2          # the centre block spans +-D/2; no point stands on it
        self.assertFalse(any(abs(x) < h - 1e-9 and abs(y) < h - 1e-9 for x, y in grid))
        self.assertEqual({round(z, 6) for z in (r["z"] for r in L.rows("C"))}, {0.02})       # z = 0.1 D

    def test_case_d_split_fibre_stands_where_a_thermistor_does(self):
        thermistor, split = places("D", instrument="thermistor"), places("D", instrument="split_fibre")
        self.assertEqual((len(thermistor), len(split)), (78, 33))
        self.assertTrue(split <= thermistor)
        self.assertTrue(all(y > 0 for _, y in split))                                    # the +y side of the tower, WD 0 only
        self.assertEqual({r["wind_direction_deg"] for r in L.rows("D") if r["instrument"] == "split_fibre"}, {0.0})
        # the two streets along y: the gaps between the block columns x/H in [-0.8, -0.4], [-0.2, 0.2], [0.5, 0.9] (geometry.json)
        boxes = L.geometry("D").boxes
        columns = sorted({(lo[0], hi[0]) for lo, hi in boxes if abs((lo[0] + hi[0]) / 2) < 0.3 and (hi[2] - lo[2]) < 0.1})
        self.assertEqual(columns[:3], [(-0.2, -0.1), (-0.05, 0.05), (0.125, 0.225)])
        beside = {p for p in thermistor if -0.1 < p[0] < -0.05 or 0.05 < p[0] < 0.125}
        self.assertEqual(len(beside), 50)

    def test_case_d_twelve_places_read_nothing(self):
        """MP_caseD.png marks 12 thermistor places around the tower as unmeasured: points 26-29, 32, 33, 36, 37, 40-43 (clean/build.log)."""
        tab = L.rows("D")
        read = {(round(r["x"], 6), round(r["y"], 6)) for r in tab if r["instrument"] == "thermistor" and r["measured"]}
        every = {(round(r["x"], 6), round(r["y"], 6)): int(r["point_id"]) for r in tab if r["instrument"] == "thermistor"}
        self.assertEqual(sorted(n for p, n in every.items() if p not in read), [26, 27, 28, 29, 32, 33, 36, 37, 40, 41, 42, 43])
        self.assertEqual(len(read), 66)

    def test_case_e_both_states_at_the_same_80_places(self):
        self.assertEqual(places("E", config="bc"), places("E", config="ac"))
        self.assertEqual(len(places("E", config="ac")), 80)
        self.assertEqual(len({r["wind_direction_deg"] for r in L.rows("E")}), 16)

    def test_case_e_new_buildings(self):
        new = L.e_new_buildings()
        self.assertEqual([b[4] for b in new], [60.0, 18.0, 18.0])                         # data paper 3.5.1: one of 60 m, two of 18 m
        self.assertEqual(sum(1 for b in new if (b[1] - b[0]) * (b[3] - b[2]) > 400), 3)

    def test_case_e_groups_hold_for_the_tunnels_own_footprints(self):
        """The official STL (the tunnel's model, scaled x250) places the buildings within 3.5 m of the 3dm reconstruction the rule reads
        (the 18 m buildings stand 3 m further west in it): the points within 26 m of its roofs are all in the near groups, and the points
        beyond 34 m are all in 'elsewhere'; the 30 m limit of the rule is a choice between them."""
        tris = L.read_stl(os.path.join(L.CASES_DIR, "E", "geometry_ac.stl"))

        def box(b):
            """The roof triangles at the height of building b whose centres lie within 2.5 m of its footprint: its footprint in the official STL."""
            xs, ys = [], []
            for t in tris:
                cx, cy = sum(v[0] for v in t) / 3, sum(v[1] for v in t) / 3
                if all(abs(v[2] - b[4]) < 0.05 for v in t) and b[0] - 2.5 < cx < b[1] + 2.5 and b[2] - 2.5 < cy < b[3] + 2.5:
                    xs += [v[0] for v in t]
                    ys += [v[1] for v in t]
            return (min(xs), max(xs), min(ys), max(ys))
        mine = L.e_new_buildings()
        theirs = [box(b) for b in mine]
        for a, b in zip(mine, theirs):
            self.assertLess(max(abs(a[i] - b[i]) for i in range(4)), 3.5)
        tab = L.rows("E")
        for r in tab:
            if r["config"] != "ac" or r["wind_direction_deg"] != 0.0:
                continue
            d = min(L._e_dist(r, b) for b in theirs)
            if d <= L.E_NEAR - 4.0:
                self.assertNotEqual(L.classify("E", r), 2, r["point_id"])
            if d > L.E_NEAR + 4.0:
                self.assertEqual(L.classify("E", r), 2, r["point_id"])

    def test_case_f_planes_and_field(self):
        heights = {}
        for r in L.rows("F"):
            heights.setdefault((r["config"], r["instrument"]), set()).add(round(r["z"] - L.F_RAISE, 6))
        self.assertEqual(heights[("h5", "thermistor")], {5.0})
        self.assertEqual(heights[("default", "thermistor")], {9.0})
        self.assertEqual(heights[("h20", "thermistor")], {20.0})
        self.assertEqual(heights[("default", "cup_anemometer")], {3.0, 7.0, 8.0, 9.0, 11.0})       # clean/QUESTIONS.md QF7
        self.assertEqual(places("F", config="default", instrument="thermistor"), places("F", config="default", instrument="cup_anemometer"))
        self.assertTrue(places("F", config="h5") <= places("F", config="default", instrument="thermistor"))

    def test_case_f_reference_buildings(self):
        """SMB and KDD: the workbook's positions (the names of MP_caseF.csv are exchanged, QUESTIONS.md QF6) and the roofs in the STL."""
        with io.open(os.path.join(L.REPO, "raw", "cases", "case-f", "MP_caseF.csv"), encoding="utf-8") as f:
            mp = {r["No"]: (float(r["x"]) * 800, float(r["y"]) * 800) for r in csv.DictReader(f)}
        for name, other in (("SMB", "KDD"), ("KDD", "SMB")):
            self.assertAlmostEqual(L.TOWERS[name][0], mp[other][0], delta=0.1)
            self.assertAlmostEqual(L.TOWERS[name][1], mp[other][1], delta=0.1)
        tris = L.read_stl(os.path.join(L.CASES_DIR, "F", "geometry.stl"))
        for name, (x, y, z) in L.TOWERS.items():
            roof = max(v[2] for t in tris for v in t if abs(v[0] - x) < 15 and abs(v[1] - y) < 15)
            self.assertAlmostEqual(roof, z, delta=0.5, msg=name)
        self.assertAlmostEqual(max(math.hypot(v[0], v[1]) for t in tris[::50] for v in t), L.DISC_F, delta=1.0)

    def test_case_m_release_point_and_reference_point_from_the_tunnels_file(self):
        with io.open(os.path.join(L.REPO, "raw", "cases", "case-m", "LC_caseM.csv"), encoding="utf-8") as f:
            lc = {r["No."]: (float(r["x (m)"]) * 600, float(r["y (m)"]) * 600, float(r["Elevation"]) * 600) for r in csv.DictReader(f)}
        for want, got in ((lc["Gas_source"], L.SOURCES["M"][0][1]), (lc["Reference"], L.MAST)):
            self.assertEqual([round(v, 2) for v in want], [round(v, 2) for v in got])
        sx, sy, _ = lc["Gas_source"]
        dist = {int(k): math.hypot(v[0] - sx, v[1] - sy) for k, v in lc.items() if k.isdigit()}
        self.assertEqual((sum(d < L.M_NEAR for d in dist.values()), sum(d > L.M_FAR for d in dist.values())), (4, 2))
        self.assertGreater(min(abs(d - t) for d in dist.values() for t in (L.M_NEAR, L.M_FAR)), 3.0)        # no point within 3 m of a limit
        for r in L.rows("M"):          # the table's places are the tunnel's, in full-scale metres, 3 m above the ground
            self.assertAlmostEqual(r["x"], lc[str(int(r["point_id"]))][0], delta=0.05)       # LC_caseM.csv has four decimals of a model metre
            self.assertAlmostEqual(r["y"], lc[str(int(r["point_id"]))][1], delta=0.05)

    def test_wind_directions_come_from_the_table(self):
        self.assertEqual(sorted(L.flow_dirs("C")), [0.0, 22.5, 45.0])
        self.assertEqual(sorted(L.flow_dirs("D", "thermistor")), [0.0, 22.5, 45.0])
        self.assertAlmostEqual(L.flow_dirs("C")[45.0][1], -math.sqrt(0.5), places=6)           # C turns toward -y, D toward +y: the sense differs
        self.assertAlmostEqual(L.flow_dirs("D", "thermistor")[45.0][1], math.sqrt(0.5), places=6)


class Labels(unittest.TestCase):
    def test_mult(self):
        for v, want in ((0, "0"), (1, "H"), (-1, "-H"), (2, "2H"), (0.25, "H/4"), (0.75, "3H/4"), (-0.5, "-H/2"), (-0.375, "-3H/8"), (1.25, "5H/4"),
                        (0.65, "0.65H"), (-5 / 6, "-5H/6"), (1.9, "1.9H"), (0.04, "H/25")):
            self.assertEqual(L.mult(v, "H"), want, v)

    def test_labels_name_the_unit(self):
        self.assertEqual([g.label for g in L.groups("A")], ["vertical profiles, y/b = 0", "plane z/b = 0.125", "plane z/b = 1.25"])
        self.assertEqual([g.short for g in L.groups("K")], ["section y/H = 0", "section y/H = ±1", "section y/H = ±2", "section y/H = ±3"])


if __name__ == "__main__":
    unittest.main()
