---
name: canvas-design
description: Creates visual art in PDF and PNG formats covering design philosophies, aesthetic movements, and museum-quality graphics. Communicates through form, space, and color rather than text.
---

# Canvas Design Skill

Visual art creation for print and digital graphics. Communication through form, space, and color — not text.

---

## Process

1. **Understand the intent** — What feeling should this evoke?
2. **Create design philosophy** (.md) articulating aesthetic movement
3. **Express visually on canvas** (.pdf/.png)
4. Generate **3-5 distinct variations** exploring different aesthetic directions
5. Iterate on user favorites

---

## Tools & Stack

### Primary (Recommended)

| Tool | Use Case | Why |
|------|----------|-----|
| **Typst** | PDF generation | Fast, programmable, beautiful output |
| **Sharp** | Image processing | Resize, crop, format conversion |
| **SVG** | Vector graphics | Scalable, editable, web-ready |
| **Mermaid** | Diagrams | Flowcharts, mind maps, architectures |

### Secondary

| Tool | Use Case |
|------|----------|
| ImageMagick | Batch processing, effects |
| Puppeteer | HTML → PDF/PNG |
| html2canvas | Web → image |
| Cairo (via Node) | Programmatic drawing |

### Typst Quick Reference

```typst
// Basic document
#set page(
  width: 1200pt,
  height: 630pt,
  margin: 0pt,
  fill: rgb("#0a0f1a")
)

#set text(font: "Outfit", fill: white)

// Positioned element
#place(
  top + left,
  dx: 100pt,
  dy: 100pt,
  text(size: 72pt, weight: "bold", "Your Title")
)

// Rectangle
#place(
  bottom,
  rect(width: 100%, height: 80pt, fill: rgb("#00d4aa"))
)
```

---

## What "Distinct" Means

Variations must differ in **AT LEAST 3** dimensions:

| Dimension | Options |
|-----------|---------|
| Color palette | Warm/cool, monochrome/vibrant, dark/light |
| Composition | Centered, rule-of-thirds, asymmetric, edge-tension |
| Aesthetic style | Minimalism, maximalism, brutalist, organic |
| Typographic approach | Big type, small type, no type, type as art |
| Visual rhythm | Static, dynamic, linear, chaotic |

NEVER submit variations with same layout, different colors. That's lazy.

---

## Aesthetic Movements to Draw From

### Minimalism
- Maximum restraint
- Abundant white (or negative) space
- One or two focal elements
- Typography as hero

```
┌─────────────────────────────────────┐
│                                     │
│                                     │
│            WORD                     │
│                                     │
│                                     │
└─────────────────────────────────────┘
```

### Swiss/International
- Grid-based, mathematical
- Sans-serif typography (Helvetica roots, but use Outfit/Manrope now)
- High contrast
- Objective, rational

### Bauhaus
- Primary colors + black/white
- Geometric shapes
- Form follows function
- Bold, simple geometry

### Japanese Minimalism (Ma)
- "Negative space as form"
- Asymmetric balance
- Muted palette
- Implied rather than stated

### Brutalism
- Raw, unpolished
- Exposed structure
- Monospace type
- Intentionally jarring

### Neo-Retro
- 70s/80s color palettes
- Grain, noise, analog textures
- Warm earth tones
- Serif display fonts

---

## Color Theory (Quick Reference)

### Monochromatic
One hue, multiple values. Safe, elegant.
```css
--base: #0d9488;
--light: #5eead4;
--dark: #115e59;
```

### Complementary
Opposite on wheel. High contrast, vibrant.
```css
--primary: #0d9488; /* teal */
--accent: #f97316;  /* orange (opposite) */
```

### Analogous
Adjacent on wheel. Harmonious, calm.
```css
--a: #0d9488; /* teal */
--b: #0ea5e9; /* blue */
--c: #10b981; /* green */
```

### Triadic
Evenly spaced. Balanced, dynamic.
```css
--a: #dc2626; /* red */
--b: #0d9488; /* teal */
--c: #c9a227; /* gold */
```

---

## Composition Techniques

### Rule of Thirds
Divide canvas into 3x3 grid. Place focal points at intersections.

```
┌───────┬───────┬───────┐
│       │       │   X   │  ← focal point
├───────┼───────┼───────┤
│       │       │       │
├───────┼───────┼───────┤
│       │       │       │
└───────┴───────┴───────┘
```

### Golden Ratio
Spiral from corner. Place key elements along the curve.

### Edge Tension
Place elements close to (but not touching) edges. Creates visual tension.

### Asymmetric Balance
Heavy element + light element with more space = balanced.

### Overlap
Elements breaking grid boundaries create depth.

---

## Typography as Visual Element

### Type as Art
When text IS the design, not just on the design:

```typst
#place(
  center + horizon,
  rotate(-5deg,
    text(
      size: 200pt,
      weight: "black",
      tracking: -0.05em,
      fill: rgb("#1a1a1a").lighten(90%),
      "WORD"
    )
  )
)

// Smaller text on top
#place(
  center + horizon,
  text(size: 48pt, weight: "bold", "Your Message")
)
```

### Hierarchy Through Scale
Display: 72-200pt
Headline: 36-48pt
Body: 14-18pt
Caption: 10-12pt

