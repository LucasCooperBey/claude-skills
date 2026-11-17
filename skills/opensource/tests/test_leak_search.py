"""Tests for scripts/leak_search.py. Each test runs the script as a subprocess on temporary files.

Every string with the shape of a token, a private key header or a home folder path
is built at run time from pieces, so this file holds no such literal.

Set OPENSOURCE_SCRIPTS_DIR to point the tests at another copy of the scripts
(tests/mutation_driver.py does this to run them against deliberately broken copies).
"""
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCRIPTS = os.environ.get("OPENSOURCE_SCRIPTS_DIR") or os.path.join(SKILL, "scripts")
LEAK = os.path.join(SCRIPTS, "leak_search.py")
SAMPLE = os.path.join(SKILL, "examples", "sample-tool")
EXAMPLE_TERMS = os.path.join(SKILL, "leak-terms.example.txt")

SLASH = "/"
USERS_PATH = SLASH + "Users" + SLASH + "someone" + SLASH + "work"
HOME_PATH = SLASH + "home" + SLASH + "someone" + SLASH + "work"
BACKSLASH = chr(92)
WINDOWS_USERS = "C:" + BACKSLASH + "Users" + BACKSLASH + "someone"
PRIVATE_KEY_LINE = "-----" + "BEGIN " + "RSA " + "PRIVATE " + "KEY" + "-----"
PLAIN_KEY_LINE = "-----" + "BEGIN " + "PRIVATE " + "KEY" + "-----"
PGP_KEY_LINE = "-----" + "BEGIN PGP " + "PRIVATE " + "KEY " + "BLOCK" + "-----"
PUBLIC_KEY_LINE = "-----" + "BEGIN " + "PUBLIC " + "KEY" + "-----"


def run(*args, **kwargs):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, LEAK] + list(args),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env, **kwargs)


class LeakSearchTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = os.path.join(self._tmp.name, "target")
        os.makedirs(self.root)
        self.terms_path = os.path.join(self._tmp.name, "terms.txt")
        # a terms file needs at least one term; this one matches nothing in any test
        self.set_terms("unused-placeholder-term\n")

    def set_terms(self, text):
        with open(self.terms_path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def put(self, rel, text, mode="w"):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if mode == "wb":
            with open(path, "wb") as handle:
                handle.write(text)
        else:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
        return path

    def search(self, *extra):
        return run(self.terms_path, self.root, *extra)

    def assert_hit(self, text, kind, line=1):
        self.put("f.txt", text)
        result = self.search()
        self.assertEqual(result.returncode, 1, "expected a %s hit in %r" % (kind, text))
        self.assertEqual(result.stdout, "f.txt:%d: %s\n" % (line, kind))

    def assert_no_hit(self, text):
        self.put("f.txt", text)
        result = self.search()
        self.assertEqual(result.returncode, 0, "unexpected hit for %r: %s" % (text, result.stdout))
        self.assertEqual(result.stdout, "")

    # terms

    def test_a_term_hit_prints_path_line_and_term_number(self):
        self.set_terms("# my terms\n\nbluefinch\nexamplecorp\n")
        self.put("sub/notes.txt", "first line\nthe examplecorp wiki\n")
        result = self.search()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "sub/notes.txt:2: term 4\n")

    def test_term_match_ignores_case_in_the_file(self):
        self.set_terms("bluefinch\n")
        self.put("a.txt", "Project BlueFinch is internal\n")
        result = self.search()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "a.txt:1: term 1\n")

    def test_term_match_ignores_case_in_the_terms_file(self):
        self.set_terms("BLUEFINCH\n")
        self.put("a.txt", "project bluefinch is internal\n")
        result = self.search()
        self.assertEqual(result.stdout, "a.txt:1: term 1\n")

    def test_term_is_matched_as_plain_text_not_a_pattern(self):
        self.set_terms("a.b\n")
        self.put("a.txt", "axb\n")
        self.assertEqual(self.search().returncode, 0)
        self.put("a.txt", "a.b\n")
        self.assertEqual(self.search().stdout, "a.txt:1: term 1\n")

    def test_term_with_pattern_characters_does_not_crash(self):
        self.set_terms("a(b\n[x\n")
        self.put("a.txt", "a(b and [x\n")
        result = self.search()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "a.txt:1: term 1\na.txt:1: term 2\n")

    def test_comment_lines_in_the_terms_file_are_not_terms(self):
        self.set_terms("# bluefinch\nunused-placeholder-term\n")
        self.put("a.txt", "# bluefinch\n")
        self.assertEqual(self.search().returncode, 0)

    def test_blank_lines_in_the_terms_file_are_not_terms(self):
        self.set_terms("\n   \nbluefinch\n\n")
        self.put("a.txt", "an ordinary sentence\n")
        result = self.search()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_term_whitespace_is_trimmed(self):
        self.set_terms("  bluefinch  \n")
        self.put("a.txt", "bluefinch\n")
        self.assertEqual(self.search().stdout, "a.txt:1: term 1\n")

    def test_two_terms_on_one_line_give_two_hit_lines(self):
        self.set_terms("alpha\nbeta\n")
        self.put("a.txt", "beta and alpha\n")
        self.assertEqual(self.search().stdout, "a.txt:1: term 1\na.txt:1: term 2\n")

    def test_the_same_term_twice_on_a_line_is_one_hit(self):
        self.set_terms("alpha\n")
        self.put("a.txt", "alpha alpha\n")
        self.assertEqual(self.search().stdout, "a.txt:1: term 1\n")

    def test_hits_are_reported_per_file_in_path_order(self):
        self.set_terms("alpha\n")
        self.put("b.txt", "alpha\n")
        self.put("a.txt", "x\nalpha\nalpha\n")
        self.assertEqual(self.search().stdout, "a.txt:2: term 1\na.txt:3: term 1\nb.txt:1: term 1\n")

    def test_a_term_that_matches_nothing_and_a_clean_folder_exits_0_with_no_output(self):
        self.put("a.txt", "nothing to see\n")
        result = self.search()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_a_term_that_matches_nothing_still_leaves_the_built_in_patterns_on(self):
        self.put("a.txt", "mail me at someone" + "@" + "example.org\n")
        self.assertEqual(self.search().stdout, "a.txt:1: email\n")

    def assert_no_terms_refused(self, text):
        self.set_terms(text)
        self.put("a.txt", "mail me at someone" + "@" + "example.org\n")
        result = self.search()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("leak_search.py: no terms found in %s\n" % self.terms_path, result.stderr)
        self.assertNotIn("hits in", result.stderr)

    def test_an_empty_terms_file_exits_2_and_scans_nothing(self):
        self.assert_no_terms_refused("")

    def test_a_terms_file_of_only_comments_and_blank_lines_exits_2_and_scans_nothing(self):
        self.assert_no_terms_refused("# one\n\n   \n# two\n")

    def test_a_file_that_is_not_utf8_is_still_searched(self):
        self.set_terms("bluefinch\n")
        self.put("a.txt", b"\xff\xfe bluefinch\n", mode="wb")
        self.assertEqual(self.search().stdout, "a.txt:1: term 1\n")

    def test_utf8_byte_order_mark_in_the_terms_file_is_ignored(self):
        with open(self.terms_path, "wb") as handle:
            handle.write(b"\xef\xbb\xbfbluefinch\n")
        self.put("a.txt", "bluefinch\n")
        self.assertEqual(self.search().stdout, "a.txt:1: term 1\n")

    # built-in patterns

    def test_home_path_under_users_is_found(self):
        self.assert_hit("cd " + USERS_PATH + "\n", "home-path")

    def test_home_path_under_home_is_found(self):
        self.assert_hit("cd " + HOME_PATH + "\n", "home-path")

    # Rule: the account name ends where a name cannot go on: a quote, a space, a bracket,
    # a comma or the end of the line, not only a slash.
    def test_a_home_path_whose_account_name_ends_at_a_quote_is_found(self):
        self.assert_hit('cwd = "' + USERS_PATH.rsplit(SLASH, 1)[0] + '"\n', "home-path")
        self.assert_hit("cwd = '" + HOME_PATH.rsplit(SLASH, 1)[0] + "'\n", "home-path")

    def test_a_home_path_that_ends_the_line_is_found(self):
        self.assert_hit("cd " + HOME_PATH.rsplit(SLASH, 1)[0], "home-path")

    def test_a_home_path_followed_by_a_space_a_bracket_or_a_comma_is_found(self):
        account = HOME_PATH.rsplit(SLASH, 1)[0]
        for tail in (" next", ")", ",", ";", "]"):
            self.assert_hit("see " + account + tail + "\n", "home-path")

    def test_a_windows_home_path_is_found_with_either_slash_and_any_drive_letter(self):
        for text in (WINDOWS_USERS, WINDOWS_USERS + BACKSLASH + "work",
                     WINDOWS_USERS.replace(BACKSLASH, SLASH), "d:" + SLASH + "users" + SLASH + "someone" + SLASH,
                     "E:" + BACKSLASH * 2 + "Users" + BACKSLASH * 2 + "someone"):
            self.assert_hit("path = " + text + "\n", "home-path")

    def test_a_placeholder_or_a_path_that_names_no_account_is_not_found(self):
        for text in (SLASH + "Users" + SLASH, SLASH + "home" + SLASH + "$USER", "~" + SLASH + "work",
                     SLASH + "Users" + SLASH + "<name>", "C:" + BACKSLASH + "Windows" + BACKSLASH + "System32",
                     "abc:" + BACKSLASH + "Users" + BACKSLASH + "someone"):
            self.assert_no_hit("see " + text + "\n")

    def test_a_folder_that_is_not_a_home_path_is_not_found(self):
        self.assert_no_hit("see /usr/local/bin and /var/tmp/x\n")

    def test_email_address_is_found(self):
        self.assert_hit("write to first.last+tag" + "@" + "mail.example.org today\n", "email")

    def test_text_with_an_at_sign_but_no_domain_is_not_an_email(self):
        self.assert_no_hit("see pkg" + "@" + "types/node and fn" + "@" + "decorator here\n")

    def test_private_key_header_with_a_key_type_is_found(self):
        self.assert_hit(PRIVATE_KEY_LINE + "\n", "private-key")

    def test_private_key_header_without_a_key_type_is_found(self):
        self.assert_hit(PLAIN_KEY_LINE + "\n", "private-key")

    def test_pgp_private_key_block_header_is_found(self):
        self.assert_hit(PGP_KEY_LINE + "\n", "private-key")

    def test_public_key_header_is_not_a_private_key(self):
        self.assert_no_hit(PUBLIC_KEY_LINE + "\n")

    def test_sk_token_with_20_characters_is_found(self):
        self.assert_hit("key=" + "sk-" + "a" * 20 + "\n", "token-sk")

    def test_sk_token_may_hold_digits_dashes_and_underscores(self):
        self.assert_hit("sk-" + "aB3-_" * 5 + "\n", "token-sk")

    def test_sk_token_with_19_characters_is_not_found(self):
        self.assert_no_hit("key=" + "sk-" + "a" * 19 + "\n")

    def test_sk_inside_a_longer_word_is_not_a_token(self):
        self.assert_no_hit("a" + "ri" + "sk-" + "adjusted-return-calculation" + "\n")

    def test_classic_token_with_20_characters_is_found(self):
        self.assert_hit("t=" + "ghp_" + "A1" * 10 + "\n", "token-ghp")

    def test_classic_token_with_19_characters_is_not_found(self):
        self.assert_no_hit("t=" + "ghp_" + "a" * 19 + "\n")

    def test_fine_grained_token_with_20_characters_is_found(self):
        self.assert_hit("t=" + "github_pat_" + "a" * 20 + "\n", "token-github-pat")

    def test_fine_grained_token_with_19_characters_is_not_found(self):
        self.assert_no_hit("t=" + "github_pat_" + "a" * 19 + "\n")

    def test_aws_key_id_with_16_characters_is_found(self):
        self.assert_hit("id " + "AKIA" + "A1" * 8 + "\n", "token-aws")

    def test_aws_key_id_with_15_characters_is_not_found(self):
        self.assert_no_hit("id " + "AKIA" + "A" * 15 + "\n")

    def test_aws_key_id_needs_upper_case_characters(self):
        self.assert_no_hit("id " + "AKIA" + "a" * 16 + "\n")

    def test_google_key_with_35_characters_is_found(self):
        self.assert_hit("k=" + "AIza" + "aB-_9" * 7 + "\n", "token-google")

    def test_google_key_with_34_characters_is_not_found(self):
        self.assert_no_hit("k=" + "AIza" + "a" * 34 + "\n")

    def test_slack_token_prefix_is_found_for_each_kind(self):
        for kind in "baprs":
            with self.subTest(kind=kind):
                self.assert_hit("t=" + "xox" + kind + "-" + "123456\n", "token-slack")

    def test_slack_token_prefix_with_another_letter_is_not_found(self):
        self.assert_no_hit("t=" + "xox" + "z" + "-123456\n")

    def test_slack_token_prefix_needs_the_dash(self):
        self.assert_no_hit("t=" + "xox" + "b" + "123456\n")

    def test_one_line_with_two_pattern_kinds_gives_two_hit_lines(self):
        self.put("f.txt", "m=" + "me" + "@" + "mail.example.org k=" + "sk-" + "a" * 24 + "\n")
        self.assertEqual(self.search().stdout, "f.txt:1: email\nf.txt:1: token-sk\n")

    def test_pattern_hits_report_the_line_number(self):
        self.put("f.txt", "clean\nclean\nx " + "ghp_" + "a" * 24 + "\n")
        self.assertEqual(self.search().stdout, "f.txt:3: token-ghp\n")

    # never printing the match

    def test_output_never_contains_the_matched_text(self):
        secret = "sk-" + "Zq9" * 8
        private_name = "zorblax-internal-name"
        self.set_terms(private_name + "\n")
        self.put("f.txt", "k=%s and %s and %s\n" % (secret, private_name, USERS_PATH))
        result = self.search()
        self.assertEqual(result.returncode, 1)
        combined = result.stdout + result.stderr
        self.assertNotIn(secret, combined)
        self.assertNotIn(private_name, combined)
        self.assertNotIn("someone", combined)
        self.assertNotIn("Zq9", combined)

    # the allow list

    def test_allow_skips_term_hits_in_the_named_file(self):
        self.set_terms("example author\n")
        self.put("LICENSE", "Copyright (c) 2026 Example Author\n")
        result = self.search("--allow", "LICENSE")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, "")

    def test_without_allow_the_same_term_hit_is_reported(self):
        self.set_terms("example author\n")
        self.put("LICENSE", "Copyright (c) 2026 Example Author\n")
        self.assertEqual(self.search().stdout, "LICENSE:1: term 1\n")

    def test_allow_still_reports_pattern_hits_in_the_named_file(self):
        self.set_terms("example author\n")
        self.put("LICENSE", "Example Author\nreach me at me" + "@" + "mail.example.org\n")
        result = self.search("--allow", "LICENSE")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "LICENSE:2: email\n")

    def test_allow_does_not_excuse_other_files(self):
        self.set_terms("example author\n")
        self.put("LICENSE", "Example Author\n")
        self.put("README.md", "by Example Author\n")
        result = self.search("--allow", "LICENSE")
        self.assertEqual(result.stdout, "README.md:1: term 1\n")

    def test_allow_takes_several_files(self):
        self.set_terms("example author\n")
        self.put("LICENSE", "Example Author\n")
        self.put("docs/NOTICE", "Example Author\n")
        self.put("other.txt", "Example Author\n")
        result = self.search("--allow", "LICENSE", "docs/NOTICE")
        self.assertEqual(result.stdout, "other.txt:1: term 1\n")

    def test_allow_only_matches_the_named_path_not_the_same_name_elsewhere(self):
        self.set_terms("example author\n")
        self.put("LICENSE", "Example Author\n")
        self.put("vendor/LICENSE", "Example Author\n")
        result = self.search("--allow", "LICENSE")
        self.assertEqual(result.stdout, "vendor/LICENSE:1: term 1\n")

    def test_allow_accepts_an_absolute_path(self):
        self.set_terms("example author\n")
        path = self.put("LICENSE", "Example Author\n")
        result = self.search("--allow", path)
        self.assertEqual(result.returncode, 0, result.stdout)

    # what is skipped

    def test_git_folder_is_skipped(self):
        self.set_terms("bluefinch\n")
        self.put(".git/config", "bluefinch\n")
        self.put("ok.txt", "clean\n")
        self.assertEqual(self.search().returncode, 0)

    def test_node_modules_folder_is_skipped_at_any_depth(self):
        self.set_terms("bluefinch\n")
        self.put("node_modules/pkg/index.js", "bluefinch\n")
        self.put("sub/node_modules/pkg/index.js", "bluefinch\n")
        self.put("ok.txt", "clean\n")
        self.assertEqual(self.search().returncode, 0)

    def test_a_hit_beside_a_skipped_folder_is_still_found(self):
        self.set_terms("bluefinch\n")
        self.put(".git/config", "bluefinch\n")
        self.put("src/a.txt", "bluefinch\n")
        self.assertEqual(self.search().stdout, "src/a.txt:1: term 1\n")

    def test_binary_file_is_skipped(self):
        self.set_terms("bluefinch\n")
        self.put("blob.bin", b"\x00\x01bluefinch\n", mode="wb")
        self.put("ok.txt", "clean\n")
        self.assertEqual(self.search().returncode, 0)

    def test_symbolic_link_is_not_followed(self):
        self.set_terms("bluefinch\n")
        outside = os.path.join(self._tmp.name, "outside.txt")
        with open(outside, "w", encoding="utf-8") as handle:
            handle.write("bluefinch\n")
        os.symlink(outside, os.path.join(self.root, "link.txt"))
        self.assertEqual(self.search().returncode, 0)

    # hidden files, links and the file count

    def test_hidden_files_and_folders_are_read(self):
        self.set_terms("bluefinch\n")
        self.put(".github/ci.yml", "bluefinch\n")
        self.put(".env", "bluefinch\n")
        result = self.search()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines(), [".env:1: term 1", ".github/ci.yml:1: term 1"])

    def test_summary_names_the_hit_count_and_the_file_count(self):
        self.set_terms("bluefinch\n")
        self.put("a.txt", "bluefinch\n")
        self.put("b.txt", "clean\n")
        self.put("blob.bin", b"\x00bluefinch", mode="wb")
        result = self.search()
        self.assertIn("leak_search.py: 1 hits in 2 files", result.stderr)

    def test_empty_folder_exits_2_and_says_so(self):
        result = self.search()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("leak_search.py: no text file found in TARGET_DIR", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_folder_holding_only_binary_files_exits_2(self):
        self.set_terms("bluefinch\n")
        self.put("blob.bin", b"\x00\x01bluefinch\n", mode="wb")
        result = self.search()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("no text file found", result.stderr)

    def test_folder_holding_only_skipped_folders_exits_2(self):
        self.set_terms("bluefinch\n")
        self.put(".git/config", "bluefinch\n")
        self.assertEqual(self.search().returncode, 2)

    def test_a_link_whose_target_path_holds_a_home_path_is_reported(self):
        self.put("ok.txt", "clean\n")
        os.symlink(USERS_PATH + "/x", os.path.join(self.root, "l"))
        result = self.search()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "l:link: home-path\n")

    def test_a_link_to_a_linux_home_path_is_reported(self):
        self.put("ok.txt", "clean\n")
        os.symlink(HOME_PATH + "/x", os.path.join(self.root, "l"))
        self.assertEqual(self.search().stdout, "l:link: home-path\n")

    def test_a_link_whose_target_path_holds_a_term_is_reported_ignoring_case(self):
        self.set_terms("# comment\nacme-secret\n")
        self.put("ok.txt", "clean\n")
        os.symlink("/elsewhere/ACME-Secret.txt", os.path.join(self.root, "sub-link"))
        result = self.search()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "sub-link:link: term 2\n")

    def test_a_link_to_a_folder_is_checked_and_never_entered(self):
        self.set_terms("bluefinch\n")
        self.put("ok.txt", "clean\n")
        outside = os.path.join(self._tmp.name, "outside-folder")
        os.makedirs(outside)
        with open(os.path.join(outside, "x.txt"), "w", encoding="utf-8") as handle:
            handle.write("bluefinch\n")
        os.symlink(outside, os.path.join(self.root, "dir-link"))
        self.assertEqual(self.search().returncode, 0)
        named = os.path.join(self._tmp.name, "bluefinch-dir")
        os.makedirs(named)
        os.symlink(named, os.path.join(self.root, "dir-link-2"))
        self.assertEqual(self.search().stdout, "dir-link-2:link: term 1\n")

    def test_a_link_whose_target_content_holds_a_term_reports_nothing(self):
        self.set_terms("bluefinch\n")
        outside = os.path.join(self._tmp.name, "plain-name.txt")
        with open(outside, "w", encoding="utf-8") as handle:
            handle.write("bluefinch\n")
        os.symlink(outside, os.path.join(self.root, "l"))
        result = self.search()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")

    def test_a_checked_link_counts_toward_the_file_total(self):
        self.put("ok.txt", "clean\n")
        os.symlink("/elsewhere/file.txt", os.path.join(self.root, "l"))
        self.assertIn("0 hits in 2 files", self.search().stderr)

    def test_a_folder_holding_only_a_link_is_not_empty(self):
        os.symlink("/elsewhere/file.txt", os.path.join(self.root, "l"))
        result = self.search()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 hits in 1 files", result.stderr)

    def test_allow_does_not_skip_a_link(self):
        self.set_terms("bluefinch\n")
        self.put("ok.txt", "clean\n")
        os.symlink("/bluefinch/place", os.path.join(self.root, "l"))
        result = self.search("--allow", "l")
        self.assertEqual(result.stdout, "l:link: term 1\n")

    # usage errors, all exit 2

    def assert_usage_error(self, result):
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("usage:", result.stderr)

    def test_no_arguments_exits_2(self):
        self.assert_usage_error(run())

    def test_one_argument_exits_2(self):
        self.assert_usage_error(run(self.terms_path))

    def test_three_positional_arguments_exit_2(self):
        self.assert_usage_error(run(self.terms_path, self.root, "extra"))

    def test_missing_terms_file_exits_2(self):
        self.assert_usage_error(run(os.path.join(self._tmp.name, "nope.txt"), self.root))

    def test_target_that_is_not_a_folder_exits_2(self):
        self.assert_usage_error(run(self.terms_path, os.path.join(self._tmp.name, "absent")))

    def test_allow_with_no_file_exits_2(self):
        self.assert_usage_error(self.search("--allow"))

    def test_unknown_option_exits_2(self):
        self.assert_usage_error(self.search("--verbose"))

    def test_option_after_allow_exits_2(self):
        self.assert_usage_error(self.search("--allow", "LICENSE", "--verbose"))

    # exit codes

    def test_exit_0_when_clean_and_1_when_any_hit(self):
        self.set_terms("bluefinch\n")
        self.put("a.txt", "fine\n")
        self.assertEqual(self.search().returncode, 0)
        self.put("b.txt", "bluefinch\n")
        self.assertEqual(self.search().returncode, 1)

    def test_a_pattern_hit_alone_exits_1(self):
        self.put("a.txt", "k=" + "sk-" + "a" * 24 + "\n")
        self.assertEqual(self.search().returncode, 1)

    # a long line, a file that cannot be read, and names

    # Rule: the email pattern takes linear time. A long run of letters and digits with no
    # at sign must finish well inside the timeout; the old pattern took minutes on it.
    def test_a_long_run_of_name_characters_with_no_at_sign_finishes_quickly(self):
        self.put("f.txt", ("ab12" * 50000) + "\n")
        result = self.search_with_timeout(20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")

    # Rule: the faster email pattern still reports an address that ends a long run.
    def test_an_address_at_the_end_of_a_long_run_is_still_reported_as_an_email(self):
        self.put("f.txt", ("ab12" * 50000) + "@example.com\n")
        result = self.search_with_timeout(20)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, "f.txt:1: email\n")

    # Rule: the home-path pattern takes linear time on a line of a million characters.
    def test_long_lines_that_almost_match_the_home_path_pattern_finish_quickly(self):
        users = SLASH + "Users" + SLASH
        for line in (users + "<" * 1000000, (users + "<<<<<<<<<<<<<<<<<<<< ") * 50000,
                     "C:" + BACKSLASH * 1000000, (users + SLASH) * 200000):
            self.put("f.txt", line + "\n")
            result = self.search_or_fail_on_a_hang()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout, "")

    def search_with_timeout(self, seconds):
        return run(self.terms_path, self.root, timeout=seconds)

    def search_or_fail_on_a_hang(self, seconds=20):
        try:
            return self.search_with_timeout(seconds)
        except subprocess.TimeoutExpired:
            self.fail("leak_search.py did not finish in %d seconds (it opened a named pipe)" % seconds)

    def make_pipe(self, rel):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        os.mkfifo(path)
        return path

    # Rule: a named pipe is never opened. It is skipped with one stderr line, it is not
    # counted as checked or as unreadable, and the exit code is the one the other files give.
    def test_a_named_pipe_is_skipped_and_does_not_change_the_exit_code(self):
        self.put("a.txt", "clean\n")
        self.make_pipe("sub/pipe")
        result = self.search_or_fail_on_a_hang()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(
            result.stderr.splitlines(),
            ["leak_search.py: skipped special file sub/pipe", "leak_search.py: 0 hits in 1 files"])

    # Rule: the name of a named pipe is checked like any name, though its content is not read.
    def test_the_name_of_a_named_pipe_is_still_checked(self):
        self.set_terms("bluefinch\n")
        self.put("a.txt", "clean\n")
        self.make_pipe("bluefinch.fifo")
        result = self.search_or_fail_on_a_hang()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "bluefinch.fifo:name: term 1\n")
        self.assertIn("leak_search.py: skipped special file bluefinch.fifo\n", result.stderr)

    # Rule: a link that points at a pipe is not followed: the link text is checked, the pipe is not opened.
    def test_a_link_that_points_at_a_named_pipe_is_not_opened(self):
        self.put("a.txt", "clean\n")
        self.make_pipe("pipe")
        os.symlink("pipe", os.path.join(self.root, "alias"))
        result = self.search_or_fail_on_a_hang()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            result.stderr.splitlines(),
            ["leak_search.py: skipped special file pipe", "leak_search.py: 0 hits in 2 files"])

    def lock(self, rel, mode=0o000):
        path = os.path.join(self.root, rel)
        restored = 0o755 if os.path.isdir(path) else 0o644
        os.chmod(path, mode)
        self.addCleanup(os.chmod, path, restored)
        return path

    def skip_if_readable_anyway(self, path):
        if os.path.isdir(path):
            readable = os.access(path, os.R_OK | os.X_OK)
        else:
            readable = os.access(path, os.R_OK)
        if readable:
            self.skipTest("this process can read a mode 000 entry (root)")

    # Rule: a file that cannot be read is named on stderr, counted, and makes the run exit 2,
    # even when no hit was found; hits found elsewhere are still printed.
    def test_a_file_that_cannot_be_read_is_named_and_the_run_exits_2(self):
        self.put("ok.txt", "clean\n")
        self.put("sub/locked.txt", "clean\n")
        self.skip_if_readable_anyway(self.lock("sub/locked.txt"))
        result = self.search()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(
            result.stderr.splitlines(),
            ["leak_search.py: could not read sub/locked.txt",
             "leak_search.py: 0 hits in 1 files, could not read 1"])

    # Rule: an unreadable file does not hide the hits found in the files that can be read.
    def test_hits_in_readable_files_are_printed_beside_an_unreadable_one(self):
        self.set_terms("bluefinch\n")
        self.put("a.txt", "bluefinch\n")
        self.put("b.txt", "clean\n")
        self.skip_if_readable_anyway(self.lock("b.txt"))
        result = self.search()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "a.txt:1: term 1\n")
        self.assertEqual(
            result.stderr.splitlines()[-1], "leak_search.py: 1 hits in 1 files, could not read 1")

    # Rule: a folder whose entries cannot be listed is reported the same way, and a run that
    # reads nothing else still says what it could not read instead of "no text file found".
    def test_a_folder_that_cannot_be_listed_is_named_and_the_run_exits_2(self):
        self.put("locked/inner.txt", "clean\n")
        self.skip_if_readable_anyway(self.lock("locked"))
        result = self.search()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(
            result.stderr.splitlines(),
            ["leak_search.py: could not read locked",
             "leak_search.py: 0 hits in 0 files, could not read 1"])

    # Rule: a binary file is skipped silently and is not counted as unreadable.
    def test_a_binary_file_is_not_counted_as_unreadable(self):
        self.put("blob.bin", b"\x00\x01", mode="wb")
        self.put("ok.txt", "clean\n")
        result = self.search()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("could not read", result.stderr)

    # Rule: a link whose text cannot be read is reported like a file that cannot be read.
    # A real link always reads, so this one runs main() in this process with readlink failing.
    def test_a_link_whose_text_cannot_be_read_is_named_and_the_run_exits_2(self):
        self.put("ok.txt", "clean\n")
        os.symlink("elsewhere", os.path.join(self.root, "l"))
        spec = importlib.util.spec_from_file_location("leak_search_under_test", LEAK)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        out, err = io.StringIO(), io.StringIO()
        real_readlink = os.readlink

        def readlink(path, *args, **kwargs):
            if os.path.basename(path) == "l":
                raise OSError("denied")
            return real_readlink(path, *args, **kwargs)

        with mock.patch.object(module.os, "readlink", side_effect=readlink), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = module.main(["leak_search.py", self.terms_path, self.root])
        self.assertEqual(code, 2, out.getvalue() + err.getvalue())
        self.assertEqual(
            err.getvalue().splitlines(),
            ["leak_search.py: could not read l",
             "leak_search.py: 0 hits in 1 files, could not read 1"])

    def load_leak_module(self):
        spec = importlib.util.spec_from_file_location("leak_search_under_test", LEAK)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # Rule: a folder that cannot be listed is reported at its place in the walk, before the
    # entries that come after it, and not held back to the end. os.walk reports the failure
    # after the folder before it was yielded and before the next one, so this test gives
    # walk_entries a walk that does that, in this process, and needs no locked folder
    # (a locked folder cannot be made under root).
    def test_an_unreadable_folder_is_reported_before_the_folders_after_it(self):
        module = self.load_leak_module()

        def fake_walk(top, onerror=None):
            yield top, ["a", "b"], []
            onerror(OSError(13, "denied", os.path.join(top, "a")))
            yield os.path.join(top, "b"), [], ["x.txt"]

        with mock.patch.object(module.os, "walk", fake_walk):
            entries = list(module.walk_entries(self.root))
        self.assertEqual(
            entries,
            [(os.path.join(self.root, "a"), module.KIND_UNREADABLE),
             (os.path.join(self.root, "b"), module.KIND_DIR),
             (os.path.join(self.root, "b", "x.txt"), module.KIND_FILE)])

    # Rule: the name of the target folder itself is never checked. The one entry that is the
    # target folder is a target that cannot be listed; it is named ".", with no name hit.
    def test_the_name_of_the_target_folder_itself_is_not_checked(self):
        module = self.load_leak_module()
        self.set_terms("bluefinch\n")
        named = os.path.join(self._tmp.name, "bluefinch-target")
        os.makedirs(named)

        def fake_walk(top, onerror=None):
            onerror(OSError(13, "denied", top))
            return
            yield

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(module.os, "walk", fake_walk), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = module.main(["leak_search.py", self.terms_path, named])
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(code, 2, err.getvalue())
        self.assertEqual(
            err.getvalue().splitlines(),
            ["leak_search.py: could not read .",
             "leak_search.py: 0 hits in 0 files, could not read 1"])

    # Rule: a name that is not valid text is printed escaped on stdout and stderr and never raises.
    # The name is made with a lone surrogate (what Linux gives for a byte that is not text), in a
    # patched walk, so the test needs no such file on disk; both streams only take ASCII.
    def test_a_name_with_undecodable_bytes_is_printed_escaped_on_both_streams(self):
        module = self.load_leak_module()
        self.set_terms("bad\n")
        bad = os.path.join(self.root, "bad" + chr(0xDCFF))

        def fake_walk_entries(root):
            yield bad, module.KIND_FILE

        raw_out, raw_err = io.BytesIO(), io.BytesIO()
        out = io.TextIOWrapper(raw_out, encoding="ascii", newline="\n")
        err = io.TextIOWrapper(raw_err, encoding="ascii", newline="\n")
        with mock.patch.object(module, "walk_entries", fake_walk_entries), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = module.main(["leak_search.py", self.terms_path, self.root])
            except UnicodeEncodeError as exc:
                self.fail("printing the name raised: %s" % exc)
            out.flush()
            err.flush()
        escaped = "bad" + BACKSLASH + "udcff"
        self.assertEqual(raw_out.getvalue().decode("ascii"), escaped + ":name: term 1\n")
        self.assertEqual(
            raw_err.getvalue().decode("ascii").splitlines(),
            ["leak_search.py: could not read " + escaped,
             "leak_search.py: 1 hits in 0 files, could not read 1"])
        self.assertEqual(code, 2)

    # Rule: the name of a file is checked against the terms and printed as path:name: kind.
    def test_a_file_name_that_holds_a_term_is_reported(self):
        self.set_terms("bluefinch\n")
        self.put("sub/BlueFinch-notes.txt", "clean\n")
        result = self.search()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "sub/BlueFinch-notes.txt:name: term 1\n")
        self.assertIn("leak_search.py: 1 hits in 1 files", result.stderr)

    # Rule: a folder name is checked, and its hit comes before the hits inside it.
    def test_a_folder_name_hit_comes_before_the_hits_inside_it(self):
        self.set_terms("bluefinch\n")
        self.put("bluefinch/a.txt", "bluefinch\n")
        self.put("zeta.txt", "clean\n")
        result = self.search()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout.splitlines(), ["bluefinch:name: term 1", "bluefinch/a.txt:1: term 1"])

    # Rule: an entry's name hit comes before its content hits.
    def test_a_name_hit_comes_before_the_content_hits_of_the_same_file(self):
        self.set_terms("bluefinch\n")
        self.put("bluefinch.txt", "bluefinch\n")
        result = self.search()
        self.assertEqual(
            result.stdout.splitlines(), ["bluefinch.txt:name: term 1", "bluefinch.txt:1: term 1"])

    # Rule: --allow never skips a name.
    def test_allow_does_not_skip_a_name_hit(self):
        self.set_terms("bluefinch\n")
        self.put("bluefinch.txt", "bluefinch\n")
        result = self.search("--allow", "bluefinch.txt")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "bluefinch.txt:name: term 1\n")

    # Rule: the names of binary files are checked, and a folder with only binary files
    # still ends "no text file found" after the name hit is printed.
    def test_the_name_of_a_binary_file_is_checked(self):
        self.set_terms("bluefinch\n")
        self.put("bluefinch.bin", b"\x00\x01", mode="wb")
        result = self.search()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "bluefinch.bin:name: term 1\n")
        self.assertIn("no text file found in TARGET_DIR", result.stderr)

    # Rule: the name of a symbolic link is checked as well as the text it holds.
    def test_the_name_of_a_symbolic_link_is_checked(self):
        self.set_terms("bluefinch\n")
        self.put("ok.txt", "clean\n")
        os.symlink("elsewhere", os.path.join(self.root, "bluefinch-link"))
        result = self.search()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "bluefinch-link:name: term 1\n")

    # Rule: the built-in patterns apply to names too, and the name hit names the kind.
    def test_a_name_in_the_shape_of_an_email_address_is_reported(self):
        name = "someone" + "@" + "example.com.txt"
        self.put(name, "clean\n")
        result = self.search()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, name + ":name: email\n")

    # Rule: .git and node_modules folders are neither entered nor name-checked, and the
    # name of TARGET_DIR itself is not checked.
    def test_skipped_folders_and_the_target_folder_are_not_name_checked(self):
        self.set_terms(".git\nnode_modules\ntarget\n")
        self.put(".git/config", "clean\n")
        self.put("sub/node_modules/x.js", "clean\n")
        self.put("ok.txt", "clean\n")
        result = self.search()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")

    # the shipped example

    def test_example_terms_find_the_planted_terms_in_the_sample(self):
        result = run(EXAMPLE_TERMS, SAMPLE)
        self.assertEqual(result.returncode, 1)
        hits = result.stdout.splitlines()
        self.assertIn("LICENSE:3: term 5", hits)
        self.assertIn("README.md:5: term 3", hits)
        self.assertIn("README.md:5: term 4", hits)
        self.assertIn("wordstat.py:4: term 3", hits)
        self.assertIn("wordstat.py:12: term 4", hits)
        self.assertEqual(len(hits), 6)

    def test_example_terms_with_allow_license_leave_only_the_scrubbable_hits(self):
        result = run(EXAMPLE_TERMS, SAMPLE, "--allow", "LICENSE")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("LICENSE", result.stdout)


if __name__ == "__main__":
    unittest.main()
