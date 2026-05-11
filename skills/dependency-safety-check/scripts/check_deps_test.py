#!/usr/bin/env python3

import contextlib
import importlib.util
import io
import pathlib
import unittest


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


if __name__ == "__main__":
    unittest.main()
