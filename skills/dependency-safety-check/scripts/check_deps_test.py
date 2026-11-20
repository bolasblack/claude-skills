#!/usr/bin/env python3

import contextlib
import importlib.util
import io
import pathlib
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlsplit


SCRIPT_PATH = pathlib.Path(__file__).with_name("check-deps.py")
spec = importlib.util.spec_from_file_location("check_deps", SCRIPT_PATH)
check_deps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_deps)


class ParseArgsTest(unittest.TestCase):
    def test_defaults_to_npm_and_30_day_minimum_age(self):
        options = check_deps.parse_args(["left-pad@1.3.0"])

        self.assertEqual("npm", options["ecosystem"])
        self.assertEqual(30, options["min_age_days"])
        self.assertEqual([("left-pad", "1.3.0")], options["packages"])

    def test_accepts_custom_minimum_age(self):
        options = check_deps.parse_args(["--min-age-days", "7", "left-pad@1.3.0"])

        self.assertEqual(7, options["min_age_days"])
        self.assertEqual([("left-pad", "1.3.0")], options["packages"])

    def test_rejects_minimum_age_below_allowed_floor(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                check_deps.parse_args(["--min-age-days", "6", "left-pad@1.3.0"])


def advisory(ghsa_id, severity):
    return {"ghsa_id": ghsa_id, "severity": severity, "summary": "summary of " + ghsa_id}


class GithubAdvisoryTest(unittest.TestCase):
    def check(self, name, version, ecosystem="npm", response=()):
        with mock.patch.object(check_deps, "fetch_json", return_value=list(response)) as fetch:
            result = check_deps.check_github_advisory(name, version, ecosystem)
        query = parse_qs(urlsplit(fetch.call_args[0][0]).query)
        return result, query

    def test_asks_only_for_advisories_affecting_the_checked_version(self):
        _, query = self.check("@scope/pkg", "7.30.2")

        self.assertEqual(["@scope/pkg@7.30.2"], query["affects"])

    def test_reports_every_advisory_github_returns_for_the_version(self):
        response = [advisory("GHSA-low-%d" % i, "low") for i in range(5)]
        response.append(advisory("GHSA-crit", "critical"))

        result, query = self.check("undici", "7.30.0", response=response)

        self.assertEqual(["100"], query["per_page"])
        self.assertEqual(6, len(result["findings"]))
        self.assertIn("error", [f["severity"] for f in result["findings"]])

    def test_uses_github_names_for_pypi_and_cargo(self):
        _, pypi_query = self.check("requests", "2.31.0", "pypi")
        _, cargo_query = self.check("hyper", "0.14.10", "cargo")

        self.assertEqual(["pip"], pypi_query["ecosystem"])
        self.assertEqual(["rust"], cargo_query["ecosystem"])


class OsvTest(unittest.TestCase):
    def queried_ecosystem(self, ecosystem):
        with mock.patch.object(check_deps, "fetch_json", return_value={}) as fetch:
            check_deps.check_osv("pkg", "1.0.0", ecosystem)
        return fetch.call_args[1]["data"]["package"]["ecosystem"]

    def test_uses_osv_names_for_pypi_and_cargo(self):
        self.assertEqual("npm", self.queried_ecosystem("npm"))
        self.assertEqual("PyPI", self.queried_ecosystem("pypi"))
        self.assertEqual("crates.io", self.queried_ecosystem("cargo"))


if __name__ == "__main__":
    unittest.main()
