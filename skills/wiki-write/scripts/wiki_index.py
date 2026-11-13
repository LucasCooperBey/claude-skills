#!/usr/bin/env python3
"""Rebuild INDEX.md from wiki markdown. Standard library only. No network.

did the work: INDEX N entries, with N greater than zero
had no work: INDEX: no entries
could not do it: ERROR: could not build index: ...
"""

import os
import re
import sys
import tempfile
import time

DIRS = ["decisions", "synthesis", "counterfactuals"]
FENCE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def wiki_dir():
    value = os.environ.get("WIKI_DIR")
    if value:
        return value
    return "./wiki"


def fm_value(fm, key):
    """Frontmatter scalar, including a folded block."""
    match = re.search(r"(?m)^%s:[ \t]*(.*)$" % re.escape(key), fm)
    if not match:
        return ""
    val = match.group(1).strip().strip('"').strip("'")
    if val not in (">", "|", ">-", "|-", ">+", "|+", ""):
        return val
    lines = fm.split("\n")
    start = -1
    prefix = re.compile(r"^%s:" % re.escape(key))
    for index, line in enumerate(lines):
        if prefix.match(line):
            start = index
            break
    buf = []
    for line in lines[start + 1:]:
        if re.match(r"^\s+\S", line):
            buf.append(line.strip())
        elif line.strip() == "":
            continue
        else:
            break
    return " ".join(buf)


def alt_ids(fm):
    """Decision alternative ids. The chosen id is prefixed with *."""
    collecting = False
    ids = []
    chosen = []
    for line in fm.split("\n"):
        if not collecting:
            if line.startswith("alternatives_considered:"):
                collecting = True
            continue
        if re.match(r"^[A-Za-z0-9_]+:", line):
            break
        matched = re.match(r"^\s+- id:\s*(.*?)\s*$", line)
        if matched:
            ids.append(matched.group(1).strip().strip('"').strip("'"))
            chosen.append(False)
            continue
        if ids and re.match(r"^\s+chosen:\s*true\s*$", line):
            chosen[-1] = True
    parts = []
    for index, name in enumerate(ids):
        if not name:
            continue
        prefix = "*" if chosen[index] else ""
        parts.append(prefix + name)
    return ", ".join(parts)


def list_markdown(directory):
    names = []
    for name in os.listdir(directory):
        if not name.endswith(".md") or name == ".gitkeep":
            continue
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            names.append(name)
    names.sort()
    return names


def entry_from(folder, name, path):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    rel = "%s/%s" % (folder, name)
    if text.startswith("---") and not FENCE.match(text):
        return {"rel": rel, "broken": True}
    match = FENCE.match(text)
    if match:
        fm = match.group(1)
    else:
        fm = ""
    status = fm_value(fm, "status").lower()
    eid = fm_value(fm, "id") or name[:-3]
    entry_type = fm_value(fm, "type") or "?"
    date = fm_value(fm, "date") or "?"
    actors = fm_value(fm, "actors") or "[]"
    tags = fm_value(fm, "tags") or "[]"
    summary = re.sub(r"\s+", " ", fm_value(fm, "summary")).strip()
    if not summary:
        summary = "(no summary)"
    extras = ""
    if entry_type == "decision":
        confidence = fm_value(fm, "confidence") or "?"
        alts = alt_ids(fm) or "?"
        extras = " | confidence=%s | alts=[%s]" % (confidence, alts)
    line = "- `%s` | %s | %s | actors=%s | tags=%s%s | %s" % (
        eid, entry_type, date, actors, tags, extras, summary)
    return {
        "rel": rel,
        "broken": False,
        "superseded": status == "superseded",
        "line": line,
    }


def render(wiki):
    sections = []
    skipped = []
    count = 0
    total_size = 0
    seen = 0
    oldest = None
    for folder in DIRS:
        directory = os.path.join(wiki, folder)
        if not os.path.isdir(directory):
            continue
        names = list_markdown(directory)
        if not names:
            continue
        rows = []
        for name in names:
            path = os.path.join(directory, name)
            seen += 1
            stamp = os.path.getmtime(path)
            base = name[:-3]
            if oldest is None or (stamp, base) < oldest[0]:
                oldest = ((stamp, base), base)
            item = entry_from(folder, name, path)
            if item["broken"]:
                skipped.append(item["rel"])
                continue
            if item["superseded"]:
                continue
            rows.append(item["line"])
            count += 1
            total_size += os.path.getsize(path)
        sections.append((folder, rows))
    skipped.sort()
    lines = [
        "# Wiki index",
        "",
        "Generated: %s" % time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "",
        "Format: `<id> | <type> | <date> | actors=[..] | tags=[..] | "
        "confidence=<c> | alts=[*chosen, rejected, ...] | <summary>`",
        "",
        "Reflections are listed in the counterfactuals section.",
        "",
        "A reader loads this file, pairs it with a question, and opens the entries that match.",
        "",
        "---",
        "",
    ]
    for folder, rows in sections:
        lines.append("## %s" % folder)
        lines.append("")
        for row in rows:
            lines.append(row)
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Stats")
    lines.append("")
    lines.append("- Active entries: %d" % count)
    lines.append("- Total size: %dB" % total_size)
    if oldest is not None:
        lines.append("- Oldest entry: %s" % oldest[1])
    lines.append("")
    text = "\n".join(lines)
    return text, count, total_size, skipped, seen


def write_index(wiki, text):
    fd, tmp = tempfile.mkstemp(prefix=".INDEX.", dir=wiki)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, os.path.join(wiki, "INDEX.md"))
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main():
    wiki = wiki_dir()
    if not os.path.isdir(wiki):
        if os.path.exists(wiki):
            sys.stderr.write("ERROR: could not build index: WIKI_DIR is not a directory\n")
            return 1
        print("INDEX: no entries")
        return 0
    try:
        text, count, total_size, skipped, seen = render(wiki)
        write_index(wiki, text)
    except OSError as exc:
        sys.stderr.write("ERROR: could not build index: %s\n" % exc)
        return 1
    if skipped:
        print("skipped %d entries without a closing frontmatter fence: %s" % (
            len(skipped), ", ".join(skipped)))
    if seen == 0:
        print("INDEX: no entries")
    else:
        print("INDEX: %d entries, %dB" % (count, total_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