---

## Output Specifications

| Use Case | Format | Size | DPI |
|----------|--------|------|-----|
| Print (poster) | PDF | Custom | 300 |
| Print (card) | PDF | 4x6", 5x7" | 300 |
| Web/social | PNG | 1200x630, 1080x1080 | 72-150 |
| OG image | PNG/JPG | 1200x630 | 72 |
| Presentation | PNG | 1920x1080 | 150 |
| Thumbnail | PNG | 1280x720 | 72 |

### Sharp Export Examples

```javascript
// High-quality PNG
await sharp(input)
  .resize(1200, 630, { fit: 'cover' })
  .png({ quality: 100 })
  .toFile(output);

// Print-ready (300 DPI at 4x6")
await sharp(input)
  .resize(1200, 1800) // 4*300 x 6*300
  .png({ quality: 100 })
  .toFile('print-ready.png');
```

---

## Iteration Workflow

1. **User describes intent** — "I need a thumbnail for a video about AI agents"
2. **Create 3-5 variations** exploring different directions
3. **User picks favorites** — "I like #2 and #4"
4. **User explains what resonated** — "The bold type, the dark background"
5. **Generate 3 more** inspired by those elements
6. **Final should feel like 10th iteration, not first draft**

---

## Principles

1. **Text as visual accent, not explanation** — If you need words to explain the design, the design failed
2. **Communication through form, space, color** — Visual language, not verbal
3. **Intentionality over safety** — Commit to a bold direction
4. **One idea per canvas** — Don't dilute with multiple messages
5. **Hierarchy is everything** — What do you see first? Second? Third?

---

## BANNED

**Elements (Never Use)**:
- Purple/pink/blue gradients
- Helvetica, Arial, system fonts
- Centered-everything without visual tension
- Lazy noise overlays (unless intentional aesthetic)
- Fake CLI/terminal aesthetics
- Editorial/newspaper layouts
- Perfect bilateral symmetry
- Floating shapes with no focal point
- Geometric blob SVGs
- Stock photo vibes

**Behaviors (Never Do)**:
- Submit first draft as final
- Use same layout with different colors
- Add text to "explain" the visual
- Default to safe, boring choices

---

## Example Workflow: Thumbnail

```
User: Create a thumbnail for "Building AI Agents in 2026"

1. Philosophy: Bold, technical, futuristic. Dark mode. Agent = helper.

2. Variations:
   /1 - Minimal: Large "AI AGENTS" text, subtle circuit pattern
   /2 - Conceptual: Abstract network nodes, no text
   /3 - Character: Robot icon + human silhouette partnership
   /4 - Technical: Code fragment + glow effect
   /5 - Bold type: "2026" massive, "AI AGENTS" smaller

3. User: "I like #1 and #4 — the minimal approach with technical hints"

4. Generate 3 more:
   /6 - Merge: Large text + subtle code fragments
   /7 - Variation: Monospace type + accent color bar
   /8 - Refined: #4 with better hierarchy

5. User: "#8 is close, make the glow less intense"

6. Final adjustments → export at 1280x720 PNG
```

---

## Templates by Use Case

### Thumbnail (YouTube)
```typst
#set page(width: 1280pt, height: 720pt, margin: 0pt)
#set text(font: "Bebas Neue", fill: white)

#place(
  center + horizon,
  text(size: 120pt, "YOUR TITLE")
)

#place(bottom, rect(width: 100%, height: 4pt, fill: rgb("#00d4aa")))
```

### OG Image
```typst
#set page(width: 1200pt, height: 630pt, margin: 0pt)

// Background gradient (not purple!)
#place(
  rect(
    width: 100%,
    height: 100%,
    fill: gradient.linear(
      rgb("#0a0f1a"),
      rgb("#1a1a2e"),
      angle: 45deg
    )
  )
)

// Title
#place(
  left + horizon,
  dx: 80pt,
  text(size: 64pt, weight: "bold", fill: white, "Title Here")
)
```

### Poster (Minimal)
```typst
#set page(paper: "a3", margin: 2cm)
#set text(font: "Outfit", size: 14pt)

#place(top + left, text(size: 120pt, weight: "black", "WORD"))

#place(bottom + right, text(size: 14pt, "supporting text"))
```

---

## Output Format

After generating visuals, output:

```
✅ SUCCESS: Generated [N] visual variations
📊 METRIC: variations=[count]
📊 METRIC: aesthetic=[movement name]
📊 METRIC: format=[PDF/PNG]
📊 METRIC: dimensions=[WxH]

Files:
- /1: [description] → [path]
- /2: [description] → [path]
...

Ready for feedback — which directions resonate?
```

After iteration:

```
✅ SUCCESS: Refined design based on feedback
📊 METRIC: inspired_by=[#2, #4]
📊 METRIC: preserved=[bold type, dark background]
📄 OUTPUT: [final file path]
```

For single outputs:

```
✅ SUCCESS: Created [asset type] in [aesthetic] style
📊 METRIC: format=[PDF/PNG]
📊 METRIC: size=[dimensions]
📄 OUTPUT: [file path]
```

---

*Communication through form, space, and color. Not text.*
