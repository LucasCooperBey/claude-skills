"""Stdlib checks for write-entry.sh.

WIKI_DIR is a temp directory so no other wiki is read or written.
WIKI_ENTRY_DATE is fixed so the date is not taken from the clock.
"""

import os
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "write-entry.sh")
ENTRY_DATE = "2026-10-01"
FENCE_WARN = "WARN: closing '---' not found in input, caller must format frontmatter properly"


def body_lines(count):
    return ["incident body line %d" % (index + 1) for index in range(count)]


def incident_input(count, include_fence, include_summary):
    # Caller stdin is frontmatter fields, then an exact '---' line, then body.
    # The writer injects the opening fence itself.
    lines = [
        "actors: [ops]",
        "tags: [backups]",
    ]
    if include_summary:
        lines.append("summary: backups probe misread and a cap shorter than the run")
    if include_fence:
        lines.append("---")
        lines.append("")
    lines.extend(body_lines(count))
    return "\n".join(lines) + "\n"


class WriteEntryTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.wiki = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def run_type(self, entry_type, slug, stdin_text):
        env = os.environ.copy()
        env["WIKI_DIR"] = self.wiki
        env["WIKI_ENTRY_DATE"] = ENTRY_DATE
        return subprocess.run(
            ["/bin/bash", SCRIPT, entry_type, slug],
            input=stdin_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            cwd=self.wiki,
            timeout=60,
        )

    def run_incident(self, slug, stdin_text):
        return self.run_type("incident", slug, stdin_text)

    def entry_path(self, slug, folder="decisions"):
        return os.path.join(self.wiki, folder, ENTRY_DATE + "-" + slug + ".md")

    def assert_no_warn(self, stderr):
        warned = [line for line in stderr.splitlines() if "WARN:" in line]
        self.assertEqual(warned, [])

    def written_files(self):
        found = []
        for root, _dirs, files in os.walk(self.wiki):
            for name in files:
                found.append(os.path.join(root, name))
        return found

    def test_well_formed_60_line_body_does_not_warn(self):
        """source: 2026-10-01-backups-probe-misread-and-a-cap-shorter-than-the-run
        A 60-line body keeps the closing fence near the top of the file.
        """
        slug = "sixty-line-body"
        body = body_lines(60)
        proc = self.run_incident(slug, incident_input(60, True, True))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assert_no_warn(proc.stderr)
        path = self.entry_path(slug)
        self.assertTrue(os.path.isfile(path))
        self.assertTrue(path.startswith(os.path.join(self.wiki, "decisions") + os.sep))
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        self.assertEqual(lines[0], "---")
        fences = [index for index, line in enumerate(lines) if line == "---"]
        self.assertEqual(len(fences), 2)
        remainder = lines[fences[1] + 1:]
        if remainder[:1] == [""]:
            remainder = remainder[1:]
        self.assertEqual(remainder, body)

    def test_well_formed_5_line_body_does_not_warn(self):
        """source: 2026-10-01-backups-probe-misread-and-a-cap-shorter-than-the-run
        The same entry with a 5-line body exits 0 and prints no WARN.
        """
        slug = "five-line-body"
        proc = self.run_incident(slug, incident_input(5, True, True))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assert_no_warn(proc.stderr)

    def test_input_without_closing_fence_warns_and_publishes(self):
        """source: 2026-10-01-backups-probe-misread-and-a-cap-shorter-than-the-run
        Input with no exact --- line still publishes and warns.
        """
        slug = "no-closing-fence"
        proc = self.run_incident(slug, incident_input(5, False, True))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(FENCE_WARN, proc.stderr.splitlines())
        self.assertTrue(os.path.isfile(self.entry_path(slug)))

    def test_missing_summary_exits_66_and_writes_no_file(self):
        # source: missing summary is refused
        """source: 2026-10-01-backups-probe-misread-and-a-cap-shorter-than-the-run
        Missing summary exits 66 and leaves the temporary wiki with no file.
        """
        slug = "missing-summary"
        proc = self.run_incident(slug, incident_input(5, True, False))
        self.assertEqual(proc.returncode, 66, proc.stderr)
        self.assertEqual(self.written_files(), [])
        self.assertFalse(os.path.exists(self.entry_path(slug)))

    def test_duplicate_id_is_refused(self):
        # source: duplicate id is refused
        """source: duplicate id is refused
        A second write of the same id exits 65, prints one line, and leaves the first file unchanged.
        """
        slug = "duplicate-note"
        text = incident_input(3, True, True)
        first = self.run_incident(slug, text)
        path = self.entry_path(slug)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, "WROTE: %s\n" % path)
        with open(path, "r", encoding="utf-8") as handle:
            original = handle.read()
        second = self.run_incident(slug, text)
        self.assertEqual(second.returncode, 65, second.stderr)
        self.assertEqual(
            second.stderr.splitlines(),
            ["ERROR: duplicate id '%s-%s'" % (ENTRY_DATE, slug)],
        )
        with open(path, "r", encoding="utf-8") as handle:
            self.assertEqual(handle.read(), original)

    def test_slug_must_be_kebab_case(self):
        # source: slug must be kebab-case
        slug = "Not-Kebab"
        proc = self.run_incident(slug, incident_input(2, True, True))
        self.assertEqual(proc.returncode, 64, proc.stderr)
        self.assertEqual(proc.stderr.splitlines(), ["ERROR: slug must be kebab-case"])
        self.assertEqual(self.written_files(), [])

    def test_unknown_type_is_refused(self):
        # source: type must be decision, synthesis, incident, or reflection
        proc = self.run_type("lesson", "some-slug", incident_input(2, True, True))
        self.assertEqual(proc.returncode, 64, proc.stderr)
        self.assertEqual(len(proc.stderr.splitlines()), 1)
        self.assertIn("invalid type", proc.stderr)
        self.assertEqual(self.written_files(), [])

    def test_folder_for_each_type(self):
        # source: folder mapping per type
        mapping = {
            "decision": "decisions",
            "incident": "decisions",
            "synthesis": "synthesis",
            "reflection": "counterfactuals",
        }
        for entry_type, folder in mapping.items():
            slug = "folder-" + entry_type
            proc = self.run_type(entry_type, slug, incident_input(2, True, True))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            path = self.entry_path(slug, folder)
            self.assertTrue(os.path.isfile(path), path)
            self.assertEqual(proc.stdout, "WROTE: %s\n" % path)


if __name__ == "__main__":
    unittest.main()
