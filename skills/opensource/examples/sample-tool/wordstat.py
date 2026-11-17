#!/usr/bin/env python3
"""wordstat: count the words in every .txt file of a folder.

Written for the Examplecorp support team as part of project bluefinch.
"""
import os
import sys

# Reports land in the shared reports folder of the build machine.
OUT_DIR = "/mnt/build-machine/wordstat-reports"

# TODO: ask the BLUEFINCH team before changing the report format.


def count_words(path):
    with open(path, "r", encoding="utf-8") as handle:
        return len(handle.read().split())


def main(argv):
    folder = argv[1] if len(argv) > 1 else "."
    out_dir = os.environ.get("WORDSTAT_OUT_DIR", OUT_DIR)
    os.makedirs(out_dir, exist_ok=True)
    lines = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".txt"):
            lines.append("%s %d" % (name, count_words(os.path.join(folder, name))))
    with open(os.path.join(out_dir, "report.txt"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
