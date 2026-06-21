---
name: frontend-design
description: Builds web components, pages, applications, landing pages, and styled web UIs. Creates distinctive, production-grade frontend interfaces that avoid generic AI aesthetics.
---

# Frontend Design Skill

This skill steers the model away from generic AI aesthetics toward distinctive, production-grade frontend. Pair with `design-taste` for architecture-level decisions.

## Arguments & Stack Detection

```
$ARGUMENTS = raw user input after skill name
```

**Parse first:**
- `--files path1,path2` — scope to specific files
- `--stack react|vue|svelte|vanilla` — override auto-detection
- `--single` — skip multi-variation, build one design
- `--iterate` — refine existing designs from user feedback
- Remaining text = the design brief

**Auto-detect stack** (don't assume React + Tailwind):
1. Check `package.json` for framework (next, nuxt, svelte, astro, vite)
2. Check for Tailwind config → use Tailwind classes. No config → use CSS modules or vanilla CSS
3. Check for existing component library (shadcn, radix, vuetify) → extend it, don't fight it
4. No `package.json` → plain HTML/CSS

**Time budget:** 25 min for multi-variation. 10 min for single component. If >15 files touched, stop and confirm scope.

---

## Error Handling

- **No frontend project detected:** "This directory has no frontend files. Point me at the right directory or describe what to create."
- **Existing design system found:** Respect it. Don't override brand colors/fonts with recommendations below. Extend, don't replace.
- **Dev server won't start:** Build the files anyway. Note: "Dev server failed — files are written, start manually."
- **User wants something banned below:** Bans are defaults, not laws. If the user explicitly wants glassmorphism or blue buttons, do it well.

---

## Multi-Variation Technique

For landing pages or aesthetic-focused UI, generate **5 distinct designs on routes /1-/5** with navigation bar.

**How to set up routes:** Create 5 page files (e.g., Next.js `app/1/page.tsx` through `app/5/page.tsx`, or Vite with react-router). Add a sticky nav with links between them.

**Why this works:**
- Within context, the model knows the other 4 designs
- It actively makes each one unique from the others
- Roll enough times, steer to what you like

**Skip for**: bug fixes, existing design systems, `--single` flag, or explicitly conservative requests.

---

## What "Distinct" Means

Each variation must differ in **AT LEAST 3** dimensions:

| Dimension | Options |
|-----------|---------|
| Layout structure | Asymmetric, centered, sidebar, split, full-bleed |
| Typography family/pairing | Serif+sans, mono+display, single bold family |
| Color palette | Dark mode, warm earth, cool minimal, high contrast |
| Visual density | Minimal (lots of white), rich (layered elements) |
| Theme | Light, dark, colorful, monochrome |

NEVER submit variations with same layout, different colors. That's lazy.

---

## Iteration Workflow (The Core Value)

After initial 5 designs:

1. **User identifies favorites** — "I like #2 and #4"
2. **User explains what resonated** — "The chunky type on #2, the color blocking on #4"
3. **Generate 5 more inspired by those elements**
4. **Repeat until you have a solid starting point**

---

## Font Recommendations

Use these for NEW projects without an existing design system. If the project already has fonts, keep them.

### Display / Headers

| Font | Vibe |
|------|------|
| **Fraunces** | Quirky serif, character |
| **Playfair Display** | Elegant, editorial |
| **DM Serif Display** | Clean, modern serif |
| **Bebas Neue** | Tall, condensed, bold |
| **Archivo Black** | Heavy, impactful |
| **Syne** | Distinctive, geometric |
| **Space Mono** | Technical, code-y |
| **JetBrains Mono** | Developer aesthetic |

### Body Text

| Font | Vibe |
|------|------|
| **Outfit** | Modern, clean |
| **Plus Jakarta Sans** | Warm, friendly |
| **Nunito Sans** | Rounded, approachable |
| **Source Sans 3** | Neutral, readable |
| **Manrope** | Geometric, modern |
| **Work Sans** | Clean, professional |

### Pairings That Work

```css
/* Elegant editorial */
--font-display: 'Fraunces', serif;
--font-body: 'Source Sans 3', sans-serif;

/* Bold modern */
--font-display: 'Bebas Neue', sans-serif;
--font-body: 'Outfit', sans-serif;

/* Technical/dev */
--font-display: 'Space Mono', monospace;
--font-body: 'Manrope', sans-serif;

/* Warm and approachable */
--font-display: 'Syne', sans-serif;
--font-body: 'Plus Jakarta Sans', sans-serif;
```

---

## Color Palettes

### Dark Mode

```css
/* Deep navy + bright accent */
--bg: #0a0f1a; --surface: #141b2d; --text: #e4e8f0; --accent: #00d4aa;

/* True black + gold */
--bg: #000000; --surface: #111111; --text: #ffffff; --accent: #c9a227;

/* Warm dark */
--bg: #1a1612; --surface: #2d2620; --text: #f5f0eb; --accent: #e07a5f;
```

### Light Mode

```css
/* Warm cream */
--bg: #faf6f1; --surface: #ffffff; --text: #1a1612; --accent: #c25b3f;

/* Cool minimal */
--bg: #f8fafc; --surface: #ffffff; --text: #0f172a; --accent: #0ea5e9;

/* High contrast */
--bg: #ffffff; --surface: #f1f5f9; --text: #000000; --accent: #dc2626;
```

### Distinctive Accent Colors

Warm terracotta (#c25b3f), Deep teal (#0d9488), Burnt orange (#ea580c), Gold/ochre (#c9a227), Coral (#f97316), Deep purple (#7c3aed — only if intentional).

---

## Layout Patterns

Adapt these to the detected stack. Examples shown in JSX + Tailwind — translate to Vue templates, Svelte markup, or plain HTML as needed.

### Asymmetric Hero
```
12-col grid: 5-col text left, 7-col visual right, min-h-screen
```

### Split Screen
```
flex row, each half w-1/2, min-h-screen, contrasting backgrounds
```

### Offset Grid
```
3-col grid with staggered mt offsets for visual rhythm
```

### Overlap Elements
```
relative container + absolute decorative element + z-indexed content
```

---

## Motion

Don't scatter micro-interactions. Do one orchestrated page-load animation with staggered entrance (opacity 0→1, y 20→0, 0.1s delay per item).

**Stack-aware implementation:**
- React: `framer-motion` variants if already installed, CSS keyframes if not
- Vue: `<Transition>` / `<TransitionGroup>` built-ins
- Svelte: `transition:fly` / `transition:fade` built-ins
- Vanilla: CSS `@keyframes` + `animation-delay` with intersection observer

Don't add framer-motion as a new dependency just for entrance animations — CSS handles it fine.

---

## Accessibility Pre-Flight

Before delivering any design, verify:
1. **Color contrast** — WCAG AA minimum (4.5:1 body text, 3:1 large text)
2. **Focus indicators** — visible focus ring on all interactive elements
3. **Semantic HTML** — headings in order, buttons for actions, links for navigation
4. **Reduced motion** — wrap animations in `prefers-reduced-motion` media query

See `design-taste` for the full a11y checklist.

---

## Execution Principles

1. **Commit to a direction** — Restrained precision is as bold as maximalist chaos
2. **Intentionality over intensity** — Every choice should feel purposeful
3. **Space is a design element** — Use generous whitespace
4. **Hierarchy through size** — Big headlines, readable body
5. **One accent, not five** — Pick one color, use it sparingly
6. **Responsive by default** — Verify mobile unless told otherwise

---

## Defaults to Avoid

These are defaults, not absolutes. If the user explicitly requests one, do it well.

**Fonts (avoid for new projects):**
- Inter, Roboto, Arial as display fonts (fine as body text in apps with existing systems)

**Colors (avoid):**
- Purple/pink/blue gradients on white (#1 AI slop indicator)

**Patterns (avoid):**
- Hero → features grid → pricing → footer (predictable)
- Card grids with uniform rounded corners
- Glassmorphism everywhere
- 3 centered feature cards
- Blue primary buttons
- Geometric blob SVGs
- Shadcn defaults unchanged

---

## When User Says "Make It Look Good"

1. Ask: "What vibe? Minimal/bold/playful/professional?"
2. Generate 5 variations on /1-/5 (unless `--single`)
3. Wait for feedback on favorites
4. Iterate with steering
5. Don't converge on safe choices

---

## Integration

- **design-taste**: Use for architecture-level design decisions, design system creation, visual identity. frontend-design is for building; design-taste is for deciding.
- **redesign**: Use when upgrading existing UI. frontend-design is for new builds.
- **pp3p**: Run after building to polish the output.

---

## Output Format

After generating designs:
```
SUCCESS: Generated [N] design variations on routes /1-/[N]
METRIC: variations=[count] dimensions_varied=[list]
Navigation: [localhost URL]
Ready for feedback — which designs resonate?
```

For single components:
```
SUCCESS: Created [component type] with [key characteristics]
METRIC: files=[paths]
```
