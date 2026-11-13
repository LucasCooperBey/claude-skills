# pdf-generation

A Claude Code skill with working patterns for making PDFs from code: Typst templates first, with Puppeteer and plain print HTML as fallbacks, and Sharp for photos. Its main rule is to escape every piece of user text before it goes into a Typst template, because characters such as `#`, `$`, `_`, `*`, `@`, `<` and `[` mean something to Typst and break the layout or the build.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/pdf-generation ~/.claude/skills/
```

The folder carries `reference.md` (Typst syntax), `troubleshooting.md` (common faults and fixes) and `scripts/validate-typst.sh`, which checks a `.typ` file for unbalanced brackets, stray `$` and function calls before you compile it. Run the validator from wherever you installed the skill:

```bash
bash ~/.claude/skills/pdf-generation/scripts/validate-typst.sh invoice.typ
```

For a copy inside one project, give that path instead, for example `bash .claude/skills/pdf-generation/scripts/validate-typst.sh invoice.typ`.

## Quick start

Put your data in the project folder (here an `order.json`), then in Claude Code type:

```
Use the pdf-generation skill to turn order.json into a one-page invoice: write invoice.typ, escaping every customer and item string the way the skill says, check it with bash ~/.claude/skills/pdf-generation/scripts/validate-typst.sh invoice.typ, then compile it with typst compile invoice.typ invoice.pdf. Report what you escaped, the validator's output and the result.
```

## Example

The fixture was an `order.json` whose strings hold most of the characters Typst treats as markup:

```json
{
  "invoice": "INV-1042",
  "customer": "O'Brien & Sons #42 <wholesale>",
  "items": [
    {"name": "Widget_v2 [blue]", "qty": 3, "price": 12.50},
    {"name": "50% off *promo* @launch", "qty": 1, "price": 11.00}
  ],
  "currency": "$"
}
```

The skill escaped each string with its `escapeTypstString` rules and placed it in the document text. Its report, trimmed to the table, the validator output and the result:

```
| Source string | Written to `invoice.typ` as |
|---|---|
| `O'Brien & Sons #42 <wholesale>` | `O'Brien & Sons \#42 \<wholesale\>` |
| `Widget_v2 [blue]` | `Widget\_v2 \[blue\]` |
| `50% off *promo* @launch` | `50% off \*promo\* \@launch` |
| currency `$` | `\$` (in every price) |

`'`, `&` and `%` aren't on the skill's escape list, so I left them alone.

Validating invoice.typ...
Potential function calls found (verify these are intentional):
10:  [#text(size: 24pt, weight: "bold")[Invoice]],

File statistics:
  Lines:       29
  Characters:      793
  Open brackets:       18
  Close brackets:       18

Validation complete.

The one flagged line is my own command for the "Invoice" heading, so that's expected.

typst compile invoice.typ invoice.pdf finished with no output, meaning no errors or warnings.
```

The PDF was one US Letter page of 20.6 KB (20,563 bytes). Its text, read back with `pdftotext -layout invoice.pdf -`:

```
Invoice                                                Invoice: INV-1042


Bill to: O’Brien & Sons #42 <wholesale>


 Item                                     Qty   Unit price   Line total

 Widget_v2 [blue]                           3       $12.50       $37.50

 50% off *promo* @launch                    1       $11.00       $11.00

                                                    Total       $48.50
```

Every character prints as written. Typst turns the straight apostrophe in O'Brien into a curly one, which is its normal typography.

## Needs

- Claude Code.
- The `typst` command line compiler for the Typst path (`brew install typst`, or see typst.app).
- Optional, only if your project uses them: `@myriaddreamin/typst.ts` to compile Typst inside a JavaScript app, `sharp` for photos, `puppeteer-core` and a local Chrome for the HTML fallback.

## Limits

- The skill is guidance and patterns. It does not ship a PDF generator; the `generatePdf` calls in its debugging tips stand for your own function.
- The validator is a quick text check. It exits 1 only when no file is given or the file is not found; whatever it finds in the file, it exits 0. It counts `[` and `]` (escaped ones included) and warns when the counts differ, lists up to five lines where a `#` and a lowercase letter follow another character (a `#set` at the start of a line is not listed), and up to five lines where a `$` follows any character but a backslash. A clean result does not prove the file compiles; `typst compile` does.
- The five-tier fallback chain and the browser table describe one way to set up a production pipeline. Take the parts your project needs.
