"""Tests for the pure and the flow parts of tests/mutation_driver.py.

The driver is loaded from OPENSOURCE_SCRIPTS_DIR when it holds a copy of
mutation_driver.py, so the driver can run these tests against a deliberately
broken copy of itself, the same way it does for the scripts.
"""
import contextlib
import importlib.util
import io
import os
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
COPY = os.path.join(os.environ.get("OPENSOURCE_SCRIPTS_DIR") or "", "mutation_driver.py")
DRIVER_PATH = COPY if os.environ.get("OPENSOURCE_SCRIPTS_DIR") and os.path.exists(COPY) else os.path.join(HERE, "mutation_driver.py")

RAN_OK = "----------------------------------------------------------------------\nRan 1 test in 0.001s\n\nOK\n"
RAN_SKIPPED = "----------------------------------------------------------------------\nRan 1 test in 0.001s\n\nOK (skipped=1)\n"
RAN_FAILED = "======\nFAIL: test_x\n----------------------------------------------------------------------\nRan 1 test in 0.001s\n\nFAILED (failures=1)\n"


def load_driver():
    spec = importlib.util.spec_from_file_location("mutation_driver_under_test", DRIVER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.driver = load_driver()

    def test_a_clean_run_is_a_pass(self):
        self.assertEqual(self.driver.classify(0, RAN_OK), self.driver.PASSED)

    def test_a_run_that_skips_itself_is_not_a_pass(self):
        self.assertEqual(self.driver.classify(0, RAN_SKIPPED), self.driver.SKIPPED)

    def test_the_word_skipped_before_the_last_line_does_not_make_a_pass_a_skip(self):
        text = "a log line that says skipped=3\n" + RAN_OK
        self.assertEqual(self.driver.classify(0, text), self.driver.PASSED)

    def test_a_timeout_is_a_timeout_and_not_a_failure(self):
        self.assertEqual(self.driver.classify(None, ""), self.driver.TIMED_OUT)

    def test_a_failing_run_is_a_failure(self):
        self.assertEqual(self.driver.classify(1, RAN_FAILED), self.driver.FAILED)

    def test_an_exit_0_with_no_test_run_is_unclear_and_not_a_pass(self):
        self.assertEqual(self.driver.classify(0, ""), self.driver.UNCLEAR)
        self.assertEqual(self.driver.classify(0, "NO TESTS RAN\n"), self.driver.UNCLEAR)


class MainTests(unittest.TestCase):
    def setUp(self):
        self.driver = load_driver()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.scripts = os.path.join(self._tmp.name, "scripts")
        os.makedirs(self.scripts)
        with open(os.path.join(self.scripts, "x.py"), "w", encoding="utf-8") as handle:
            handle.write("a = 1\n")

    def run_main(self, mutations, results):
        """results maps a test id to the list of (code, stderr) answers its runs give, in order."""
        calls = []

        def fake_run_test(scripts_dir, test_id):
            calls.append(test_id)
            # a run the test did not expect answers as a pass, so a driver that goes on too far fails an assertion
            return results[test_id].pop(0) if results[test_id] else (0, RAN_OK)

        out = io.StringIO()
        with mock.patch.object(self.driver, "SCRIPTS", self.scripts), \
                mock.patch.object(self.driver, "MUTATIONS", mutations), \
                mock.patch.object(self.driver, "run_test", fake_run_test), \
                contextlib.redirect_stdout(out):
            code = self.driver.main()
        return code, out.getvalue().splitlines(), calls

    def test_a_skipped_test_is_not_run_and_its_mutation_is_neither_killed_nor_survived(self):
        mutations = [("m-skipped", "x.py", "a = 1", "a = 2", "T.test_skipped"),
                     ("m-killed", "x.py", "a = 1", "a = 3", "T.test_real")]
        results = {"T.test_skipped": [(0, RAN_SKIPPED), (0, RAN_OK)],
                   "T.test_real": [(0, RAN_OK), (1, RAN_FAILED)]}
        code, lines, calls = self.run_main(mutations, results)
        self.assertEqual(code, 0, lines)
        self.assertIn("not run here: T.test_skipped (skipped)", lines)
        self.assertIn("killed: m-killed", lines)
        self.assertNotIn("survived: m-skipped (test_skipped)", lines)
        self.assertEqual(lines[-1], "mutations: 2, killed: 1, survived: 0, not run: 1")
        self.assertEqual(calls.count("T.test_skipped"), 1)

    def test_a_survivor_gives_exit_1_and_is_counted(self):
        mutations = [("m-alive", "x.py", "a = 1", "a = 2", "T.test_real")]
        code, lines, _ = self.run_main(mutations, {"T.test_real": [(0, RAN_OK), (0, RAN_OK)]})
        self.assertEqual(code, 1)
        self.assertIn("survived: m-alive (test_real)", lines)
        self.assertEqual(lines[-1], "mutations: 1, killed: 0, survived: 1, not run: 0")

    def test_a_mutation_run_that_times_out_is_reported_and_never_killed(self):
        mutations = [("m-slow", "x.py", "a = 1", "a = 2", "T.test_real")]
        code, lines, _ = self.run_main(mutations, {"T.test_real": [(0, RAN_OK), (None, "")]})
        self.assertEqual(code, 1, lines)
        self.assertIn("timed out: m-slow", lines)
        self.assertNotIn("killed: m-slow", lines)
        self.assertEqual(lines[-1], "mutations: 1, killed: 0, survived: 0, not run: 0, timed out: 1")

    def test_a_setup_run_that_times_out_is_a_setup_problem(self):
        mutations = [("m-slow", "x.py", "a = 1", "a = 2", "T.test_real")]
        code, lines, calls = self.run_main(mutations, {"T.test_real": [(None, "")]})
        self.assertEqual(code, 1)
        self.assertEqual(lines, ["timed out: T.test_real"])
        self.assertEqual(calls, ["T.test_real"])

    def test_a_setup_run_that_fails_is_a_setup_problem(self):
        mutations = [("m", "x.py", "a = 1", "a = 2", "T.test_real")]
        code, lines, _ = self.run_main(mutations, {"T.test_real": [(1, RAN_FAILED)]})
        self.assertEqual(code, 1)
        self.assertEqual(lines, ["setup problem: T.test_real does not pass on the unbroken scripts"])


if __name__ == "__main__":
    unittest.main()
