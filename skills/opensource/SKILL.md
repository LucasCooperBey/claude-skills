---
name: opensource
description: Use when the user wants to take one tool out of a private or mixed repository and publish it as its own repository, public or private ("open source this", "publish this tool", "should this be public", "extract this into its own repo"). Runs five yes-or-no checks on visibility, copies the tool into a clean folder with fresh history, scrubs it with asserted replacements, searches for leaks, then creates the repository private first. Not for pushing a repository that already exists as it is.
---

# opensource: extract, scrub, check, publish

This skill turns something built inside a private or mixed repository into its own repository. It decides whether the tool should be public, copies only what the tool needs into a clean folder, removes private details with replacements that must each find their target, searches the result for leaks, and creates the repository private before anything is made public.

It fails closed. Any step that is unsure stops and keeps the repository private.

Two scripts ship with the skill, in the `scripts/` folder next to this file. Run them from this skill's folder, or give their full path. Both use only the Python standard library.

- `scripts/scrub.py RULES.json TARGET_DIR [--dry-run]` applies literal find-and-replace rules and fails if any rule finds nothing.
- `scripts/leak_search.py TERMS.txt TARGET_DIR [--allow FILE ...]` searches for the owner's own private terms and for common secret shapes.

A sample tool, an example terms file and example rules sit beside them, so the scripts can be tried before they are pointed at real work.

## Step 0: decide visibility

Ask five yes-or-no questions about the tool. It may be public only if all five are yes. If any answer is no or unsure, it is private.

1. Is it useful to someone else, on a stack that is not the owner's? A test harness, a prompt pattern or a command line helper is. Glue that only makes sense next to the owner's own deployment is not.
2. Does it work with no private context left in it? After the scrub it must hold no internal paths, business data, customer data or description of the owner's own systems.
3. Is the value a pattern, and not data or an audience? A retry wrapper is a pattern. A scraped dataset, a lead list or a private database is valuable because it is private, so it stays private however generic the code around it looks.
4. Is nothing in it owned by, or identifying, a client or an employer?
5. Does publishing fit the owner's purpose, such as portfolio, teaching or a community resource?

Then choose the owner of the new repository: a personal account or an organization. Choose by who will maintain it. If that is not clear from the conversation, ask the user once.

Write the five answers and the owner choice down in one short note before moving on. The visibility decided here is a ceiling. Step 4 creates the repository private whatever this step says, and a public flip needs a separate yes.

## Step 1: extract into a clean folder

Never publish the source repository in place. A mixed repository never becomes public.

1. Make a new empty folder outside the source repository.
2. Copy only the files the tool needs. Leave behind notes, fixtures with real data, local configuration and anything the tool does not import.
3. Run `git init` in the new folder, so history starts fresh. The first commit comes in Step 4, after the checks.
4. Add a licence. Ask the owner which one; MIT is common. The owner's own name belongs in the licence and nowhere else in the repository.
5. Add a `.gitignore` for dependencies, build output and local environment files, and a `.env.example` holding placeholders only.
6. Keep the project's own build, type-check and test settings as they are. Do not loosen them to make the copy pass.
7. Check the name. `gh repo view OWNER/NAME` should answer not found, and `gh search repos "NAME"` shows collisions and prior art. Name the difference, not the category.

## Step 2: scrub with asserted replacements

A replacement that silently finds nothing leaves private text in a file you believe is clean. So every rule here must find its target, and the run fails if one does not.

First look at what is there. Write a terms file (see Step 3) and run `scripts/leak_search.py` on the clean folder to list the lines that need work. Then write a rules file: a JSON list of objects.

```json
[
  {"file": "src/*.py", "find": "the old text", "replace": "the new text", "count": 2}
]
```

- `file` is a glob relative to the target folder; `**` reaches nested folders. `*` and `**` do not match names that start with a dot, so name a hidden folder in the glob: `.github/**/*.yml`. A file that resolves outside the target folder through a symbolic link is never matched or written. The leak search does read hidden files, which is why it runs after the scrub.
- `find` is literal text, never a pattern. Rules run in order and a later rule sees the result of an earlier one.
- `replace` may be empty.
- `count` is optional. When given, it is the exact total number of occurrences across all matched files.
- A rule fails when any matched file does not hold the `find` text, so a glob should match only files that hold it. A matched file that is not UTF-8 text stops the run.

