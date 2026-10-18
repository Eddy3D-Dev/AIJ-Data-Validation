#!/usr/bin/env python3
"""Tests of clean/geometry_checks.py on synthetic inputs, and of scripts/check_geometry.py against the files it writes.

    python scripts/test_geometry.py
"""
import os
import random
import re
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, "clean"))
sys.path.insert(0, HERE)
import check_geometry as C  # noqa: E402
import geometry_checks as G  # noqa: E402


def box(lo, hi):
    """A box as 12 triangles, outward."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    p = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return [(p[a], p[b], p[c]) for a, b, c in faces]


def flip(tris, which):
    return [(a, c, b) if i in which else (a, b, c) for i, (a, b, c) in enumerate(tris)]


class Bodies(unittest.TestCase):
    def test_a_cube_is_watertight(self):
        s = G.stl_stats(box((0, 0, 0), (1, 1, 1)))
        self.assertTrue(s["watertight"])
        self.assertEqual((s["bodies"], s["edges_boundary"], s["inconsistent_triangles"], s["body_contacts"]), (1, 0, 0, 0))
        self.assertAlmostEqual(s["min_body_volume"], 1.0)

    def test_three_flipped_triangles_are_repaired(self):
        bad = flip(box((0, 0, 0), (1, 2, 3)), {1, 5, 8})
        before = G.stl_stats(bad)
        self.assertFalse(before["watertight"])
        self.assertEqual(before["inconsistent_triangles"], 3)
        fixed, info = G.orient_consistent(bad)
        after = G.stl_stats(fixed)
        self.assertTrue(after["watertight"])
        self.assertEqual(after["inconsistent_triangles"], 0)
        self.assertAlmostEqual(after["min_body_volume"], 6.0)
        self.assertEqual(info["bodies"], 1)

    def test_a_cube_wound_inward_is_reversed_whole(self):
        inward = flip(box((0, 0, 0), (1, 1, 1)), set(range(12)))
        fixed, info = G.orient_consistent(inward)
        self.assertEqual((info["bodies_reversed"], info["triangles_reversed"]), (1, 12))
        self.assertAlmostEqual(G.stl_stats(fixed)["min_body_volume"], 1.0)

    def test_an_open_sheet_is_detected_and_faces_up(self):
        sheet = [((0, 0, 0), (1, 1, 0), (1, 0, 0)), ((0, 0, 0), (0, 1, 0), (1, 1, 0))]   # wound downward
        s = G.stl_stats(sheet)
        self.assertFalse(s["watertight"])
        self.assertEqual(s["edges_boundary"], 4)
        fixed, _ = G.orient_consistent(sheet)
        self.assertEqual(G._up_down(fixed), (2, 0))

    def test_two_cubes_sharing_an_edge_are_two_closed_bodies_with_one_contact(self):
        s = G.stl_stats(box((0, 0, 0), (1, 1, 1)) + box((1, 1, 0), (2, 2, 1)))
        self.assertEqual((s["bodies"], s["body_contacts"], s["edges_boundary"]), (2, 1, 0))
        self.assertTrue(s["watertight"])
        self.assertEqual(s["edges_non_manifold"], 1)

    def test_a_missing_face_opens_a_body(self):
        s = G.stl_stats(box((0, 0, 0), (1, 1, 1))[:-2])
        self.assertFalse(s["watertight"])
        self.assertEqual(s["edges_boundary"], 4)


class Repairs(unittest.TestCase):
    def test_a_wall_two_buildings_share_is_dropped_and_they_become_one_body(self):
        a, b = box((0, 0, 0), (1, 1, 1)), box((1, 0, 0), (2, 1, 1))
        wall = lambda tris, x: [t for t in tris if all(p[0] == x for p in t)]
        a = [t for t in a if t not in wall(a, 1)] + [((1, 0, 0), (1, 0, 1), (1, 1, 1)), ((1, 0, 0), (1, 1, 1), (1, 1, 0))]   # a's wall, one diagonal
        b = [t for t in b if t not in wall(b, 1)] + [((1, 0, 0), (1, 1, 0), (1, 0, 1)), ((1, 1, 0), (1, 1, 1), (1, 0, 1))]   # b's wall, the other
        before = G.stl_stats(a + b)
        self.assertFalse(before["watertight"])
        fixed, info = G.clean_buildings(a + b)
        after = G.stl_stats(fixed)
        self.assertTrue(after["watertight"])
        self.assertEqual((after["bodies"], len(info["party_walls"]), after["triangles"]), (1, 1, 20))
        self.assertAlmostEqual(after["min_body_volume"], 2.0)

    def test_a_terrain_sheet_is_closed_with_a_base_slab(self):
        v = lambda x, y: (float(x), float(y), 0.0)
        sheet = []
        for y in range(2):
            for x in range(2):   # a 2 x 2 grid of unit squares, wound downward
                a, b, c, d = v(x, y), v(x + 1, y), v(x + 1, y + 1), v(x, y + 1)
                sheet += [(a, c, b), (a, d, c)]
        sheet.append(((0.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.4, 0.5, 0.01)))   # a flap: hung on a diagonal that two triangles use, two free edges
        closed, info = G.close_terrain(sheet, z=-1.0, digits=6)
        s = G.stl_stats(closed)
        self.assertEqual(info["flaps_removed"], 1)
        self.assertTrue(s["watertight"], s)
        self.assertEqual((s["bodies"], s["bbox_min"][2]), (1, -1.0))
        self.assertAlmostEqual(s["min_body_volume"], 4.0)   # 2 x 2 m, 1 m deep
        self.assertEqual(info["base_triangles"], 3 * 8)     # two skirt triangles and one cap triangle per rim edge

    def test_a_triangle_on_one_line_is_removed_and_its_neighbour_split(self):
        # a square split into two triangles, the lower edge carrying a middle vertex that a zero-area triangle fills
        a, m, b, c, d = (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 2.0, 0.0), (0.0, 2.0, 0.0)
        tris = [(a, b, c), (a, c, d), (a, m, b)]
        self.assertTrue(any(G._is_degenerate(*t) for t in tris))
        out, dropped = G.split_degenerate(tris)
        self.assertEqual(dropped, 1)
        self.assertFalse(any(G._is_degenerate(*t) for t in out))
        self.assertEqual(G.stl_stats(out)["edges_boundary"], 5)   # the square's rim: four sides, the bottom one now split at m


class Checker(unittest.TestCase):
    """check_geometry.py, which shares no code with the module, on files the module wrote."""

    def check(self, tris, tweak=None):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "geometry.stl")
            G.write_ascii_stl(path, tris, "t", digits=6)
            if tweak:
                with open(path) as f:
                    text = f.read()
                with open(path, "w") as f:
                    f.write(tweak(text))
            return C.check_file(path)

    def test_a_written_cube_passes(self):
        self.assertEqual(self.check(box((0, 0, 0), (1, 1, 1)))["why"], [])

    def test_flipped_triangles_fail_even_with_their_normals_flipped_too(self):
        random.seed(1)
        tris = box((0, 0, 0), (1, 1, 1)) * 1 + box((3, 0, 0), (4, 1, 1))
        r = self.check(flip(tris, set(random.sample(range(len(tris)), 3))))
        self.assertTrue(any("same way" in w for w in r["why"]), r["why"])
        self.assertGreater(r["inconsistent"], 0)

    def test_a_stored_normal_that_disagrees_with_the_winding_fails(self):
        r = self.check(box((0, 0, 0), (1, 1, 1)), lambda t: re.sub(r"facet normal \S+ \S+ \S+", "facet normal 0.6 0.8 0", t, count=1))
        self.assertTrue(any("stored normals" in w for w in r["why"]), r["why"])

    def test_a_missing_face_and_a_repeated_triangle_fail(self):
        self.assertTrue(any("boundary" in w for w in self.check(box((0, 0, 0), (1, 1, 1))[:-2])["why"]))
        tris = box((0, 0, 0), (1, 1, 1))
        self.assertTrue(any("repeated" in w for w in self.check(tris + [tris[0]])["why"]))

    def test_two_cubes_touching_along_an_edge_pass_with_one_contact(self):
        r = self.check(box((0, 0, 0), (1, 1, 1)) + box((1, 1, 0), (2, 2, 1)))
        self.assertEqual((r["why"], r["bodies"], r["contacts"]), ([], 2, 1))


if __name__ == "__main__":
    unittest.main(verbosity=1)
