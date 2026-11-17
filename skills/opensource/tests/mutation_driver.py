#!/usr/bin/env python3
"""Prove the tests can fail: break each check in a copy of a script and run its named test.

Usage:
    python3 tests/mutation_driver.py

For each mutation the driver copies scripts/ to a temporary folder, replaces one
piece of code there (the original files are never touched), and runs the one
test that is meant to catch that break. A mutation is "killed" when the test
fails and "survived" when the test still passes, which would mean the test does
not really check what its name says. The driver first runs every named test
against the unbroken copy and refuses to continue if one does not pass.

A test that skips itself (the mode 000 tests do when the process is root and can
read anything) is not a pass. The driver prints "not run here: TEST_ID (skipped)"
for it, leaves its mutations out of both killed and survived, and counts them as
"not run". A run that times out is printed as "timed out: NAME" and is never
counted as killed.

The last line reads "mutations: N, killed: K, survived: S, not run: R".

Exit codes: 0 no mutation survived and none timed out, 1 at least one survived,
timed out, or a setup problem.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCRIPTS = os.path.join(SKILL, "scripts")

SC = "test_scrub.ScrubTests."
LK = "test_leak_search.LeakSearchTests."

# (name, script, old text, new text, test that must fail). The old text must
# appear exactly once in the script.
MUTATIONS = []


def add(name, script, old, new, test):
    MUTATIONS.append((name, script, old, new, test))


# scrub.py: missing targets
add("scrub: a glob that matches no file is accepted", "scrub.py",
    "ok = bool(files)", "ok = True", SC + "test_glob_matching_no_file_exits_1")
add("scrub: a find text that is absent is accepted", "scrub.py",
    "if count_here == 0:", "if False:", SC + "test_find_text_absent_exits_1_and_names_the_rule")
add("scrub: only the first matched file is checked for the find text", "scrub.py",
    "if count_here == 0:", "if count_here == 0 and total == 0:",
    SC + "test_find_absent_from_one_of_several_matched_files_exits_1")
add("scrub: count too low is accepted", "scrub.py",
    'total != rule["count"]', 'total < rule["count"]', SC + "test_count_too_low_exits_1_and_writes_nothing")
add("scrub: count too high is accepted", "scrub.py",
    'total != rule["count"]', 'total > rule["count"]', SC + "test_count_too_high_exits_1")
add("scrub: count is checked per file instead of in total", "scrub.py",
    'total != rule["count"]', 'count_here != rule["count"]', SC + "test_count_is_the_total_across_all_matched_files")
add("scrub: files are written before the run fails on a missing rule", "scrub.py",
    "            return EXIT_MISSING",
    "            write_changes(root, texts, original)\n            return EXIT_MISSING",
    SC + "test_a_missing_rule_writes_nothing_even_when_earlier_rules_were_fine")
add("scrub: only the first missing rule is reported", "scrub.py",
    'missing.append((number, rule["find"]))',
    'missing.append((number, rule["find"]))\n            break',
    SC + "test_every_missing_rule_is_reported")
add("scrub: the missing line drops its rule number format", "scrub.py",
    '"MISSING rule %d: %s"', '"MISSING rule %d %s"', SC + "test_find_text_absent_exits_1_and_names_the_rule")
add("scrub: a dry run still fails on a missing target only without --dry-run", "scrub.py",
    "        if missing:", "        if missing and not dry_run:", SC + "test_dry_run_still_fails_on_a_missing_target")
add("scrub: a folder that matches the glob is not skipped", "scrub.py",
    "if os.path.islink(path) or not os.path.isfile(path):", "if os.path.islink(path):",
    SC + "test_folders_matched_by_a_glob_are_skipped")
add("scrub: a symbolic link is followed", "scrub.py",
    "if os.path.islink(path) or not os.path.isfile(path):", "if not os.path.isfile(path):",
    SC + "test_a_symbolic_link_to_a_file_inside_the_target_is_not_followed")
add("scrub: files inside .git can be matched", "scrub.py",
    'if ".git" in rel.split(os.sep):', "if False:", SC + "test_files_inside_the_git_folder_are_never_matched")
add("scrub: a file reached through a symlinked folder outside the target is matched", "scrub.py",
    "if not (os.path.realpath(path) + os.sep).startswith(real_root + os.sep):", "if False:",
    SC + "test_a_symlinked_folder_leading_outside_the_target_is_never_written")
add("scrub: the containment check compares a bare prefix of the target path", "scrub.py",
    "startswith(real_root + os.sep)", "startswith(real_root)",
    SC + "test_a_symlinked_folder_to_a_sibling_sharing_the_target_name_prefix_is_never_written")
add("scrub: every file behind a symlinked folder is dropped, even inside the target", "scrub.py",
    "if not (os.path.realpath(path) + os.sep).startswith(real_root + os.sep):",
    "if os.path.realpath(path) != os.path.join(real_root, os.path.relpath(path, root)):",
    SC + "test_a_symlinked_folder_inside_the_target_is_still_matched")
add("scrub: a glob star matches hidden folders", "scrub.py",
    "    found = glob.glob(os.path.join(glob.escape(root), pattern), recursive=True)\n    real_root",
    "    found = glob.glob(os.path.join(glob.escape(root), pattern), recursive=True)\n"
    "    found += glob.glob(os.path.join(glob.escape(root), \"**\", \".*\", \"**\", pattern.split(\"/\")[-1]), recursive=True)\n"
    "    real_root",
    SC + "test_star_globs_do_not_match_hidden_folders")
add("scrub: a glob that names a hidden folder cannot match it", "scrub.py",
    'if ".git" in rel.split(os.sep):', 'if any(part.startswith(".") for part in rel.split(os.sep)):',
    SC + "test_a_glob_that_names_the_hidden_folder_matches_it")

# scrub.py: replacing and reporting
add("scrub: the replacement is never applied", "scrub.py",
    '.replace(rule["find"], rule["replace"])', '.replace(rule["find"], rule["find"])',
    SC + "test_replaces_literal_text_and_reports_the_rule")
add("scrub: only the first occurrence is replaced", "scrub.py",
    '.replace(rule["find"], rule["replace"])', '.replace(rule["find"], rule["replace"], 1)',
    SC + "test_replaces_literal_text_and_reports_the_rule")
add("scrub: the report always says one file", "scrub.py",
    "report.append((number, total, len(files)))", "report.append((number, total, 1))",
    SC + "test_report_counts_files_and_occurrences_across_a_glob")
add("scrub: the report counts files where it should count occurrences", "scrub.py",
    "report.append((number, total, len(files)))", "report.append((number, len(files), len(files)))",
    SC + "test_report_counts_files_and_occurrences_across_a_glob")
add("scrub: the report line wording changes", "scrub.py",
    '"rule %d: replaced %d in %d files"', '"rule %d: changed %d in %d files"',
    SC + "test_one_report_line_per_rule_in_order")
add("scrub: later rules do not see earlier replacements", "scrub.py",
    "for rel in files:\n            texts[rel] = texts[rel].replace",
    "for rel in files:\n            texts[rel] = original[rel].replace",
    SC + "test_later_rule_sees_the_result_of_an_earlier_rule")
add("scrub: line endings are rewritten on read", "scrub.py",
    'with open(path, "r", encoding="utf-8", newline="") as handle:',
    'with open(path, "r", encoding="utf-8") as handle:', SC + "test_line_endings_are_preserved")
add("scrub: the file mode is lost", "scrub.py",
    "            shutil.copymode(path, handle.name)", "            pass", SC + "test_file_mode_is_preserved")
add("scrub: temporary files are left behind", "scrub.py",
    "        os.replace(temp, path)", "        shutil.copyfile(temp, path)",
    SC + "test_no_temporary_files_are_left_behind")
add("scrub: an unchanged file is rewritten", "scrub.py",
    "if texts[rel] == original[rel]:", "if False:", SC + "test_a_file_whose_text_does_not_change_is_not_rewritten")

# scrub.py: dry run
add("scrub: --dry-run is ignored", "scrub.py",
    "            dry_run = True", "            dry_run = False", SC + "test_dry_run_writes_nothing")
add("scrub: a dry run writes anyway", "scrub.py",
    "        if not dry_run:", "        if True:", SC + "test_dry_run_writes_nothing")

# scrub.py: exit codes and usage
add("scrub: a missing target exits 0", "scrub.py",
    "EXIT_MISSING = 1", "EXIT_MISSING = 0", SC + "test_find_text_absent_exits_1_and_names_the_rule")
add("scrub: a usage error exits 1", "scrub.py",
    "EXIT_USAGE = 2", "EXIT_USAGE = 1", SC + "test_no_arguments_exits_2")
add("scrub: success exits 3", "scrub.py",
    "EXIT_OK = 0", "EXIT_OK = 3", SC + "test_replaces_literal_text_and_reports_the_rule")
add("scrub: an unknown flag is ignored", "scrub.py",
    '            raise UsageError("unknown option %s" % arg)', "            pass", SC + "test_unknown_flag_exits_2")
add("scrub: extra positional arguments are ignored", "scrub.py",
    "if len(positional) != 2:", "if len(positional) < 2:", SC + "test_three_positional_arguments_exit_2")
add("scrub: a missing second argument is ignored", "scrub.py",
    "if len(positional) != 2:", "if len(positional) > 2:", SC + "test_one_argument_exits_2")
add("scrub: an unreadable rules file is not a usage error", "scrub.py",
    "except (OSError, ValueError) as exc:\n        raise UsageError(\"cannot read rules file",
    "except OSError as exc:\n        raise UsageError(\"cannot read rules file",
    SC + "test_rules_file_that_is_not_json_exits_2")
add("scrub: a rules file that is not a list is accepted", "scrub.py",
    "if not isinstance(data, list):", "if False:", SC + "test_rules_file_that_is_an_empty_object_exits_2")
add("scrub: a rule with unknown keys is accepted", "scrub.py",
    "    if unknown:", "    if False:", SC + "test_rule_with_an_unknown_key_exits_2")
add("scrub: a missing required key is not caught", "scrub.py",
    "        if not isinstance(rule.get(key), str):", "        if False:",
    SC + "test_rule_missing_a_required_key_exits_2")
add("scrub: a non-string value is accepted", "scrub.py",
    "        if not isinstance(rule.get(key), str):", "        if key not in rule:",
    SC + "test_rule_with_a_non_string_value_exits_2")
add("scrub: an empty find is accepted", "scrub.py",
    '    if not rule["find"]:', "    if False:", SC + "test_rule_with_an_empty_find_exits_2")
add("scrub: a boolean count is accepted", "scrub.py",
    "if isinstance(count, bool) or not isinstance(count, int) or count < 1:",
    "if not isinstance(count, int) or count < 1:", SC + "test_rule_with_a_bad_count_exits_2")
add("scrub: a zero count is accepted", "scrub.py",
    "or count < 1:", "or count < 0:", SC + "test_rule_with_a_bad_count_exits_2")
add("scrub: a non-integer count is accepted", "scrub.py",
    "or not isinstance(count, int) or count < 1:", "or count < 1:", SC + "test_rule_with_a_bad_count_exits_2")
add("scrub: a glob may climb out of the target", "scrub.py",
    'if os.path.isabs(rule["file"]) or ".." in segments:', 'if os.path.isabs(rule["file"]):',
    SC + "test_glob_that_climbs_out_of_the_target_exits_2")
add("scrub: an absolute glob is accepted", "scrub.py",
    'if os.path.isabs(rule["file"]) or ".." in segments:', 'if ".." in segments:',
    SC + "test_absolute_glob_exits_2")
add("scrub: a target that is not a folder is accepted", "scrub.py",
    "if not os.path.isdir(root):", "if False:", SC + "test_target_that_is_not_a_folder_exits_2")
add("scrub: a file that is not UTF-8 is not a usage error", "scrub.py",
    "except (OSError, UnicodeDecodeError) as exc:", "except OSError as exc:",
    SC + "test_matched_file_that_is_not_utf8_exits_2")

# leak_search.py: terms
add("leak: term matching is case sensitive for the file", "leak_search.py",
    "lowered = line.lower()", "lowered = line", LK + "test_term_match_ignores_case_in_the_file")
add("leak: term matching is case sensitive for the term", "leak_search.py",
    "terms.append((term_number, text.lower()))", "terms.append((term_number, text))",
    LK + "test_term_match_ignores_case_in_the_terms_file")
add("leak: term hits are never reported", "leak_search.py",
    "if term in lowered:", "if False:", LK + "test_a_term_hit_prints_path_line_and_term_number")
add("leak: terms are matched as patterns", "leak_search.py",
    "if term in lowered:", "if re.search(term, lowered):", LK + "test_term_is_matched_as_plain_text_not_a_pattern")
add("leak: comment lines are read as terms", "leak_search.py",
    'if text.startswith("#"):', "if False:", LK + "test_comment_lines_in_the_terms_file_are_not_terms")
add("leak: blank lines are read as terms", "leak_search.py",
    "if not text:", "if False:", LK + "test_blank_lines_in_the_terms_file_are_not_terms")
add("leak: term whitespace is kept", "leak_search.py",
    "text = raw.strip()", "text = raw", LK + "test_term_whitespace_is_trimmed")
add("leak: term numbers start at zero", "leak_search.py",
    "enumerate(raw_lines, start=1)", "enumerate(raw_lines, start=0)", LK + "test_a_term_hit_prints_path_line_and_term_number")
add("leak: line numbers start at zero", "leak_search.py",
    "enumerate(lines, start=1)", "enumerate(lines, start=0)", LK + "test_pattern_hits_report_the_line_number")
add("leak: a byte order mark stays in the first term", "leak_search.py",
    'encoding="utf-8-sig"', 'encoding="utf-8"', LK + "test_utf8_byte_order_mark_in_the_terms_file_is_ignored")
add("leak: a file that is not UTF-8 stops the run", "leak_search.py",
    'data.decode("utf-8", errors="replace")', 'data.decode("utf-8", errors="strict")', LK + "test_a_file_that_is_not_utf8_is_still_searched")

# leak_search.py: built-in patterns
HOME = 'r"/(?:Users|home)/(?:[^/\\s]+/|[A-Za-z0-9._-]+)"'
add("leak: the Users folder is not a home path", "leak_search.py",
    HOME, 'r"/(?:home)/(?:[^/\\s]+/|[A-Za-z0-9._-]+)"', LK + "test_home_path_under_users_is_found")
add("leak: the home folder is not a home path", "leak_search.py",
    HOME, 'r"/(?:Users)/(?:[^/\\s]+/|[A-Za-z0-9._-]+)"', LK + "test_home_path_under_home_is_found")
add("leak: any usr folder counts as a home path", "leak_search.py",
    HOME, 'r"/(?:Users|home|usr)/(?:[^/\\s]+/|[A-Za-z0-9._-]+)"', LK + "test_a_folder_that_is_not_a_home_path_is_not_found")
add("leak: the home-path pattern is off", "leak_search.py",
    HOME, 'r"(?!)"', LK + "test_home_path_under_users_is_found")
EMAIL = 'r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\\.[A-Za-z0-9-]+)+"'
add("leak: the email pattern is off", "leak_search.py",
    EMAIL, 'r"(?!)"', LK + "test_email_address_is_found")
add("leak: an email needs no domain dot", "leak_search.py",
    EMAIL, 'r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\\.[A-Za-z0-9-]+)*"',
    LK + "test_text_with_an_at_sign_but_no_domain_is_not_an_email")
KEY = 'r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----"'
add("leak: the private-key pattern is off", "leak_search.py",
    KEY, 'r"(?!)"', LK + "test_private_key_header_with_a_key_type_is_found")
add("leak: a private key header must name a key type", "leak_search.py",
    KEY, 'r"-----BEGIN (?:[A-Z0-9]+ )PRIVATE KEY(?: BLOCK)?-----"',
    LK + "test_private_key_header_without_a_key_type_is_found")
add("leak: a PGP block header is not found", "leak_search.py",
    KEY, 'r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"', LK + "test_pgp_private_key_block_header_is_found")
add("leak: a public key header counts as private", "leak_search.py",
    KEY, 'r"-----BEGIN (?:[A-Z0-9]+ )*(?:PRIVATE|PUBLIC) KEY(?: BLOCK)?-----"',
    LK + "test_public_key_header_is_not_a_private_key")

SK = 'r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}"'
add("leak: the sk token pattern is off", "leak_search.py", SK, 'r"(?!)"', LK + "test_sk_token_with_20_characters_is_found")
add("leak: an sk token needs 21 characters", "leak_search.py",
    SK, 'r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{21,}"', LK + "test_sk_token_with_20_characters_is_found")
add("leak: an sk token needs only 19 characters", "leak_search.py",
    SK, 'r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{19,}"', LK + "test_sk_token_with_19_characters_is_not_found")
add("leak: an sk token cannot hold dashes or underscores", "leak_search.py",
    SK, 'r"(?<![A-Za-z0-9])sk-[A-Za-z0-9]{20,}"', LK + "test_sk_token_may_hold_digits_dashes_and_underscores")
add("leak: an sk token may start inside a word", "leak_search.py",
    SK, 'r"sk-[A-Za-z0-9_-]{20,}"', LK + "test_sk_inside_a_longer_word_is_not_a_token")

GHP = 'r"(?<![A-Za-z0-9])ghp_[A-Za-z0-9_]{20,}"'
add("leak: the ghp token pattern is off", "leak_search.py", GHP, 'r"(?!)"', LK + "test_classic_token_with_20_characters_is_found")
add("leak: a ghp token needs 21 characters", "leak_search.py",
    GHP, 'r"(?<![A-Za-z0-9])ghp_[A-Za-z0-9_]{21,}"', LK + "test_classic_token_with_20_characters_is_found")
add("leak: a ghp token needs only 19 characters", "leak_search.py",
    GHP, 'r"(?<![A-Za-z0-9])ghp_[A-Za-z0-9_]{19,}"', LK + "test_classic_token_with_19_characters_is_not_found")

PAT = 'r"(?<![A-Za-z0-9])github_pat_[A-Za-z0-9_]{20,}"'
add("leak: the github_pat token pattern is off", "leak_search.py",
    PAT, 'r"(?!)"', LK + "test_fine_grained_token_with_20_characters_is_found")
add("leak: a github_pat token needs 21 characters", "leak_search.py",
    PAT, 'r"(?<![A-Za-z0-9])github_pat_[A-Za-z0-9_]{21,}"', LK + "test_fine_grained_token_with_20_characters_is_found")
add("leak: a github_pat token needs only 19 characters", "leak_search.py",
    PAT, 'r"(?<![A-Za-z0-9])github_pat_[A-Za-z0-9_]{19,}"', LK + "test_fine_grained_token_with_19_characters_is_not_found")

AWS = 'r"(?<![A-Za-z0-9])AKIA[A-Z0-9]{16}"'
add("leak: the AWS key pattern is off", "leak_search.py", AWS, 'r"(?!)"', LK + "test_aws_key_id_with_16_characters_is_found")
add("leak: an AWS key needs 17 characters", "leak_search.py",
    AWS, 'r"(?<![A-Za-z0-9])AKIA[A-Z0-9]{17}"', LK + "test_aws_key_id_with_16_characters_is_found")
add("leak: an AWS key needs only 15 characters", "leak_search.py",
    AWS, 'r"(?<![A-Za-z0-9])AKIA[A-Z0-9]{15}"', LK + "test_aws_key_id_with_15_characters_is_not_found")
add("leak: an AWS key may be lower case", "leak_search.py",
    AWS, 'r"(?<![A-Za-z0-9])AKIA[A-Za-z0-9]{16}"', LK + "test_aws_key_id_needs_upper_case_characters")

GOO = 'r"(?<![A-Za-z0-9])AIza[A-Za-z0-9_-]{35}"'
add("leak: the Google key pattern is off", "leak_search.py", GOO, 'r"(?!)"', LK + "test_google_key_with_35_characters_is_found")
add("leak: a Google key needs 36 characters", "leak_search.py",
    GOO, 'r"(?<![A-Za-z0-9])AIza[A-Za-z0-9_-]{36}"', LK + "test_google_key_with_35_characters_is_found")
add("leak: a Google key needs only 34 characters", "leak_search.py",
    GOO, 'r"(?<![A-Za-z0-9])AIza[A-Za-z0-9_-]{34}"', LK + "test_google_key_with_34_characters_is_not_found")

SLACK = 'r"(?<![A-Za-z0-9])xox[baprs]-"'
add("leak: the Slack token pattern is off", "leak_search.py", SLACK, 'r"(?!)"', LK + "test_slack_token_prefix_is_found_for_each_kind")
for letter in "baprs":
    add("leak: a Slack token of kind %s is not found" % letter, "leak_search.py",
        SLACK, 'r"(?<![A-Za-z0-9])xox[%s]-"' % "baprs".replace(letter, ""),
        LK + "test_slack_token_prefix_is_found_for_each_kind")
add("leak: any letter counts as a Slack token kind", "leak_search.py",
    SLACK, 'r"(?<![A-Za-z0-9])xox[a-z]-"', LK + "test_slack_token_prefix_with_another_letter_is_not_found")
add("leak: a Slack token needs no dash", "leak_search.py",
    SLACK, 'r"(?<![A-Za-z0-9])xox[baprs]"', LK + "test_slack_token_prefix_needs_the_dash")

# leak_search.py: output
add("leak: a term hit prints the term", "leak_search.py",
    'hits.append((line_number, "term %d" % term_number))',
    'hits.append((line_number, "term %d %s" % (term_number, term)))',
    LK + "test_output_never_contains_the_matched_text")
add("leak: a pattern hit prints the line", "leak_search.py",
    "hits.append((line_number, name))", "hits.append((line_number, name + \" \" + line))",
    LK + "test_output_never_contains_the_matched_text")
add("leak: only the first pattern hit on a line is reported", "leak_search.py",
    "hits.append((line_number, name))", "hits.append((line_number, name))\n                break",
    LK + "test_one_line_with_two_pattern_kinds_gives_two_hit_lines")

# leak_search.py: the allow list
add("leak: allow does nothing", "leak_search.py",
    "if not is_allowed:", "if True:", LK + "test_allow_skips_term_hits_in_the_named_file")
add("leak: allow hides pattern hits too", "leak_search.py",
    "for name, regex in PATTERNS:", "for name, regex in ([] if is_allowed else PATTERNS):",
    LK + "test_allow_still_reports_pattern_hits_in_the_named_file")
add("leak: allow ignores the path it is given", "leak_search.py",
    "paths.add(os.path.realpath(os.path.join(root, item)))", "pass",
    LK + "test_allow_skips_term_hits_in_the_named_file")
add("leak: allow matches any file with the same name", "leak_search.py",
    "os.path.realpath(path) in allowed",
    "os.path.basename(path) in set(os.path.basename(a) for a in allowed)",
    LK + "test_allow_only_matches_the_named_path_not_the_same_name_elsewhere")

# leak_search.py: what is skipped
add("leak: the .git folder is searched", "leak_search.py",
    'SKIP_DIRS = {".git", "node_modules"}', 'SKIP_DIRS = {"node_modules"}', LK + "test_git_folder_is_skipped")
add("leak: the node_modules folder is searched", "leak_search.py",
    'SKIP_DIRS = {".git", "node_modules"}', 'SKIP_DIRS = {".git"}', LK + "test_node_modules_folder_is_skipped_at_any_depth")
add("leak: binary files are searched", "leak_search.py",
    'if b"\\0" in data[:BINARY_SNIFF_BYTES]:', "if False:", LK + "test_binary_file_is_skipped")
add("leak: symbolic links are followed", "leak_search.py",
    "            yield path, KIND_LINK if os.path.islink(path) else KIND_FILE", "            yield path, KIND_FILE",
    LK + "test_symbolic_link_is_not_followed")

# leak_search.py: exit codes and usage
add("leak: hits exit 0", "leak_search.py",
    "return EXIT_HITS if total else EXIT_CLEAN", "return EXIT_CLEAN", LK + "test_exit_0_when_clean_and_1_when_any_hit")
add("leak: a clean run exits 1", "leak_search.py",
    "return EXIT_HITS if total else EXIT_CLEAN", "return EXIT_HITS", LK + "test_exit_0_when_clean_and_1_when_any_hit")
add("leak: an empty folder is a clean result", "leak_search.py",
    "    if checked == 0:", "    if False:", LK + "test_empty_folder_exits_2_and_says_so")
add("leak: the empty folder message is dropped", "leak_search.py",
    "no text file found in TARGET_DIR", "nothing here", LK + "test_empty_folder_exits_2_and_says_so")
add("leak: an empty folder exits 1", "leak_search.py",
    'no text file found in TARGET_DIR\\n")\n        return EXIT_USAGE',
    'no text file found in TARGET_DIR\\n")\n        return EXIT_HITS',
    LK + "test_empty_folder_exits_2_and_says_so")
add("leak: a binary file counts as a checked file", "leak_search.py",
    "    if lines is None:\n        return None\n    return scan_lines(lines, terms, is_allowed)",
    "    if lines is None:\n        return []\n    return scan_lines(lines, terms, is_allowed)",
    LK + "test_folder_holding_only_binary_files_exits_2")
add("leak: the summary repeats the hit count as the file count", "leak_search.py",
    "% (total, checked))", "% (total, total))", LK + "test_summary_names_the_hit_count_and_the_file_count")
add("leak: symbolic links are skipped", "leak_search.py",
    "            yield path, KIND_LINK if os.path.islink(path) else KIND_FILE",
    "            if os.path.islink(path):\n                continue\n            yield path, KIND_FILE",
    LK + "test_a_link_whose_target_path_holds_a_home_path_is_reported")
add("leak: a link is read as the file it points to", "leak_search.py",
    "hits = scan_link(path, terms)", "hits = scan_file(path, terms, False)",
    LK + "test_a_link_whose_target_content_holds_a_term_reports_nothing")
add("leak: link text is not checked against the terms", "leak_search.py",
    "scan_lines([target], terms, False)", "scan_lines([target], [], False)",
    LK + "test_a_link_whose_target_path_holds_a_term_is_reported_ignoring_case")
add("leak: link text is not checked against the patterns", "leak_search.py",
    "for _, kind in scan_lines([target], terms, False)]",
    'for _, kind in scan_lines([target], terms, False) if kind.startswith("term")]',
    LK + "test_a_link_whose_target_path_holds_a_home_path_is_reported")
add("leak: a link hit is printed with a line number", "leak_search.py",
    '[("link", kind)', '[(1, kind)', LK + "test_a_link_whose_target_path_holds_a_home_path_is_reported")
add("leak: the allow list skips a link", "leak_search.py",
    "scan_lines([target], terms, False)", "scan_lines([target], terms, True)",
    LK + "test_allow_does_not_skip_a_link")
add("leak: a link to a folder is not checked", "leak_search.py",
    "linked_dirs = [d for d in dirs if os.path.islink(os.path.join(base, d))]", "linked_dirs = []",
    LK + "test_a_link_to_a_folder_is_checked_and_never_entered")
add("leak: a checked link is not counted", "leak_search.py",
    "        checked += 1\n", "        checked += 0 if kind == KIND_LINK else 1\n",
    LK + "test_a_checked_link_counts_toward_the_file_total")
add("leak: hidden folders are skipped", "leak_search.py",
    "if d not in SKIP_DIRS and d not in linked_dirs",
    'if d not in SKIP_DIRS and d not in linked_dirs and not d.startswith(".")',
    LK + "test_hidden_files_and_folders_are_read")
add("leak: hits exit 2", "leak_search.py",
    "EXIT_HITS = 1", "EXIT_HITS = 2", LK + "test_a_pattern_hit_alone_exits_1")
add("leak: a usage error exits 1", "leak_search.py",
    "EXIT_USAGE = 2", "EXIT_USAGE = 1", LK + "test_no_arguments_exits_2")
add("leak: extra positional arguments are ignored", "leak_search.py",
    "if len(args) != 2:", "if len(args) < 2:", LK + "test_three_positional_arguments_exit_2")
add("leak: a missing target argument is ignored", "leak_search.py",
    "if len(args) != 2:", "if len(args) > 2:", LK + "test_one_argument_exits_2")
add("leak: --allow with no file is accepted", "leak_search.py",
    "        if not allow:", "        if False:", LK + "test_allow_with_no_file_exits_2")
add("leak: an option after --allow is read as a file", "leak_search.py",
    '            raise UsageError("unexpected option %s after --allow" % item)', "            pass",
    LK + "test_option_after_allow_exits_2")
add("leak: an unreadable terms file is not a usage error", "leak_search.py",
    "    except OSError as exc:\n        raise UsageError(\"cannot read terms file",
    "    except ValueError as exc:\n        raise UsageError(\"cannot read terms file",
    LK + "test_missing_terms_file_exits_2")
add("leak: a terms file with no terms is accepted", "leak_search.py",
    "        if not terms:\n", "        if False:\n",
    LK + "test_an_empty_terms_file_exits_2_and_scans_nothing")
add("leak: a target that is not a folder is accepted", "leak_search.py",
    "if not os.path.isdir(root):", "if False:", LK + "test_target_that_is_not_a_folder_exits_2")

# leak_search.py: a long line, a file that cannot be read, names
add("leak: the email pattern loses its look-behind and goes quadratic", "leak_search.py",
    'r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@', 'r"[A-Za-z0-9._%+-]+@',
    LK + "test_a_long_run_of_name_characters_with_no_at_sign_finishes_quickly")
add("leak: a file that could not be read is not counted", "leak_search.py",
    "            unreadable += 1\n", "            pass\n",
    LK + "test_a_file_that_cannot_be_read_is_named_and_the_run_exits_2")
add("leak: names are never checked", "leak_search.py",
    "    return [kind for _, kind in scan_lines([name], terms, False)]", "    return []",
    LK + "test_a_file_name_that_holds_a_term_is_reported")


# leak_search.py: special files
add("leak: a named pipe is opened like a file", "leak_search.py",
    "        elif is_regular_file(path):\n", "        elif True:\n",
    LK + "test_a_named_pipe_is_skipped_and_does_not_change_the_exit_code")
add("leak: a named pipe is counted as unreadable", "leak_search.py",
    "            sys.stderr.write(\"leak_search.py: skipped special file %s\\n\" % rel)\n            continue\n",
    "            sys.stderr.write(\"leak_search.py: skipped special file %s\\n\" % rel)\n            unreadable += 1\n            continue\n",
    LK + "test_a_named_pipe_is_skipped_and_does_not_change_the_exit_code")
add("leak: the name of a special file is not checked", "leak_search.py",
    "        if rel != \".\":\n", "        if rel != \".\" and kind != KIND_FILE:\n",
    LK + "test_the_name_of_a_named_pipe_is_still_checked")
add("leak: a link is scanned as a file", "leak_search.py",
    "yield path, KIND_LINK if os.path.islink(path) else KIND_FILE", "yield path, KIND_FILE",
    LK + "test_a_link_that_points_at_a_named_pipe_is_not_opened")

# leak_search.py: home paths
add("leak: a home path counts only when a slash follows the account name", "leak_search.py",
    r'|[A-Za-z0-9._-]+)"', r')"',
    LK + "test_a_home_path_that_ends_the_line_is_found")
add("leak: a home path is not found when a quote ends the account name", "leak_search.py",
    r'|[A-Za-z0-9._-]+)"', r'|[A-Za-z0-9._-]+(?=[/\s]))"',
    LK + "test_a_home_path_whose_account_name_ends_at_a_quote_is_found")
add("leak: a Windows home path is limited to the C drive", "leak_search.py",
    r"(?<![A-Za-z])[A-Za-z]:", r"(?<![A-Za-z])C:",
    LK + "test_a_windows_home_path_is_found_with_either_slash_and_any_drive_letter")
add("leak: a Windows home path is found only with backslashes", "leak_search.py",
    r"[A-Za-z]:[\\/]{1,2}[Uu]sers", r"[A-Za-z]:[\\]{1,2}[Uu]sers",
    LK + "test_a_windows_home_path_is_found_with_either_slash_and_any_drive_letter")
add("leak: a placeholder account name is read as an account", "leak_search.py",
    r"/(?:Users|home)/(?:[^/\s]+/|", r"/(?:Users|home)/(?:[^/\s]+/|[^/\s]+|",
    LK + "test_a_placeholder_or_a_path_that_names_no_account_is_not_found")
add("leak: the home path pattern takes exponential time", "leak_search.py",
    r"(?:[^/\s]+/|", r"(?:(?:[^/\s]+)+/|",
    LK + "test_long_lines_that_almost_match_the_home_path_pattern_finish_quickly")

# leak_search.py: the walk reports an unlistable folder in place, and the target's own name is not checked
add("leak: an unlistable folder is only reported at the end of the walk", "leak_search.py",
    "        while problems:\n            yield problem_path(problems.pop(0), root), KIND_UNREADABLE\n        if base != root:\n",
    "        if base != root:\n",
    LK + "test_an_unreadable_folder_is_reported_before_the_folders_after_it")
add("leak: the name of the target folder is checked", "leak_search.py",
    '        if rel != ".":\n', "        if True:\n",
    LK + "test_the_name_of_the_target_folder_itself_is_not_checked")
add("leak: a name with undecodable bytes raises when printed", "leak_search.py",
    '            stream.reconfigure(errors="backslashreplace")\n', '            stream.reconfigure(errors="strict")\n',
    LK + "test_a_name_with_undecodable_bytes_is_printed_escaped_on_both_streams")
add("leak: only stdout escapes a name with undecodable bytes", "leak_search.py",
    "    for stream in (sys.stdout, sys.stderr):\n", "    for stream in (sys.stdout,):\n",
    LK + "test_a_name_with_undecodable_bytes_is_printed_escaped_on_both_streams")

# mutation_driver.py itself: skipped tests, timeouts and the summary line
# (each old text spans a line break, so it does not match the copy of itself written below)
MD = "test_mutation_driver."
add("driver: a skipped test counts as a pass", "mutation_driver.py",
    '    if "skipped=" in lines[-1]:\n        return SKIPPED\n',
    '    if False:\n        return SKIPPED\n',
    MD + "ClassifyTests.test_a_run_that_skips_itself_is_not_a_pass")
add("driver: only the last line of stderr decides a skip is not looked for", "mutation_driver.py",
    '    if "skipped=" in lines[-1]:\n',
    '    if "skipped=" in err:\n',
    MD + "ClassifyTests.test_the_word_skipped_before_the_last_line_does_not_make_a_pass_a_skip")
add("driver: a timeout is classified as a failure", "mutation_driver.py",
    '    if code is None:\n        return TIMED_OUT\n',
    '    if code is None:\n        return FAILED\n',
    MD + "ClassifyTests.test_a_timeout_is_a_timeout_and_not_a_failure")
add("driver: an exit 0 with no test run is a pass", "mutation_driver.py",
    '    if "Ran 1 test" not in err:\n        return UNCLEAR\n',
    '    if "Ran 1 test" not in err:\n        return PASSED\n',
    MD + "ClassifyTests.test_an_exit_0_with_no_test_run_is_unclear_and_not_a_pass")
add("driver: the not run here line is not printed", "mutation_driver.py",
    '                print("not run here: %s (skipped)" % test_id)\n',
    '                pass\n',
    MD + "MainTests.test_a_skipped_test_is_not_run_and_its_mutation_is_neither_killed_nor_survived")
add("driver: the mutations of a skipped test are run anyway", "mutation_driver.py",
    '            if test_id in not_run_tests:\n',
    '            if False:\n',
    MD + "MainTests.test_a_skipped_test_is_not_run_and_its_mutation_is_neither_killed_nor_survived")
add("driver: the not run count is always zero", "mutation_driver.py",
    '        len(MUTATIONS), len(killed), len(survived), len(not_run))\n',
    '        len(MUTATIONS), len(killed), len(survived), 0)\n',
    MD + "MainTests.test_a_skipped_test_is_not_run_and_its_mutation_is_neither_killed_nor_survived")
add("driver: a mutation run that times out is counted as killed", "mutation_driver.py",
    '                timed_out.append(name)\n',
    '                killed.append(name)\n',
    MD + "MainTests.test_a_mutation_run_that_times_out_is_reported_and_never_killed")
add("driver: a timeout does not change the exit code", "mutation_driver.py",
    '    return 1 if survived or timed_out else 0\n',
    '    return 1 if survived else 0\n',
    MD + "MainTests.test_a_mutation_run_that_times_out_is_reported_and_never_killed")
add("driver: a setup run that times out is accepted", "mutation_driver.py",
    '                print("timed out: %s" % test_id)\n                problems += 1\n',
    '                print("timed out: %s" % test_id)\n',
    MD + "MainTests.test_a_setup_run_that_times_out_is_a_setup_problem")
add("driver: a survivor does not change the exit code", "mutation_driver.py",
    '    return 1 if survived or timed_out else 0\n',
    '    return 1 if timed_out else 0\n',
    MD + "MainTests.test_a_survivor_gives_exit_1_and_is_counted")
add("driver: a failing setup run is accepted", "mutation_driver.py",
    '                print("setup problem: %s does not pass on the unbroken scripts" % test_id)\n                problems += 1\n',
    '                print("setup problem: %s does not pass on the unbroken scripts" % test_id)\n',
    MD + "MainTests.test_a_setup_run_that_fails_is_a_setup_problem")


def run_test(scripts_dir, test_id):
    env = dict(os.environ, OPENSOURCE_SCRIPTS_DIR=scripts_dir, PYTHONDONTWRITEBYTECODE="1")
    try:
        done = subprocess.run(
            [sys.executable, "-m", "unittest", "-q", test_id], cwd=HERE, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None, ""
    return done.returncode, done.stderr


PASSED = "passed"
FAILED = "failed"
SKIPPED = "skipped"
TIMED_OUT = "timed out"
UNCLEAR = "unclear"


def classify(code, err):
    """Say how one run of one named test went, from its exit code and its stderr.

    code is None when the run timed out. A test that skips itself (for example
    when the process is root and can read a mode 000 file) exits 0 with
    "OK (skipped=1)" as unittest's last line, so it is told apart from a pass.
    """
    if code is None:
        return TIMED_OUT
    if code != 0:
        return FAILED
    if "Ran 1 test" not in err:
        return UNCLEAR
    lines = err.strip().splitlines()
    if "skipped=" in lines[-1]:
        return SKIPPED
    return PASSED


def main():
    with tempfile.TemporaryDirectory() as work:
        pristine = os.path.join(work, "pristine")
        shutil.copytree(SCRIPTS, pristine, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(os.path.join(HERE, "mutation_driver.py"), pristine)
        problems = 0
        not_run_tests = set()
        for test_id in sorted(set(item[4] for item in MUTATIONS)):
            outcome = classify(*run_test(pristine, test_id))
            if outcome == SKIPPED:
                print("not run here: %s (skipped)" % test_id)
                not_run_tests.add(test_id)
            elif outcome == TIMED_OUT:
                print("timed out: %s" % test_id)
                problems += 1
            elif outcome != PASSED:
                print("setup problem: %s does not pass on the unbroken scripts" % test_id)
                problems += 1
        if problems:
            return 1
        killed = []
        survived = []
        not_run = []
        timed_out = []
        for index, (name, script, old, new, test_id) in enumerate(MUTATIONS):
            if test_id in not_run_tests:
                not_run.append(name)
                continue
            broken = os.path.join(work, "m%d" % index)
            shutil.copytree(pristine, broken)
            path = os.path.join(broken, script)
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read()
            if text.count(old) != 1:
                print("setup problem: %r appears %d times in %s" % (old[:60], text.count(old), script))
                return 1
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text.replace(old, new))
            outcome = classify(*run_test(broken, test_id))
            if outcome == TIMED_OUT:
                timed_out.append(name)
                print("timed out: %s" % name)
            elif outcome == SKIPPED:
                not_run.append(name)
            elif outcome == FAILED:
                killed.append(name)
                print("killed: %s" % name)
            else:
                survived.append(name)
                print("survived: %s (%s)" % (name, test_id.split(".")[-1]))
            shutil.rmtree(broken)
    print("")
    line = "mutations: %d, killed: %d, survived: %d, not run: %d" % (
        len(MUTATIONS), len(killed), len(survived), len(not_run))
    if timed_out:
        line += ", timed out: %d" % len(timed_out)
    print(line)
    return 1 if survived or timed_out else 0


if __name__ == "__main__":
    sys.exit(main())
