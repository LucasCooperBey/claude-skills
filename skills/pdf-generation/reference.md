# Typst Quick Reference

## Document Setup

```typst
#set document(title: "My Document", author: "Author Name")

#set page(
  paper: "us-letter",
  margin: (top: 1in, bottom: 0.75in, left: 0.75in, right: 0.75in),
  footer: [Page #counter(page).display()]
)

#set text(font: "Libertinus Serif", size: 10.5pt)
#set par(justify: true, leading: 0.75em)
```

## Typography

```typst
// Headings
= Level 1 Heading
== Level 2 Heading

// Text styling
#text(weight: "bold")[Bold text]
#text(style: "italic")[Italic text]
#text(fill: rgb("#ff0000"))[Red text]
#text(size: 14pt)[Larger text]

// Small caps and tracking
#text(tracking: 0.1em)[S P A C E D]
#smallcaps[Small Caps]

// Uppercase
#upper[uppercase text]
```

## Layout

```typst
// Horizontal space
#h(10pt)

// Vertical space
#v(10pt)

// Line break
#linebreak()

// Page break
#pagebreak()
#pagebreak(weak: true)  // Only if needed

// Blocks
#block(width: 100%, inset: 10pt, fill: rgb("#f0f0f0"))[
  Content in a block
]

// Box (inline)
#box(width: 50pt)[inline content]
```

## Grids

```typst
#grid(
  columns: (1fr, 2fr),
  rows: (auto, auto),
  column-gutter: 10pt,
  row-gutter: 8pt,
  align: (left, right),
  [Cell 1], [Cell 2],
  [Cell 3], [Cell 4],
)
```

## Images

```typst
// Basic image
#image("path/to/image.jpg")

// With constraints
#image("photo.jpg", width: 100%)
#image("photo.jpg", height: 6in)

// With fit mode (CRITICAL for preventing overflow)
#image("photo.jpg", width: 80%, height: 5in, fit: "contain")

// fit options:
// - "contain": Fit within bounds, preserve aspect ratio
// - "cover": Fill bounds, may crop
// - "stretch": Distort to fill
```

## Colors

```typst
// RGB
rgb("#ff0000")
rgb(255, 0, 0)

// Grayscale
luma(128)     // Gray (0-255)
luma(50%)     // Gray (percentage)

// Named colors
black, white, red, green, blue
```

## Lines and Shapes

```typst
// Horizontal line
#line(length: 100%, stroke: 1pt + black)

// Box with border
#box(stroke: 0.5pt + luma(220), radius: 2pt)[content]

// Rectangle
#rect(width: 100%, height: 50pt, fill: blue)
```

## Special Characters That Need Escaping

| Character | Meaning | Escape |
|-----------|---------|--------|
| `\` | Escape char | `\\` |
| `#` | Code/function | `\#` |
| `$` | Math mode | `\$` |
| `[` `]` | Content block | `\[` `\]` |
| `_` | Subscript | `\_` |
| `*` | Emphasis | `\*` |
| `@` | Reference | `\@` |
| `<` `>` | Raw/labels | `\<` `\>` |
| `` ` `` | Raw inline | `` \` `` |

## Common Patterns

### Bullet List
```typst
// Using box for custom bullets
#box(width: 12pt)[–] First item
#box(width: 12pt)[–] Second item
```

### Badge/Tag
```typst
#box(fill: rgb("#fff3cd"), inset: (x: 4pt, y: 1pt), radius: 2pt)[
  #text(size: 7pt, fill: rgb("#856404"))[Tag text]
]
```

### Two-Column Layout
```typst
#grid(
  columns: (1fr, auto),
  align: (left, right),
  [Left content],
  [Right content]
)
```

### Conditional Content
```typst
#if condition [
  Content if true
] else [
  Content if false
]
```

## Debugging

```typst
// Show element boundaries (debug)
#set page(fill: rgb("#ffffcc"))

// Check variable value
#repr(myVariable)
```

## Common Mistakes

1. **Forgetting to escape user content** → Text layering/overlap
2. **No height constraint on images** → Page overflow
3. **Using `width: 100%` on portrait images** → Huge vertical space
4. **Newlines in interpolated strings** → Template parse errors
5. **Missing closing brackets** → Compilation failure
