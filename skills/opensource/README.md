# opensource

A Claude Code skill for taking one tool out of an internal repository and publishing it as its own repository. It walks through five yes-or-no checks where unsure means private, a copy into a clean folder with fresh history, a scrub whose replacements must each find their target, a leak search, and a repository created private first. The scrub and the leak search ship as stand-alone Python scripts that run on any folder.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
mkdir -p ~/.claude/skills
cp -R claude-skills/skills/opensource ~/.claude/skills/
```

## Quick start

Run these from the skill folder. The sample tool in `examples/sample-tool` holds made-up private terms for the scripts to find.

```bash
# 1. Search the sample for the terms in the example terms file. It finds hits.
python3 scripts/leak_search.py leak-terms.example.txt examples/sample-tool

# 2. Scrub a temporary copy with the example rules.
work=$(mktemp -d)
cp -R examples/sample-tool "$work/sample"
python3 scripts/scrub.py scrub-rules.example.json "$work/sample"

# 3. Search the copy again. LICENSE names the author, so it is allowed. No hits.
python3 scripts/leak_search.py leak-terms.example.txt "$work/sample" --allow LICENSE

# 4. A rule whose target is absent fails, and nothing is written.
printf '[{"file": "README.md", "find": "text that is not there", "replace": "x"}]\n' > "$work/absent.json"
python3 scripts/scrub.py "$work/absent.json" "$work/sample"

# 5. A folder with nothing to check is an error, not a clean result.
mkdir "$work/empty"
python3 scripts/leak_search.py leak-terms.example.txt "$work/empty"
```

The first search and the failing rule each exit 1. The scrub and the second search exit 0. The search of an empty folder exits 2. The search's last line says how many files it checked. Exit code 2 means bad usage, a terms file with no terms, nothing to check, or a file that could not be read. `--dry-run` on `scrub.py` prints the same lines as a real run and writes nothing.

## Example

A real run of the commands above, with the exit code printed after each. The `leak_search.py:` lines are its summary on stderr: hits, then the number of text files and links it checked.

```
$ python3 scripts/leak_search.py leak-terms.example.txt examples/sample-tool
LICENSE:3: term 5
README.md:5: term 3
README.md:5: term 4
wordstat.py:4: term 3
wordstat.py:4: term 4
wordstat.py:12: term 4
leak_search.py: 6 hits in 3 files
exit 1

$ python3 scripts/scrub.py scrub-rules.example.json "$work/sample"
rule 1: replaced 1 in 1 files
rule 2: replaced 1 in 1 files
rule 3: replaced 1 in 1 files
rule 4: replaced 1 in 1 files
exit 0

$ python3 scripts/leak_search.py leak-terms.example.txt "$work/sample" --allow LICENSE
leak_search.py: 0 hits in 3 files
exit 0

$ python3 scripts/scrub.py "$work/absent.json" "$work/sample"
MISSING rule 1: text that is not there
exit 1

$ mkdir "$work/empty"
$ python3 scripts/leak_search.py leak-terms.example.txt "$work/empty"
leak_search.py: no text file found in TARGET_DIR
exit 2
```

Each hit line is `path:line: kind`. A hit in a file, link or folder name is `path:name: kind`, where `path` is the path of that entry. `term 5` means line 5 of the terms file. A built-in pattern shows its name instead, such as `home-path` or `email`. The matched text is never printed. File paths are, so read them before pasting the output into a chat or a ticket.

## Using it on your own tool

1. Write a terms file: one private term per line, such as your names, employers, clients, product and codenames, and internal host and repository names. Lines starting with `#` are comments. Use `leak-terms.example.txt` as a starting point.
2. Write the rules file: a JSON list of `{"file", "find", "replace", "count"}` objects, where `count` is optional. Use `scrub-rules.example.json` as a starting point. A rule fails with a `MISSING` line when any file its glob matches does not hold the `find` text, so point each glob only at files that hold it. A matched file that is not UTF-8 text, such as an image, stops the run with exit 2 and nothing is written. `*` and `**` in `file` do not match names that start with a dot, so name hidden folders in the glob (`.github/**/*.yml`). The leak search does read hidden files, which is why it runs after the scrub.
3. Start Claude Code and ask it to open source a named folder, for example "open source the folder tools/retry-wrapper". The skill asks the five questions, copies the tool into a clean folder, helps write the rules, runs both scripts and your project's own tests, and creates the repository private. It makes the repository public only after you say so.

## Needs

Python 3.9 or newer, git, and the GitHub command line tool (`gh`) for the publish step. The scripts' own tests run from the skill folder with `python3 -m unittest discover -s tests`.

## Limits

- The leak search finds only the terms you list and the shapes it knows: home folder paths, email addresses, private key headers and a short list of token formats. A home folder path counts when it is written out in full: the `Users` or `home` folder at the top of a path and an account name that ends at a slash, a quote, a space, the end of the line or other punctuation, or a Windows path such as a drive letter, `Users` and an account name with either kind of slash. A path that starts with `~` is not found. After the `Users` or `home` folder in a path with forward slashes, any run of characters with no white space in it counts as an account name when another forward slash follows, so a variable or a `<name>` placeholder written there is reported. A variable or a `<name>` placeholder that ends the path, or that stands between backslashes in a Windows path, is not found. A placeholder in plain letters, such as `YOUR_NAME`, cannot be told from an account name and is reported. A package reference written as a name, an at sign and a version number, the form some lock files use for an exact pin, has the shape of an email address and is reported as one.
- `--allow` takes every argument after it as a file name, so put it last.
- It reads files and not git history. It never follows a symbolic link; it checks the text of the link itself (where it points) and reports it as `path:link: kind`. It also checks the name of every file, link and folder (not `.git` or `node_modules` folders, which it never enters) and reports a hit as `path:name: kind`; `--allow` does not skip a name.
- A file or folder it cannot read is named on stderr as `leak_search.py: could not read PATH`. The last line then ends `, could not read K` and the exit code is 2, even when nothing else was found.
- A file with a zero byte in its first 8,192 bytes is treated as binary and skipped, and that includes UTF-16 text. Its name is still checked.
- A named pipe, socket or device file is never opened, so it cannot make the search wait. Its name is checked, its content is not read, and stderr says `leak_search.py: skipped special file PATH`. It is not counted as checked or as unreadable and does not change the exit code.
- A file or folder name that is not valid text (possible on Linux) is printed with a backslash escape, such as `\udcff` for one byte, instead of stopping the run.
- A terms file with no term in it (empty, or only comments and blank lines) exits 2 with `leak_search.py: no terms found in TERMS.txt` and scans nothing, so a search with nothing to look for is never reported as clean.
- A folder with no text file to check (empty, or only binary files) exits 2 with `leak_search.py: no text file found in TARGET_DIR`, so an empty result is never reported as clean.
- `scrub.py` never writes a file that resolves outside the target folder, and its `*` and `**` skip names that start with a dot.
- A clean result does not prove a repository is safe. Run a history scanner as well.

## Related

[shipgate](https://github.com/LucasCooperBey/shipgate) is a fail-closed pre-publish gate that runs gitleaks and trufflehog over the files and the history, which complements these two scripts.
