#!/usr/bin/env python3
"""Search a folder for your own private terms and for common secret shapes.

Usage:
    python3 leak_search.py TERMS.txt TARGET_DIR [--allow FILE ...]

TERMS.txt holds one term per line. A term is matched as plain text, ignoring
upper and lower case. Blank lines and lines starting with # are skipped. A
terms file with no term left (empty, or only comments and blank lines) is an
error: it exits 2 and prints "leak_search.py: no terms found in TERMS.txt",
because a search with nothing to look for would read as clean.

Built-in patterns are always on:
    home-path          a home folder path: the Users or home folder, then an
                       account name that ends at a slash, a quote, a space, the
                       end of the line or other punctuation; also a Windows
                       path, a drive letter then Users and an account name,
                       with a slash or a backslash
    email              an email address
    private-key        a private key header line
    token-sk           "sk-" followed by 20 or more letters, digits, - or _
    token-ghp          "ghp_" followed by 20 or more letters, digits or _
    token-github-pat   "github_pat_" followed by 20 or more letters, digits or _
    token-aws          "AKIA" followed by 16 upper-case letters or digits
    token-google       "AIza" followed by 35 letters, digits, - or _
    token-slack        "xox" with one of b, a, p, r, s and a dash

The token patterns must start at the beginning of a word, so "risk-" followed by
a long hyphenated phrase is not read as a key.

It skips .git and node_modules folders and binary files (a file with a zero byte
near its start; UTF-16 text has such bytes, so it is skipped too). It reads
hidden files and folders. A symbolic link is never followed; instead the text of
the link itself (where it points) is checked against the terms and the patterns,
because git publishes that text. A link hit is printed as "path:link: kind". A
link is never skipped by --allow.

The name of every file, symbolic link and folder under TARGET_DIR is checked the
same way, because git publishes names too. A hit in a name is printed as
"path:name: kind", where path is the path of that entry. A name hit comes before
the hits inside that folder or file, binary files' names are checked, and --allow
never skips a name.

It opens only regular files. A named pipe, socket or device is never opened, so
a pipe cannot make it wait forever. Its name is checked like any name, its
content is not read, and it prints "leak_search.py: skipped special file PATH"
on stderr. It is neither counted as checked nor as unreadable, so it does not
change the exit code.

It prints one line per hit as "path:line: kind" where path is relative to
TARGET_DIR and kind is "term N" (N is the term's line number in TERMS.txt) or a
pattern name. It never prints the matched text. The last line, on stderr, is
"leak_search.py: N hits in M files", where N counts every hit line and M counts
the text files and the symbolic links it checked. A folder with nothing to check
(empty, or only binary files) is an error, not a clean result: it exits 2 and
prints "leak_search.py: no text file found
in TARGET_DIR".

A file, link or folder it cannot read is never skipped in silence. It prints
"leak_search.py: could not read PATH" on stderr for each one and goes on. The
last line then reads "leak_search.py: N hits in M files, could not read K" and
the exit code is 2, whatever N is.

--allow names files where a term hit is expected, for example LICENSE carrying
the author's name. Each path is read relative to TARGET_DIR (an absolute path
also works). Term hits in an allowed file are skipped. Pattern hits there are
still reported.

Exit codes: 0 no hits, 1 at least one hit, 2 bad usage, a terms file with no
terms, nothing to check, or a file that could not be read.
Python 3.9 or newer, standard library only.
"""
import os
import re
import stat
import sys

EXIT_CLEAN = 0
EXIT_HITS = 1
EXIT_USAGE = 2  # also: nothing to check, or an entry that could not be read

USAGE = "usage: leak_search.py TERMS.txt TARGET_DIR [--allow FILE ...]"
SKIP_DIRS = {".git", "node_modules"}
BINARY_SNIFF_BYTES = 8192
KIND_FILE = "file"
KIND_LINK = "link"
KIND_DIR = "dir"
KIND_UNREADABLE = "unreadable"

# A token must start where a word starts, so ordinary hyphenated words
# that happen to end in "sk-" do not match. The email pattern must start at the
# first character of a run of name characters; without that, a long run with no
# at sign is tried from every position and the search takes quadratic time.
# A home folder path is the Users or home folder and an account name, where the
# name ends at a slash, a quote, a space, the end of the line or any other
# character a name cannot hold; or the same under a drive letter, with either
# slash, as in a Windows path. Each part is a plain run of one character class,
# so the search takes linear time.
HOME_PATH = re.compile(
    r"/(?:Users|home)/(?:[^/\s]+/|[A-Za-z0-9._-]+)"
    r"|(?<![A-Za-z])[A-Za-z]:[\\/]{1,2}[Uu]sers[\\/]{1,2}[A-Za-z0-9._-]+")

