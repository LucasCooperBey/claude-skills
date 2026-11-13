"""Index rebuild checks.

Source recovery tests that talk to a vector store are not ported: that
store is outside this kit (no network, standard library only). These
tests cover the local INDEX.md rebuild: active lines, superseded files
left on disk and omitted, and a missing closing fence skipped.
"""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "scripts", "build-index.sh")

ENTRY = """---
id: 2026-11-12-alpha-note
type: decision
date: 2026-11-12
actors: [me, claude]
tags: [example, workflow]
summary: >
  First sentence of the note.
  Second sentence of the note.
status: active
confidence: high
alternatives_considered:
  - id: skip-the-note
    one_liner: leave it unwritten
  - id: write-the-note
    one_liner: file it
    chosen: true
---

# Alpha note

## What changed

The note exists.
"""

KEPT = """---
id: 2026-11-12-kept-note
type: incident
date: 2026-11-12
actors: [me, claude]
tags: [example, incidents]
summary: A kept note sits beside a broken file.
status: active
---

# Kept note
"""

SUPERSEDED = """---
id: 2026-11-12-old-note
type: decision
date: 2026-11-12
actors: [me, claude]
tags: [example, decisions]
summary: This note was replaced and should leave the index.
status: superseded
---

# Old note
"""


class WikiIndexTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.wiki = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def build(self, wiki=None):
        env = os.environ.copy()
        env["WIKI_DIR"] = self.wiki if wiki is None else wiki
        env["PYTHON"] = sys.executable
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            ["/bin/bash", BUILD],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            cwd=self.wiki,
            timeout=60,
        )

    def write_md(self, folder, name, text):
        directory = os.path.join(self.wiki, folder)
        os.makedirs(directory)
        path = os.path.join(directory, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def index_text(self):
        with open(os.path.join(self.wiki, "INDEX.md"), "r", encoding="utf-8") as handle:
            return handle.read()

    def bullet_lines(self, text):
        return [line for line in text.splitlines() if line.startswith("- `")]

    def test_missing_wiki_has_no_work(self):
        # source: a missing wiki reports no entries and writes nothing
        missing = os.path.join(self.wiki, "missing")
        proc = self.build(missing)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "INDEX: no entries\n")
        self.assertFalse(os.path.exists(missing))

    def test_empty_wiki_writes_index_with_no_entries(self):
        # source: an empty wiki rebuilds INDEX.md and reports no entries
        proc = self.build()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "INDEX: no entries\n")
        text = self.index_text()
        self.assertIn("Active entries: 0", text)
        self.assertIn("# Wiki index", text)

    def test_active_entry_is_one_index_line(self):
        # source: build-index writes one line per active entry
        path = self.write_md("decisions", "2026-11-12-alpha-note.md", ENTRY)
        proc = self.build()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        size = os.path.getsize(path)
        self.assertEqual(proc.stdout, "INDEX: 1 entries, %dB\n" % size)
        text = self.index_text()
        self.assertIn(
            "- `2026-11-12-alpha-note` | decision | 2026-11-12 | "
            "actors=[me, claude] | tags=[example, workflow] | "
            "confidence=high | alts=[skip-the-note, *write-the-note] | "
            "First sentence of the note. Second sentence of the note.",
            text,
        )
        self.assertIn("## decisions", text)
        self.assertIn("- Active entries: 1", text)
        again = self.build()
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertTrue(os.path.isfile(path))
        junk = [name for name in os.listdir(self.wiki) if name.startswith(".INDEX")]
        self.assertEqual(junk, [])

    def test_superseded_stays_on_disk_and_leaves_the_index(self):
        # source: superseded entries stay on disk and are omitted from INDEX.md
        path = self.write_md("decisions", "2026-11-12-old-note.md", SUPERSEDED)
        proc = self.build()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "INDEX: 0 entries, 0B\n")
        text = self.index_text()
        self.assertEqual(self.bullet_lines(text), [])
        self.assertNotIn("- `2026-11-12-old-note`", text)
        self.assertTrue(os.path.isfile(path))
        with open(path, "r", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), SUPERSEDED)

    def test_unclosed_fence_is_skipped_and_left_in_place(self):
        # source: an entry without a closing frontmatter fence is skipped
        broken = self.write_md(
            "decisions",
            "2026-11-12-broken-fence.md",
            "---\nid: 2026-11-12-broken-fence\ntype: decision\n",
        )
        kept = self.write_md("synthesis", "2026-11-12-kept-note.md", KEPT)
        proc = self.build()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(
            "skipped 1 entries without a closing frontmatter fence: "
            "decisions/2026-11-12-broken-fence.md",
            proc.stdout,
        )
        size = os.path.getsize(kept)
        self.assertIn("INDEX: 1 entries, %dB" % size, proc.stdout)
        text = self.index_text()
        bullets = self.bullet_lines(text)
        self.assertEqual(len(bullets), 1)
        self.assertIn("2026-11-12-kept-note", bullets[0])
        self.assertNotIn("broken-fence", "\n".join(bullets))
        self.assertTrue(os.path.isfile(broken))
        self.assertTrue(os.path.isfile(kept))


if __name__ == "__main__":
    unittest.main()