Typical targets: phrasing about the owner's own environment, output paths that only exist on the owner's machine (replace with a portable default and an environment variable override), business examples (replace with a neutral one), and calls that only work on one operating system (guard them).

Run `python3 scripts/scrub.py RULES.json TARGET_DIR --dry-run` first. It checks every rule and writes nothing. When it prints one `rule N: replaced K in M files` line per rule, run it again without `--dry-run`. If it prints `MISSING rule N: ...` it has written nothing and exits 1: fix the rule or the folder, and run it again.

Write the README fresh. Never copy it from internal documents, which carry internal names and plans.

## Step 3: gates

Nothing is pushed until every gate passes.

1. Write a terms file for `scripts/leak_search.py`: one term per line, matched case-insensitively as plain text, `#` for comments. List the owner's names and handles, employers, clients, products, internal host, repository and folder names, account ids, and any codename.
2. Run `python3 scripts/leak_search.py TERMS.txt TARGET_DIR`. Add `--allow LICENSE` when the licence legitimately carries the owner's name. The script also always checks for home folder paths, email addresses, private key headers and common token shapes, and it prints `path:line: kind` without ever printing the matched text. It never follows a symbolic link; it checks the text of the link itself (where it points) and prints `path:link: kind`, because git publishes that text. It also checks the name of every file, link and folder, because git publishes names, and prints a hit as `path:name: kind` (`--allow` never skips a name). Its last line, on stderr, reads `leak_search.py: N hits in M files`. A folder with no text file to check (empty, or only binary files) prints `leak_search.py: no text file found in TARGET_DIR` and exits 2, which is a failed check and not a clean result. A named pipe, socket or device file is never opened: its name is checked, its content is not read, and stderr says `leak_search.py: skipped special file PATH` without changing the exit code. A file or folder it cannot read is named on stderr as `leak_search.py: could not read PATH`; the last line then ends `, could not read K` and the exit code is 2, so fix the permission and run it again. A terms file with no term in it (empty, or only comments and blank lines) prints `leak_search.py: no terms found in TERMS.txt`, scans nothing and exits 2. Exit code 2 means bad usage, a terms file with no terms, nothing to check, or a file that could not be read.
3. Run the project's own checks: whatever it uses to build, type-check and test.
4. Any hit from either stops the publish. Fix the file, run the checks again, and do not skip a check once. Never bypass a git hook with `--no-verify`.

When unsure whether something is sensitive, treat it as sensitive and keep the repository private.

## Step 4: publish, private first

```bash
git add -A
git commit -m "NAME v0.1.0: one-line description"
gh repo create OWNER/NAME --private --source=. --remote=origin --push --description "what it does, differentiator first"
gh repo view OWNER/NAME --json visibility,url
```

Read the `gh repo view` result and confirm it says private and shows the expected address.

Making it public is a separate step, taken only after the scans in Step 3 have passed and the owner says yes in their own words. Show the owner the command and wait:

```bash
gh repo edit OWNER/NAME --visibility public --accept-visibility-change-consequences
```

If a history scanner such as gitleaks or trufflehog is installed, run it over the new repository's history before the flip. The leak search reads files, not history.

## Step 5: close the loop

- The README is written fresh for outside readers: what the tool does, how to install and run it, what it needs and its limits. It does not reuse internal documentation.
- Credit and licence any code that came from other people, in the README and in the licence files the original authors require.
- Write down which copy is canonical. Usually the internal one keeps evolving; port improvements to the public copy on purpose, not automatically.
- The source repository stays as it was. The extraction is a snapshot, not a migration.

## What this skill never does

- Make a source or mixed repository public. It extracts, and the new repository is the one that may be published.
- Publish anything that failed a check, or skip a check once for convenience.
- Copy internal documents into a public README.
- Publish datasets, scraped collections, contact lists or client work, however generic they look.
- Make a repository public without the owner's yes to that exact step.
