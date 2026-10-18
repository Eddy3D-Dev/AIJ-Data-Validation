"""Tests of validation/layout.py's measurement groups. Standard library only: python -m unittest test_layout (from validation/).

The expected sizes below are not read back from layout.py. They are the structure the tunnel and the data paper state, worked out
from them here: Case A's three sets of points from the MP drawings (a plane holds 5 + 5 + 5 + 9 x 5 = 60 positions of which the 5 at
y = 0 lie on the vertical section), Case L's 27 x 8 + 14 x 4 + 24 x 3 from section 3.12.1, Case G's 7 lines x 4 heights from 3.7.1.
"""
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
}
TOTAL = {"A": 186, "B": 224, "G": 28, "H": 1652, "I": 630, "J": 444, "K": 203, "L": 344}   # clean/README.md


class Groups(unittest.TestCase):
    def test_every_phase_one_case_has_groups(self):
        self.assertEqual(sorted(L.SPECS), sorted(EXPECTED))

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
        """A plane has one height; vertical profiles have the same x, y at several heights."""
        for case in L.SPECS:
            for g in L.groups(case):
                if g.kind == "plane":
                    self.assertEqual(len(g.zs), 1, (case, g.letter))
                else:
                    self.assertGreater(len(g.zs), 1, (case, g.letter))

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
            self.assertTrue(L.geometry(case).boxes, case)
            self.assertTrue(L.approach_flow(case), case)


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
