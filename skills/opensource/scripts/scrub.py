#!/usr/bin/env python3
"""Apply literal find-and-replace rules to a folder, and fail if any target is missing.

Usage:
    python3 scrub.py RULES.json TARGET_DIR [--dry-run]

RULES.json is a list of objects:
    {"file": "src/*.py", "find": "old text", "replace": "new text", "count": 2}

    file     a glob relative to TARGET_DIR ("**" matches nested folders).
             * and ** do not match names that start with a dot, so name a
             hidden folder in the glob: ".github/**/*.yml". A file that
             resolves outside TARGET_DIR (through a symbolic link) is never
             matched or written.
    find     a literal string, never a pattern
    replace  the text that takes its place (may be empty)
    count    optional; the total number of occurrences the rule must find
             across all matched files

Rules run in order, and a later rule sees the result of the earlier ones.
Every rule is checked before any file is written. A rule fails when its glob
matches no file, when its find text is absent from any matched file, or when
its count differs. A failed rule prints "MISSING rule N: <find>" and the run
exits 1 having written nothing. That is the point of the script: a replacement
that silently matches nothing leaves private text in a file you think is clean.

On success it prints one line per rule, "rule N: replaced K in M files". With
--dry-run it prints the same lines and writes nothing.

Exit codes: 0 done, 1 a rule target is missing, 2 bad usage or unreadable rules.
Python 3.9 or newer, standard library only.
"""
import glob
import json
import os
import shutil
import sys
import tempfile

EXIT_OK = 0
EXIT_MISSING = 1
EXIT_USAGE = 2

USAGE = "usage: scrub.py RULES.json TARGET_DIR [--dry-run]"
ALLOWED_KEYS = {"file", "find", "replace", "count"}
REQUIRED_KEYS = ("file", "find", "replace")


class UsageError(Exception):
    """The rules file, the target folder or the command line is unusable."""


def load_rules(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        raise UsageError("cannot read rules file: %s" % exc)
    if not isinstance(data, list):
        raise UsageError("rules file must hold a list of rule objects")
    for number, rule in enumerate(data, start=1):
        check_rule(number, rule)
    return data


def check_rule(number, rule):
    label = "rule %d" % number
    if not isinstance(rule, dict):
        raise UsageError("%s is not an object" % label)
    unknown = set(rule) - ALLOWED_KEYS
    if unknown:
        raise UsageError("%s has unknown keys: %s" % (label, ", ".join(sorted(unknown))))
    for key in REQUIRED_KEYS:
        if not isinstance(rule.get(key), str):
            raise UsageError("%s needs a string for '%s'" % (label, key))
    if not rule["file"]:
        raise UsageError("%s has an empty 'file'" % label)
    if not rule["find"]:
        raise UsageError("%s has an empty 'find'" % label)
    segments = rule["file"].replace("\\", "/").split("/")
    if os.path.isabs(rule["file"]) or ".." in segments:
        raise UsageError("%s: 'file' must stay inside the target folder" % label)
    if "count" in rule:
        count = rule["count"]
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise UsageError("%s: 'count' must be a whole number of 1 or more" % label)


def match_files(root, pattern):
    """Return the regular files under root that match the glob, as relative paths.

    A file whose real path lies outside root (a symbolic link in one of its
    folders) is dropped, so a run never writes outside the target.
    """
    found = glob.glob(os.path.join(glob.escape(root), pattern), recursive=True)
    real_root = os.path.realpath(root)
    matched = []
    for path in sorted(set(found)):
        if os.path.islink(path) or not os.path.isfile(path):
            continue
        if not (os.path.realpath(path) + os.sep).startswith(real_root + os.sep):
            continue
        rel = os.path.relpath(path, root)
        if ".git" in rel.split(os.sep):
            continue
        matched.append(rel)
    return matched


def read_text(root, rel):
    path = os.path.join(root, rel)
    try:
        with open(path, "r", encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise UsageError("cannot read %s as UTF-8 text: %s" % (rel, exc))


def plan(rules, root):
    """Run every rule in memory. Nothing is written here."""
    texts = {}
    original = {}
    missing = []
    report = []
    for number, rule in enumerate(rules, start=1):
        files = match_files(root, rule["file"])
        ok = bool(files)
        total = 0
        for rel in files:
            if rel not in texts:
                texts[rel] = read_text(root, rel)
                original[rel] = texts[rel]
            count_here = texts[rel].count(rule["find"])
            if count_here == 0:
                ok = False
            total += count_here
        if ok and "count" in rule and total != rule["count"]:
            ok = False
        if not ok:
            missing.append((number, rule["find"]))
            continue
        for rel in files:
            texts[rel] = texts[rel].replace(rule["find"], rule["replace"])
        report.append((number, total, len(files)))
    return missing, report, texts, original


def write_changes(root, texts, original):
    """Write every changed file. Stage all temporary files first, then swap them in."""
    staged = []
    try:
        for rel in sorted(texts):
            if texts[rel] == original[rel]:
                continue
            path = os.path.join(root, rel)
            handle = tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", newline="", dir=os.path.dirname(path),
                prefix=".scrub-", delete=False)
            staged.append((handle.name, path))
            with handle:
                handle.write(texts[rel])
            shutil.copymode(path, handle.name)
    except OSError as exc:
        for temp, _path in staged:
            try:
                os.unlink(temp)
            except OSError:
                pass
        raise UsageError("cannot stage changes: %s" % exc)
    for temp, path in staged:
        os.replace(temp, path)


def parse_args(argv):
    dry_run = False
    positional = []
    for arg in argv[1:]:
        if arg == "--dry-run":
            dry_run = True
        elif arg.startswith("-"):
            raise UsageError("unknown option %s" % arg)
        else:
            positional.append(arg)
    if len(positional) != 2:
        raise UsageError("expected RULES.json and TARGET_DIR")
    return positional[0], positional[1], dry_run


def main(argv):
    try:
        rules_path, root, dry_run = parse_args(argv)
        rules = load_rules(rules_path)
        if not os.path.isdir(root):
            raise UsageError("target is not a folder: %s" % root)
        missing, report, texts, original = plan(rules, root)
        if missing:
            for number, find in missing:
                print("MISSING rule %d: %s" % (number, find))
            return EXIT_MISSING
        for number, replaced, file_count in report:
            print("rule %d: replaced %d in %d files" % (number, replaced, file_count))
        if not dry_run:
            write_changes(root, texts, original)
        return EXIT_OK
    except UsageError as exc:
        sys.stderr.write("scrub.py: %s\n%s\n" % (exc, USAGE))
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main(sys.argv))
