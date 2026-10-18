"""Tests of scripts/citation.py: python scripts/test_citation.py (standard library only; build_all.sh runs it).

The expected strings are frozen here on purpose: a change to a citation's wording or fields has to be made twice.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aijdata as D  # noqa: E402
import check_citation as K  # noqa: E402
import citation as C  # noqa: E402

REL = C.Release("1.2.3", "2030-01-02", "abcdef012345" + "0" * 52)
ROOT = "https://sustainableurbansystems.com/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ/api"
T = "AIJ Urban Wind Environment benchmark, Cases A-M: cleaned wind-tunnel and field data, geometry and validation API"

API_APA = f"Sustainable Urban Systems Lab. (2030). {T} (Version 1.2.3) [Data set]. {ROOT}/1.2.3/index.json"
API_BIBTEX = f'''@misc{{aijuwe_api_1_2_3,
  author    = "{{Sustainable Urban Systems Lab}}",
  title     = "{{{T}}}",
  year      = "2030",
  version   = "1.2.3",
  publisher = "Sustainable Urban Systems Lab",
  url       = "{ROOT}/1.2.3/index.json",
  note      = "Data set; data version abcdef012345"
}}'''
API_CSL = {"id": "aijuwe-api-1.2.3", "type": "dataset", "title": T, "author": [{"literal": "Sustainable Urban Systems Lab"}],
           "issued": {"date-parts": [[2030, 1, 2]]}, "version": "1.2.3", "publisher": "Sustainable Urban Systems Lab",
           "URL": f"{ROOT}/1.2.3/index.json", "note": "Data version abcdef012345"}
PAPER_APA = ("Kikumoto, H., Okaze, T., Yoshie, R., Tachibana, T., Ishihara, T., Nonomura, Y., Kiyota, N., Kondo, H., Mochida, A., "
             "& Tominaga, Y. (2026). Comprehensive Experimental Database for Validating CFD Simulations in Urban Wind Environment: "
             "Benchmark Cases Curated by the Architectural Institute of Japan. Japan Architectural Review, 9(1), e70083. "
             "https://doi.org/10.1002/2475-8876.70083")
CASE_A_APA = ("Ishihara, T., Hibi, K., Tominaga, Y., Kikumoto, H., & Okaze, T. (2025). AIJ UWE Benchmark Dataset – Case A (112): "
              "Wind Tunnel Experiment for Flow around a 1:1:2 Shape Building Model [Data set]. Zenodo. "
              "https://doi.org/10.5281/zenodo.15050147")
CASE_A_BIBTEX = '''@misc{aijuwe_case_a,
  author    = "Ishihara, Takeshi and Hibi, Kazuki and Tominaga, Yoshihide and Kikumoto, Hideki and Okaze, Tsubasa",
  title     = "{AIJ UWE Benchmark Dataset -- Case A (112): Wind Tunnel Experiment for Flow around a 1:1:2 Shape Building Model}",
  year      = "2025",
  publisher = "Zenodo",
  doi       = "10.5281/zenodo.15050147",
  url       = "https://doi.org/10.5281/zenodo.15050147",
  note      = "Data set"
}'''


class Frozen(unittest.TestCase):
    def test_api(self):
        self.assertEqual(C.api_apa(REL), API_APA)
        self.assertEqual(C.api_bibtex(REL), API_BIBTEX)
        self.assertEqual(C.api_csl(REL), API_CSL)
        self.assertEqual(C.api(REL), {"title": T, "version": "1.2.3", "url": f"{ROOT}/1.2.3/index.json", "doi": None, "apa": API_APA,
                                      "bibtex": API_BIBTEX, "csl_json": API_CSL,
                                      "release_url": C.REPO_URL + "/releases/tag/v1.2.3"})

    def test_paper(self):
        self.assertEqual(C.paper_apa(), PAPER_APA)
        self.assertIn('  doi     = "10.1002/2475-8876.70083"\n}', C.paper_bibtex())

    def test_case_a(self):
        self.assertEqual(C.case_apa("A", D.CASES["A"]), CASE_A_APA)
        self.assertEqual(C.case_bibtex("A", D.CASES["A"]), CASE_A_BIBTEX)

    def test_case_f_names_no_investigation_as_author(self):
        # the readme of Case F names no data collectors: its record's authors are the three editors
        self.assertEqual(C.case_people(D.CASES["F"]), [("Tominaga", "Yoshihide"), ("Kikumoto", "Hideki"), ("Okaze", "Tsubasa")])
        self.assertTrue(C.case_apa("F", D.CASES["F"]).startswith("Tominaga, Y., Kikumoto, H., & Okaze, T. (2025). "))


class Release(unittest.TestCase):
    def test_pinned_url_follows_version(self):
        other = C.Release("1.2.4", REL.date, REL.data_version)
        self.assertEqual(C.pinned_url("1.2.3"), f"{ROOT}/1.2.3/index.json")
        for render in (C.api_apa, C.api_bibtex, lambda r: json.dumps(C.api_csl(r)), lambda r: C.cff(r, D.CASES)):
            self.assertIn("/api/1.2.3/", render(REL))
            self.assertNotIn("/api/1.2.3/", render(other))
            self.assertIn("/api/1.2.4/", render(other))

    def test_data_version_is_in_the_note_only(self):
        self.assertIn("data version abcdef012345", C.api_bibtex(REL))
        self.assertNotIn("abcdef012345", C.api_apa(REL) + C.cff(REL, D.CASES) + C.zenodo_json(D.CASES))

    def test_no_doi_is_printed_before_one_exists(self):
        self.assertIsNone(C.API_DOI)
        self.assertNotIn("doi", C.api_bibtex(REL))
        self.assertNotIn("DOI", C.api_csl(REL))
        self.assertNotRegex(C.cff(REL, D.CASES).split("references:")[0], r"(?m)^doi:")

    def test_a_minted_doi_goes_everywhere(self):
        with mock.patch.object(C, "API_DOI", "10.5281/zenodo.1"):
            self.assertTrue(C.api_apa(REL).endswith("[Data set]. https://doi.org/10.5281/zenodo.1"))
            self.assertIn('doi       = "10.5281/zenodo.1"', C.api_bibtex(REL))
            self.assertEqual(C.api_csl(REL)["DOI"], "10.5281/zenodo.1")
            self.assertEqual(C.api(REL)["doi"], "10.5281/zenodo.1")
            self.assertRegex(C.cff(REL, D.CASES), r'(?m)^doi: "10.5281/zenodo.1"$')

    def test_year_is_the_release_year(self):
        self.assertIn("(2030)", C.api_apa(REL))
        self.assertIn('year      = "2030"', C.api_bibtex(REL))


class Cases(unittest.TestCase):
    def test_every_case_has_a_record_and_its_doi_is_cited(self):
        self.assertEqual(sorted(C.ZENODO), sorted(D.CASES))
        for cid, meta in D.CASES.items():
            c = C.case(cid, meta)
            self.assertIn(f"https://doi.org/{meta['doi']}", c["apa"], cid)
            self.assertIn(f'doi       = "{meta["doi"]}"', c["bibtex"], cid)
            self.assertIn(f"Case {cid} (", c["apa"])
            self.assertTrue(re.search(r"\(2025\)", c["apa"]))

    def test_the_title_names_the_cases_there_are(self):
        self.assertIn(f"Cases {D.CASE_IDS[0]}-{D.CASE_IDS[-1]}:", C.TITLE)

    def test_a_case_without_a_record_fails_loudly(self):
        with self.assertRaises(KeyError):
            C.case("Z", D.CASES["A"])

    def test_the_paper_is_the_one_aijdata_cites(self):
        for family, _ in C.PAPER["authors"]:
            self.assertIn(family, D.CITATION["benchmark"])
        self.assertIn(C.PAPER["doi"], D.CITATION["benchmark"])
        self.assertIn(C.GUIDELINES["doi"], D.CITATION["guidelines"])


class Files(unittest.TestCase):
    def test_every_bibtex_is_balanced_and_complete(self):
        entries = [C.api_bibtex(REL), C.paper_bibtex()] + [C.case_bibtex(c, m) for c, m in D.CASES.items()]
        for e in entries:
            self.assertEqual(K.bibtex_problems(e.split(",")[0], e), [])
        self.assertTrue(K.bibtex_problems("x", API_BIBTEX[:-1]))                       # a lost closing brace
        self.assertTrue(K.bibtex_problems("x", API_BIBTEX.replace('publisher = "Sustainable Urban Systems Lab"', 'publisher = ""')))

    def test_nothing_is_a_placeholder(self):
        texts = [C.api_apa(REL), C.api_bibtex(REL), json.dumps(C.api_csl(REL)), C.paper_apa(), C.paper_bibtex(),
                 C.site_include(REL), C.readme_block(REL), C.cff(REL, D.CASES), C.zenodo_json(D.CASES)]
        texts += ["\n".join(C.case_section(c, m)) for c, m in D.CASES.items()]
        for t in texts:
            self.assertIsNone(K.PLACEHOLDER.search(t), K.PLACEHOLDER.search(t) and K.PLACEHOLDER.search(t).group(0))

    def test_no_double_brace_a_page_could_read_as_liquid(self):
        for t in (C.site_include(REL), C.readme_block(REL), "\n".join(C.case_section("A", D.CASES["A"]))):
            rest = re.sub(r"\{\{ '[^']*' \| relative_url \}\}", "", t)      # the site links are Liquid on purpose
            self.assertNotIn("{{", rest)
            self.assertNotIn("{%", rest)

    def test_cff_is_found_by_release_py_and_cites_the_dataset(self):
        cff = C.cff(REL, D.CASES)
        self.assertEqual(re.search(r"^version:\s*['\"]?([^'\"\s]+)", cff, re.M).group(1), "1.2.3")      # the patterns release.py check uses
        self.assertEqual(re.search(r"^date-released:\s*['\"]?(\d{4}-\d{2}-\d{2})", cff, re.M).group(1), "2030-01-02")
        self.assertIn("\ntype: dataset\n", cff)
        self.assertIn(f'\ntitle: "{T}"\n', cff)
        self.assertNotIn("preferred-citation", cff)
        self.assertEqual(cff.count("\n  - type: "), 2 + len(D.CASES))
        for meta in D.CASES.values():
            self.assertIn(f'doi: "{meta["doi"]}"', cff)

    def test_zenodo_json(self):
        z = json.loads(C.zenodo_json(D.CASES))
        self.assertEqual((z["title"], z["upload_type"], z["license"], z["access_right"]), (T, "dataset", "cc-by-4.0", "open"))
        self.assertEqual(z["creators"], [{"name": "Sustainable Urban Systems Lab"}])
        ids = [(r["relation"], r["identifier"]) for r in z["related_identifiers"]]
        self.assertEqual(ids[0], ("isDescribedBy", "10.1002/2475-8876.70083"))
        self.assertEqual(sorted(i for r, i in ids[1:]), sorted(m["doi"] for m in D.CASES.values()))

    def test_readme_block_is_replaced_and_nothing_else(self):
        text = "before\n\n<!--cite-->\n\nstale\n\n<!--/cite-->\n\nafter \\& 1\n"
        new = C.readme_with_cite(text, REL)
        self.assertTrue(new.startswith("before\n\n<!--cite-->\n\n") and new.endswith("<!--/cite-->\n\nafter \\& 1\n"))
        self.assertIn(API_APA, new)
        self.assertEqual(C.readme_with_cite(new, REL), new)
        self.assertNotEqual(C.readme_with_cite(new, C.Release("1.2.4", REL.date, REL.data_version)), new)
        with self.assertRaises(ValueError):
            C.readme_with_cite("no block", REL)

    def test_data_page_section_points_to_the_api_citation(self):
        s = C.case_section("A", D.CASES["A"])
        self.assertEqual(s[0], "### Cite")
        self.assertIn(CASE_A_APA, s)
        self.assertEqual(s[-1], "API: see [About]({{ '/about/#cite' | relative_url }}).")


if __name__ == "__main__":
    unittest.main()