PATTERNS = [
    ("home-path", HOME_PATH),
    ("email", re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")),
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----")),
    ("token-sk", re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}")),
    ("token-ghp", re.compile(r"(?<![A-Za-z0-9])ghp_[A-Za-z0-9_]{20,}")),
    ("token-github-pat", re.compile(r"(?<![A-Za-z0-9])github_pat_[A-Za-z0-9_]{20,}")),
    ("token-aws", re.compile(r"(?<![A-Za-z0-9])AKIA[A-Z0-9]{16}")),
    ("token-google", re.compile(r"(?<![A-Za-z0-9])AIza[A-Za-z0-9_-]{35}")),
    ("token-slack", re.compile(r"(?<![A-Za-z0-9])xox[baprs]-")),
]


class UsageError(Exception):
    """The command line, the terms file or the target folder is unusable."""


def parse_args(argv):
    args = argv[1:]
    allow = []
    if "--allow" in args:
        index = args.index("--allow")
        allow = args[index + 1:]
        args = args[:index]
        if not allow:
            raise UsageError("--allow needs at least one file")
        for item in allow:
            if item.startswith("-"):
                raise UsageError("unexpected option %s after --allow" % item)
    if len(args) != 2:
        raise UsageError("expected TERMS.txt and TARGET_DIR")
    return args[0], args[1], allow


def load_terms(path):
    """Return a list of (line number in the terms file, lower-cased term)."""
    try:
        with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
            raw_lines = handle.read().split("\n")
    except OSError as exc:
        raise UsageError("cannot read terms file: %s" % exc)
    terms = []
    for term_number, raw in enumerate(raw_lines, start=1):
        text = raw.strip()
        if not text:
            continue
        if text.startswith("#"):
            continue
        terms.append((term_number, text.lower()))
    return terms


def allowed_paths(root, allow):
    paths = set()
    for item in allow:
        paths.add(os.path.realpath(os.path.join(root, item)))
    return paths


def walk_entries(root):
    """Yield (path, kind) for every entry under root, in a fixed order.

    kind is KIND_DIR for a folder, yielded when the walk enters it (before any
    entry inside it), KIND_FILE, KIND_LINK for a symbolic link (a link to a
    folder is yielded as a link and never entered), or KIND_UNREADABLE for a
    folder whose list of entries could not be read.
    """
    problems = []
    for base, dirs, names in os.walk(root, onerror=problems.append):
        while problems:
            yield problem_path(problems.pop(0), root), KIND_UNREADABLE
        if base != root:
            yield base, KIND_DIR
        linked_dirs = [d for d in dirs if os.path.islink(os.path.join(base, d))]
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and d not in linked_dirs)
        for name in sorted(names + linked_dirs):
            path = os.path.join(base, name)
            yield path, KIND_LINK if os.path.islink(path) else KIND_FILE
    while problems:
        yield problem_path(problems.pop(0), root), KIND_UNREADABLE


def problem_path(exc, root):
    return getattr(exc, "filename", None) or root


def read_lines(path):
    """Return the file's lines, or None when it is binary. Raises OSError when unreadable."""
    with open(path, "rb") as handle:
        data = handle.read()
    if b"\0" in data[:BINARY_SNIFF_BYTES]:
        return None
    return data.decode("utf-8", errors="replace").split("\n")


def is_regular_file(path):
    """True for a regular file. A named pipe, socket or device is not one, and neither is a link."""
    return stat.S_ISREG(os.lstat(path).st_mode)


def scan_lines(lines, terms, is_allowed):
    """Return a list of (line number, kind) hits for a list of text lines."""
    hits = []
    for line_number, line in enumerate(lines, start=1):
        if not is_allowed:
            lowered = line.lower()
            for term_number, term in terms:
                if term in lowered:
                    hits.append((line_number, "term %d" % term_number))
        for name, regex in PATTERNS:
            if regex.search(line):
                hits.append((line_number, name))
    return hits


def scan_file(path, terms, is_allowed):
    """Return the hits for one file, or None when it is binary. Raises OSError when unreadable."""
    lines = read_lines(path)
    if lines is None:
        return None
    return scan_lines(lines, terms, is_allowed)


def scan_link(path, terms):
    """Return the hits for the text a symbolic link holds. Raises OSError when unreadable."""
    target = os.readlink(path)
    return [("link", kind) for _, kind in scan_lines([target], terms, False)]


def name_hits(name, terms):
    """Return the kinds of hit in a file, link or folder name."""
    return [kind for _, kind in scan_lines([name], terms, False)]


def main(argv):
    # A name with bytes that are not text (possible on Linux) must be printed escaped, not raise.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    try:
        terms_path, root, allow = parse_args(argv)
        terms = load_terms(terms_path)
        if not terms:
            raise UsageError("no terms found in %s" % terms_path)
        if not os.path.isdir(root):
            raise UsageError("target is not a folder: %s" % root)
    except UsageError as exc:
        sys.stderr.write("leak_search.py: %s\n%s\n" % (exc, USAGE))
        return EXIT_USAGE
    allowed = allowed_paths(root, allow)
    total = 0
    checked = 0
    unreadable = 0
    for path, kind in walk_entries(root):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        if rel != ".":
            for name_kind in name_hits(os.path.basename(path), terms):
                print("%s:name: %s" % (rel, name_kind))
                total += 1
        if kind == KIND_DIR:
            continue
        hits = None
        special = False
        failed = kind == KIND_UNREADABLE
        if not failed:
            try:
                if kind == KIND_LINK:
                    hits = scan_link(path, terms)
                elif is_regular_file(path):
                    hits = scan_file(path, terms, os.path.realpath(path) in allowed)
                else:
                    special = True
            except OSError:
                failed = True
        if special:
            sys.stdout.flush()
            sys.stderr.write("leak_search.py: skipped special file %s\n" % rel)
            continue
        if failed:
            sys.stdout.flush()
            sys.stderr.write("leak_search.py: could not read %s\n" % rel)
            unreadable += 1
            continue
        if hits is None:
            continue
        checked += 1
        for where, hit_kind in hits:
            print("%s:%s: %s" % (rel, where, hit_kind))
            total += 1
    sys.stdout.flush()
    if unreadable:
        sys.stderr.write("leak_search.py: %d hits in %d files, could not read %d\n" % (total, checked, unreadable))
        return EXIT_USAGE
    if checked == 0:
        sys.stderr.write("leak_search.py: no text file found in TARGET_DIR\n")
        return EXIT_USAGE
    sys.stderr.write("leak_search.py: %d hits in %d files\n" % (total, checked))
    return EXIT_HITS if total else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main(sys.argv))
