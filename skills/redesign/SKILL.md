---
name: redesign
description: Upgrades existing websites and apps to premium quality. Audits current design, identifies generic AI patterns, and applies high-end design standards without breaking functionality. Works with any CSS framework or vanilla CSS.
---

# Redesign Skill

## How This Works

1. **Scan** — Read the codebase. Identify the framework, styling method, and current design patterns.
2. **Diagnose** — Run through the audit below. List every generic pattern, weak point, and missing state.
3. **Fix** — Apply targeted upgrades working with the existing stack. Do not rewrite from scratch.

## Design Audit

### Typography
- Browser default fonts or Inter everywhere → Replace with `Geist`, `Outfit`, `Cabinet Grotesk`, `Satoshi`
- Headlines lack presence → Increase size, tighten letter-spacing, reduce line-height
- Body text too wide → Limit to ~65 characters, increase line-height
- Only Regular/Bold weights → Introduce Medium (500) and SemiBold (600)
- Numbers in proportional font → Use monospace or `font-variant-numeric: tabular-nums`
- Orphaned words → Fix with `text-wrap: balance` or `text-wrap: pretty`

### Color and Surfaces
- Pure `#000000` background → Off-black (`#0a0a0a`, `#121212`)
- Oversaturated accents → Keep saturation < 80%
- More than one accent color → Pick one, remove the rest
- Mixing warm and cool grays → Stick to one gray family
- Purple/blue "AI gradient" aesthetic → Most common AI fingerprint, replace
- Generic `box-shadow` → Tint shadows to match background hue
- Flat design with zero texture → Add subtle noise, grain, or micro-patterns
- Random dark sections in a light page → Keep consistent background tone
- Empty flat sections → Add background imagery, patterns, or ambient gradients

### Layout
- Everything centered and symmetrical → Break with offset margins, mixed aspect ratios
- Three equal card columns → 2-column zig-zag, asymmetric grid, or masonry
- `height: 100vh` → `min-height: 100dvh` (iOS Safari fix)
- Complex flexbox math → CSS Grid
- No max-width container → Add ~1200-1440px with auto margins
- No overlap or depth → Negative margins for layering
- Buttons not bottom-aligned in card groups → Pin to bottom
- Mathematical alignment that looks optically wrong → 1-2px optical adjustments

### Interactivity and States
- No hover states → Add background shift, slight scale, or translate
- No active/pressed feedback → `scale(0.98)` or `translateY(1px)`
- Instant transitions → 200-300ms smooth transitions
- Missing focus ring → Visible focus indicators (accessibility requirement)
- No loading states → Skeleton loaders matching layout shape
- No empty states → Composed "getting started" view
- No error states → Clear, inline error messages
- Animations using `top/left/width/height` → `transform` and `opacity` only

### Content
- Generic names ("John Doe") → Diverse, realistic names
- Fake round numbers (`99.99%`) → Organic data (`47.2%`)
- AI copywriting cliches → "Elevate", "Seamless", "Unleash" all banned
- Lorem Ipsum → Real draft copy always
- Same avatar for multiple users → Unique assets per person

### Component Patterns
- Generic card look → Remove border OR use only background OR use only spacing
- 3-card carousel testimonials → Masonry wall, embedded social, single rotating quote
- Modals for everything → Inline editing, slide-over panels, expandable sections
- Footer link farm → Simplify to main paths + legal links

### Strategic Omissions (What AI Forgets)
- No legal links (privacy policy, terms)
- No "back" navigation
- No custom 404 page
- No form validation
- No "skip to content" link
- No cookie consent (if required by jurisdiction)

## Fix Priority (maximum impact, minimum risk)

1. **Font swap** — biggest instant improvement
2. **Color palette cleanup** — remove clashing colors
3. **Hover and active states** — makes interface feel alive
4. **Layout and spacing** — proper grid, max-width, consistent padding
5. **Replace generic components** — swap cliche patterns
6. **Add loading, empty, error states** — makes it feel finished
7. **Polish typography scale** — the premium final touch

## Rules

- Work with the existing tech stack. Do not migrate frameworks.
- Do not break existing functionality. Test after every change.
- Before importing new libraries, check dependency file first.
- Keep changes reviewable and focused. Small improvements over big rewrites.

## Source

Adapted from https://github.com/Leonxlnx/taste-skill (MIT, Copyright (c) 2026 Leonxlnx). Changed for this repo by Lucas Cooper-Bey in 2026: partly rewritten, keeping the "Scan, Diagnose, Fix" opening.
