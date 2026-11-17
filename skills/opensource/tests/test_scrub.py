"""Tests for scripts/scrub.py. Each test runs the script as a subprocess on temporary files.

Set OPENSOURCE_SCRIPTS_DIR to point the tests at another copy of the scripts
(tests/mutation_driver.py does this to run them against deliberately broken copies).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCRIPTS = os.environ.get("OPENSOURCE_SCRIPTS_DIR") or os.path.join(SKILL, "scripts")
SCRUB = os.path.join(SCRIPTS, "scrub.py")
LEAK = os.path.join(SCRIPTS, "leak_search.py")
SAMPLE = os.path.join(SKILL, "examples", "sample-tool")
EXAMPLE_RULES = os.path.join(SKILL, "scrub-rules.example.json")
EXAMPLE_TERMS = os.path.join(SKILL, "leak-terms.example.txt")


def run(script, *args):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, script] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env)


def write(root, rel, text, newline=""):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline=newline) as handle:
        handle.write(text)
    return path


def read(root, rel):
    with open(os.path.join(root, rel), "r", encoding="utf-8", newline="") as handle:
        return handle.read()


class ScrubTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = os.path.join(self._tmp.name, "target")
        os.makedirs(self.root)
        self.rules_path = os.path.join(self._tmp.name, "rules.json")

    def scrub(self, rules, *extra):
        with open(self.rules_path, "w", encoding="utf-8") as handle:
            json.dump(rules, handle)
        return run(SCRUB, self.rules_path, self.root, *extra)

    # replacing and reporting

    def test_replaces_literal_text_and_reports_the_rule(self):
        write(self.root, "a.txt", "alpha beta alpha\n")
        result = self.scrub([{"file": "a.txt", "find": "alpha", "replace": "gamma"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "a.txt"), "gamma beta gamma\n")
        self.assertEqual(result.stdout, "rule 1: replaced 2 in 1 files\n")

    def test_find_is_literal_not_a_pattern(self):
        write(self.root, "a.txt", "a.c abc\n")
        result = self.scrub([{"file": "a.txt", "find": "a.c", "replace": "X"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "a.txt"), "X abc\n")

    def test_report_counts_files_and_occurrences_across_a_glob(self):
        write(self.root, "a.txt", "x x\n")
        write(self.root, "b.txt", "x\n")
        write(self.root, "c.md", "x\n")
        result = self.scrub([{"file": "*.txt", "find": "x", "replace": "y"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "rule 1: replaced 3 in 2 files\n")
        self.assertEqual(read(self.root, "c.md"), "x\n")

    def test_one_report_line_per_rule_in_order(self):
        write(self.root, "a.txt", "one two\n")
        result = self.scrub([
            {"file": "a.txt", "find": "one", "replace": "1"},
            {"file": "a.txt", "find": "two", "replace": "2"},
        ])
        self.assertEqual(result.stdout, "rule 1: replaced 1 in 1 files\nrule 2: replaced 1 in 1 files\n")

    def test_later_rule_sees_the_result_of_an_earlier_rule(self):
        write(self.root, "a.txt", "first\n")
        result = self.scrub([
            {"file": "a.txt", "find": "first", "replace": "second"},
            {"file": "a.txt", "find": "second", "replace": "third"},
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "a.txt"), "third\n")

    def test_recursive_glob_reaches_nested_files(self):
        write(self.root, "top.py", "secret\n")
        write(self.root, "deep/er/inner.py", "secret\n")
        result = self.scrub([{"file": "**/*.py", "find": "secret", "replace": "clean"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "deep/er/inner.py"), "clean\n")
        self.assertEqual(read(self.root, "top.py"), "clean\n")

    def test_replace_may_be_empty(self):
        write(self.root, "a.txt", "keep DROP keep\n")
        result = self.scrub([{"file": "a.txt", "find": " DROP", "replace": ""}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "a.txt"), "keep keep\n")

    def test_line_endings_are_preserved(self):
        write(self.root, "a.txt", "one\r\ntwo\r\n")
        result = self.scrub([{"file": "a.txt", "find": "two", "replace": "2"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "a.txt"), "one\r\n2\r\n")

    def test_multi_line_find_works(self):
        write(self.root, "a.txt", "line one\nline two\nline three\n")
        result = self.scrub([{"file": "a.txt", "find": "one\nline two", "replace": "merged"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "a.txt"), "line merged\nline three\n")

    def test_files_that_no_rule_matches_are_left_alone(self):
        path = write(self.root, "untouched.txt", "alpha\n")
        before = os.stat(path).st_mtime_ns
        write(self.root, "a.txt", "alpha\n")
        result = self.scrub([{"file": "a.txt", "find": "alpha", "replace": "beta"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "untouched.txt"), "alpha\n")
        self.assertEqual(os.stat(path).st_mtime_ns, before)

    def test_files_inside_the_git_folder_are_never_matched(self):
        write(self.root, ".git/config", "alpha\n")
        result = self.scrub([{"file": ".git/config", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(read(self.root, ".git/config"), "alpha\n")

    def test_a_symbolic_link_is_not_followed(self):
        outside = write(self._tmp.name, "outside.txt", "alpha\n")
        os.symlink(outside, os.path.join(self.root, "link.txt"))
        result = self.scrub([{"file": "link.txt", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(read(self._tmp.name, "outside.txt"), "alpha\n")

    def test_a_symbolic_link_to_a_file_inside_the_target_is_not_followed(self):
        write(self.root, "real.txt", "alpha\n")
        os.symlink(os.path.join(self.root, "real.txt"), os.path.join(self.root, "link.txt"))
        result = self.scrub([{"file": "link.txt", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(read(self.root, "real.txt"), "alpha\n")

    def test_a_symlinked_folder_leading_outside_the_target_is_never_written(self):
        write(self._tmp.name, "outside/x.yml", "alpha\n")
        os.symlink(os.path.join(self._tmp.name, "outside"), os.path.join(self.root, "linked"))
        result = self.scrub([{"file": "**/*.yml", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("MISSING rule 1: alpha", result.stdout)
        self.assertEqual(read(self._tmp.name, "outside/x.yml"), "alpha\n")

    def test_a_symlinked_folder_to_a_sibling_sharing_the_target_name_prefix_is_never_written(self):
        sibling = self.root + "-more"
        write(sibling, "x.yml", "alpha\n")
        os.symlink(sibling, os.path.join(self.root, "linked"))
        result = self.scrub([{"file": "**/*.yml", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(read(sibling, "x.yml"), "alpha\n")

    def test_a_symlinked_folder_inside_the_target_is_still_matched(self):
        write(self.root, "real/x.yml", "alpha\n")
        os.symlink(os.path.join(self.root, "real"), os.path.join(self.root, "alias"))
        result = self.scrub([{"file": "alias/*.yml", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(read(self.root, "real/x.yml"), "x\n")

    def test_star_globs_do_not_match_hidden_folders(self):
        write(self.root, "a.yml", "alpha\n")
        write(self.root, ".github/ci.yml", "alpha\n")
        result = self.scrub([{"file": "**/*.yml", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "rule 1: replaced 1 in 1 files\n")
        self.assertEqual(read(self.root, "a.yml"), "x\n")
        self.assertEqual(read(self.root, ".github/ci.yml"), "alpha\n")

    def test_a_glob_that_names_the_hidden_folder_matches_it(self):
        write(self.root, ".github/ci.yml", "alpha\n")
        result = self.scrub([{"file": ".github/**/*.yml", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(read(self.root, ".github/ci.yml"), "x\n")

    def test_folders_matched_by_a_glob_are_skipped(self):
        write(self.root, "a.txt", "alpha\n")
        os.makedirs(os.path.join(self.root, "folder"))
        result = self.scrub([{"file": "*", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "rule 1: replaced 1 in 1 files\n")

    def test_file_mode_is_preserved(self):
        path = write(self.root, "run.sh", "alpha\n")
        os.chmod(path, 0o755)
        result = self.scrub([{"file": "run.sh", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(os.stat(path).st_mode & 0o777, 0o755)

    def test_no_temporary_files_are_left_behind(self):
        write(self.root, "a.txt", "alpha\n")
        write(self.root, "b.txt", "alpha\n")
        result = self.scrub([{"file": "*.txt", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sorted(os.listdir(self.root)), ["a.txt", "b.txt"])

    def test_a_file_whose_text_does_not_change_is_not_rewritten(self):
        path = write(self.root, "a.txt", "alpha\n")
        os.utime(path, (1000000000, 1000000000))
        result = self.scrub([{"file": "a.txt", "find": "alpha", "replace": "alpha"}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(int(os.stat(path).st_mtime), 1000000000)

    # missing targets

    def test_find_text_absent_exits_1_and_names_the_rule(self):
        write(self.root, "a.txt", "alpha\n")
        result = self.scrub([{"file": "a.txt", "find": "not here", "replace": "x"}])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "MISSING rule 1: not here\n")

    def test_glob_matching_no_file_exits_1(self):
        write(self.root, "a.txt", "alpha\n")
        result = self.scrub([{"file": "nothing/*.txt", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "MISSING rule 1: alpha\n")

    def test_find_absent_from_one_of_several_matched_files_exits_1(self):
        write(self.root, "a.txt", "alpha\n")
        write(self.root, "b.txt", "no match here\n")
        result = self.scrub([{"file": "*.txt", "find": "alpha", "replace": "x"}])
        self.assertEqual(result.returncode, 1)
        self.assertIn("MISSING rule 1: alpha", result.stdout)
        self.assertEqual(read(self.root, "a.txt"), "alpha\n")

    def test_missing_rule_is_numbered_by_its_position(self):
        write(self.root, "a.txt", "alpha beta\n")
        result = self.scrub([
            {"file": "a.txt", "find": "alpha", "replace": "x"},
            {"file": "a.txt", "find": "absent", "replace": "y"},
        ])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "MISSING rule 2: absent\n")

    def test_every_missing_rule_is_reported(self):
        write(self.root, "a.txt", "alpha\n")
        result = self.scrub([
            {"file": "a.txt", "find": "gone one", "replace": "x"},
            {"file": "a.txt", "find": "gone two", "replace": "y"},
        ])
        self.assertEqual(result.stdout, "MISSING rule 1: gone one\nMISSING rule 2: gone two\n")

    def test_a_missing_rule_writes_nothing_even_when_earlier_rules_were_fine(self):
        write(self.root, "a.txt", "alpha beta\n")
        write(self.root, "b.txt", "alpha\n")
        result = self.scrub([
            {"file": "*.txt", "find": "alpha", "replace": "x"},
            {"file": "a.txt", "find": "absent", "replace": "y"},
        ])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(read(self.root, "a.txt"), "alpha beta\n")
        self.assertEqual(read(self.root, "b.txt"), "alpha\n")
        self.assertNotIn("replaced", result.stdout)

    def test_running_the_same_rules_twice_fails_the_second_time(self):
        write(self.root, "a.txt", "alpha\n")
        rules = [{"file": "a.txt", "find": "alpha", "replace": "beta"}]
        self.assertEqual(self.scrub(rules).returncode, 0)
        second = self.scrub(rules)
        self.assertEqual(second.returncode, 1)
        self.assertEqual(second.stdout, "MISSING rule 1: alpha\n")

    # count

    def test_count_that_matches_is_accepted(self):
        write(self.root, "a.txt", "x x x\n")
        result = self.scrub([{"file": "a.txt", "find": "x", "replace": "y", "count": 3}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "a.txt"), "y y y\n")

    def test_count_too_low_exits_1_and_writes_nothing(self):
        write(self.root, "a.txt", "x x x\n")
        result = self.scrub([{"file": "a.txt", "find": "x", "replace": "y", "count": 2}])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "MISSING rule 1: x\n")
        self.assertEqual(read(self.root, "a.txt"), "x x x\n")

    def test_count_too_high_exits_1(self):
        write(self.root, "a.txt", "x\n")
        result = self.scrub([{"file": "a.txt", "find": "x", "replace": "y", "count": 2}])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "MISSING rule 1: x\n")

    def test_count_is_the_total_across_all_matched_files(self):
        write(self.root, "a.txt", "x\n")
        write(self.root, "b.txt", "x x\n")
        ok = self.scrub([{"file": "*.txt", "find": "x", "replace": "y", "count": 3}])
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(ok.stdout, "rule 1: replaced 3 in 2 files\n")

    # dry run

    def test_dry_run_writes_nothing(self):
        path = write(self.root, "a.txt", "alpha\n")
        before = os.stat(path).st_mtime_ns
        result = self.scrub([{"file": "a.txt", "find": "alpha", "replace": "beta"}], "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "a.txt"), "alpha\n")
        self.assertEqual(os.stat(path).st_mtime_ns, before)

    def test_dry_run_prints_the_same_lines_as_a_real_run(self):
        write(self.root, "a.txt", "alpha alpha\n")
        rules = [{"file": "a.txt", "find": "alpha", "replace": "beta"}]
        dry = self.scrub(rules, "--dry-run")
        real = self.scrub(rules)
        self.assertEqual(dry.stdout, "rule 1: replaced 2 in 1 files\n")
        self.assertEqual(dry.stdout, real.stdout)

    def test_dry_run_still_fails_on_a_missing_target(self):
        write(self.root, "a.txt", "alpha\n")
        result = self.scrub([{"file": "a.txt", "find": "absent", "replace": "x"}], "--dry-run")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "MISSING rule 1: absent\n")

    def test_dry_run_flag_may_come_before_the_paths(self):
        write(self.root, "a.txt", "alpha\n")
        with open(self.rules_path, "w", encoding="utf-8") as handle:
            json.dump([{"file": "a.txt", "find": "alpha", "replace": "beta"}], handle)
        result = run(SCRUB, "--dry-run", self.rules_path, self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read(self.root, "a.txt"), "alpha\n")

    # usage errors, all exit 2

    def assert_usage_error(self, result):
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("usage:", result.stderr)

    def test_no_arguments_exits_2(self):
        self.assert_usage_error(run(SCRUB))

    def test_one_argument_exits_2(self):
        self.assert_usage_error(run(SCRUB, self.rules_path))

    def test_three_positional_arguments_exit_2(self):
        write(self.root, "a.txt", "alpha\n")
        with open(self.rules_path, "w", encoding="utf-8") as handle:
            json.dump([{"file": "a.txt", "find": "alpha", "replace": "x"}], handle)
        self.assert_usage_error(run(SCRUB, self.rules_path, self.root, "extra"))
        self.assertEqual(read(self.root, "a.txt"), "alpha\n")

    def test_unknown_flag_exits_2(self):
        write(self.root, "a.txt", "alpha\n")
        result = self.scrub([{"file": "a.txt", "find": "alpha", "replace": "x"}], "--force")
        self.assert_usage_error(result)
        self.assertEqual(read(self.root, "a.txt"), "alpha\n")

    def test_missing_rules_file_exits_2(self):
        self.assert_usage_error(run(SCRUB, os.path.join(self._tmp.name, "nope.json"), self.root))

    def test_rules_file_that_is_not_json_exits_2(self):
        with open(self.rules_path, "w", encoding="utf-8") as handle:
            handle.write("{not json")
        self.assert_usage_error(run(SCRUB, self.rules_path, self.root))

    def test_rules_file_that_is_not_a_list_exits_2(self):
        self.assert_usage_error(self.scrub({"file": "a", "find": "b", "replace": "c"}))

    def test_rules_file_that_is_an_empty_object_exits_2(self):
        self.assert_usage_error(self.scrub({}))

    def test_rule_missing_a_required_key_exits_2(self):
        self.assert_usage_error(self.scrub([{"file": "a.txt", "find": "alpha"}]))

    def test_rule_with_a_non_string_value_exits_2(self):
        self.assert_usage_error(self.scrub([{"file": "a.txt", "find": 5, "replace": "x"}]))

    def test_rule_with_an_unknown_key_exits_2(self):
        write(self.root, "a.txt", "alpha\n")
        result = self.scrub([{"file": "a.txt", "find": "alpha", "replace": "x", "cnt": 1}])
        self.assert_usage_error(result)
        self.assertEqual(read(self.root, "a.txt"), "alpha\n")

    def test_rule_with_an_empty_find_exits_2(self):
        write(self.root, "a.txt", "alpha\n")
        self.assert_usage_error(self.scrub([{"file": "a.txt", "find": "", "replace": "x"}]))
        self.assertEqual(read(self.root, "a.txt"), "alpha\n")

    def test_rule_with_a_bad_count_exits_2(self):
        for bad in ("2", 0, -1, 1.5, True):
            with self.subTest(count=bad):
                write(self.root, "a.txt", "alpha\n")
                self.assert_usage_error(
                    self.scrub([{"file": "a.txt", "find": "alpha", "replace": "x", "count": bad}]))

    def test_glob_that_climbs_out_of_the_target_exits_2(self):
        write(self.root, "a.txt", "alpha\n")
        outside = os.path.join(self._tmp.name, "outside.txt")
        write(self._tmp.name, "outside.txt", "alpha\n")
        self.assert_usage_error(self.scrub([{"file": "../outside.txt", "find": "alpha", "replace": "x"}]))
        self.assertEqual(read(self._tmp.name, "outside.txt"), "alpha\n")
        self.assertTrue(os.path.exists(outside))

    def test_absolute_glob_exits_2(self):
        outside = write(self._tmp.name, "abs.txt", "alpha\n")
        self.assert_usage_error(self.scrub([{"file": outside, "find": "alpha", "replace": "x"}]))
        self.assertEqual(read(self._tmp.name, "abs.txt"), "alpha\n")

    def test_target_that_is_not_a_folder_exits_2(self):
        with open(self.rules_path, "w", encoding="utf-8") as handle:
            json.dump([], handle)
        self.assert_usage_error(run(SCRUB, self.rules_path, os.path.join(self._tmp.name, "absent")))

    def test_matched_file_that_is_not_utf8_exits_2(self):
        path = os.path.join(self.root, "blob.bin")
        with open(path, "wb") as handle:
            handle.write(b"\xff\xfe alpha")
        result = self.scrub([{"file": "blob.bin", "find": "alpha", "replace": "x"}])
        self.assert_usage_error(result)
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), b"\xff\xfe alpha")

    def test_empty_rule_list_is_a_clean_no_op(self):
        write(self.root, "a.txt", "alpha\n")
        result = self.scrub([])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    # the shipped example

    def test_example_rules_clean_the_sample_so_leak_search_finds_nothing(self):
        copy = os.path.join(self._tmp.name, "sample")
        shutil.copytree(SAMPLE, copy)
        before = run(LEAK, EXAMPLE_TERMS, copy, "--allow", "LICENSE")
        self.assertEqual(before.returncode, 1, "the sample must hold planted terms")
        scrubbed = run(SCRUB, EXAMPLE_RULES, copy)
        self.assertEqual(scrubbed.returncode, 0, scrubbed.stdout + scrubbed.stderr)
        after = run(LEAK, EXAMPLE_TERMS, copy, "--allow", "LICENSE")
        self.assertEqual(after.returncode, 0, after.stdout)
        self.assertEqual(after.stdout, "")

    def test_example_rules_fail_on_a_second_run(self):
        copy = os.path.join(self._tmp.name, "sample")
        shutil.copytree(SAMPLE, copy)
        self.assertEqual(run(SCRUB, EXAMPLE_RULES, copy).returncode, 0)
        again = run(SCRUB, EXAMPLE_RULES, copy)
        self.assertEqual(again.returncode, 1)
        self.assertIn("MISSING rule 1:", again.stdout)


if __name__ == "__main__":
    unittest.main()
