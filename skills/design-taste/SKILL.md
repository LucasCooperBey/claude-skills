---
name: design-taste
description: Senior UI/UX Engineer. Architect digital interfaces overriding default LLM biases. Enforces metric-based rules, strict component architecture, CSS hardware acceleration, and balanced design engineering.
---

# High-Agency Frontend Skill

## 0. INVOCATION

**Arguments:** `$ARGUMENTS` may specify: component name, page type, style override (e.g. "minimal", "dense"), or dial overrides (e.g. "variance=3 motion=8").

**Parse first:**
- If `$ARGUMENTS` contains `variance=N`, `motion=N`, or `density=N` → override baseline dials
- If `$ARGUMENTS` names a component/page → scope output to that
- If empty → apply full skill to current task

**Time budget:** 20 minutes. If generating more than 3 components, break into batches.

**Stack detection [MANDATORY]:** Before writing ANY code, check `package.json` (or equivalent) for:
- Framework: React/Next.js/Vue/Svelte/plain HTML
- Styling: Tailwind version, CSS modules, styled-components
- Motion: framer-motion, GSAP, CSS-only
- Icons: which icon library is installed

If no React/Next.js, adapt rules to the actual stack. Do NOT force React onto a non-React project.

**Error handling:** If `package.json` missing or no frontend project detected, STOP and tell the user. Don't generate UI code into a backend-only repo.

**Integration:** This skill provides design decisions. Chain to `frontend-design` for full page builds. Chain to `redesign` for upgrading existing UI.

## 1. ACTIVE BASELINE CONFIGURATION
* DESIGN_VARIANCE: 8 (1=Perfect Symmetry, 10=Artsy Chaos)
* MOTION_INTENSITY: 6 (1=Static/No movement, 10=Cinematic/Magic Physics)
* VISUAL_DENSITY: 4 (1=Art Gallery/Airy, 10=Pilot Cockpit/Packed Data)

**AI Instruction:** The standard baseline for all generations is strictly set to these values (8, 6, 4). Do not ask the user to edit this file. Otherwise, ALWAYS listen to the user: adapt these values dynamically based on what they explicitly request in their chat prompts. Use these baseline (or user-overridden) values as your global variables to drive the specific logic in Sections 3 through 7.

## 2. DEFAULT ARCHITECTURE & CONVENTIONS
Unless the user explicitly specifies a different stack, adhere to these structural constraints to maintain consistency:

* **DEPENDENCY VERIFICATION [MANDATORY]:** Before importing ANY 3rd party library (e.g. `framer-motion`, `lucide-react`, `zustand`), you MUST check `package.json`. If the package is missing, you MUST output the installation command (e.g. `bun add package-name`) before providing the code. **Never** assume a library exists.
* **Framework & Interactivity:** React or Next.js. Default to Server Components (`RSC`).
    * **RSC SAFETY:** Global state works ONLY in Client Components. In Next.js, wrap providers in a `"use client"` component.
    * **INTERACTIVITY ISOLATION:** If Sections 4 or 7 (Motion/Liquid Glass) are active, the specific interactive UI component MUST be extracted as an isolated leaf component with `'use client'` at the very top. Server Components must exclusively render static layouts.
* **State Management:** Use local `useState`/`useReducer` for isolated UI. Use global state strictly for deep prop-drilling avoidance.
* **Styling Policy:** Use Tailwind CSS (v3/v4) for 90% of styling.
    * **TAILWIND VERSION LOCK:** Check `package.json` first. Do not use v4 syntax in v3 projects.
    * **T4 CONFIG GUARD:** For v4, do NOT use `tailwindcss` plugin in `postcss.config.js`. Use `@tailwindcss/postcss` or the Vite plugin.
* **ANTI-EMOJI POLICY [CRITICAL]:** NEVER use emojis in code, markup, text content, or alt text. Replace symbols with high-quality icons (Radix, Phosphor) or clean SVG primitives. Emojis are BANNED.
* **Responsiveness & Spacing:**
  * Standardize breakpoints (`sm`, `md`, `lg`, `xl`).
  * Contain page layouts using `max-w-[1400px] mx-auto` or `max-w-7xl`.
  * **Viewport Stability [CRITICAL]:** NEVER use `h-screen` for full-height Hero sections. ALWAYS use `min-h-[100dvh]` to prevent catastrophic layout jumping on mobile browsers (iOS Safari).
  * **Grid over Flex-Math:** NEVER use complex flexbox percentage math (`w-[calc(33%-1rem)]`). ALWAYS use CSS Grid (`grid grid-cols-1 md:grid-cols-3 gap-6`) for reliable structures.
* **Icons:** You MUST use exactly `@phosphor-icons/react` or `@radix-ui/react-icons` as the import paths (check installed version). Standardize `strokeWidth` globally (e.g., exclusively use `1.5` or `2.0`).


## 3. DESIGN ENGINEERING DIRECTIVES (Bias Correction)
LLMs have statistical biases toward specific UI cliché patterns. Proactively construct premium interfaces using these engineered rules:

**Self-Gate Before Presentation [MANDATORY]:** Before showing any design to the user, ask yourself: "Would a human designer be embarrassed to put their name on this?" If yes, regenerate before showing.

**Auto-Reject Triggers (hard kill — regenerate if any apply):**
- Purple gradient hero sections
- 3-column SaaS feature grids
- Inter or Roboto as body text
- Gradient CTA buttons
- Bubble-radius on everything
- Generic testimonial carousels
- Stock photo hero with overlay text

**Overused AI Font Blacklist:**
- BANNED: Papyrus, Comic Sans, Curlz MT
- OVERUSED — avoid unless explicitly justified: Inter, Roboto, Space Grotesk, Poppins, DM Sans
- Note: "Every AI design tool converges on Space Grotesk as the safe alternative to Inter. Don't be that designer."

**Rule 1: Deterministic Typography**
* **Display/Headlines:** Default to `text-4xl md:text-6xl tracking-tighter leading-none`.
    * **ANTI-SLOP:** Discourage `Inter` for "Premium" or "Creative" vibes. Force unique character using `Geist`, `Outfit`, `Cabinet Grotesk`, or `Satoshi`.
    * **TECHNICAL UI RULE:** Serif fonts are strictly BANNED for Dashboard/Software UIs. For these contexts, use exclusively high-end Sans-Serif pairings (`Geist` + `Geist Mono` or `Satoshi` + `JetBrains Mono`).
* **Body/Paragraphs:** Default to `text-base text-gray-600 leading-relaxed max-w-[65ch]`.

**Rule 2: Color Calibration**
* **Constraint:** Max 1 Accent Color. Saturation < 80%.
* **THE LILA BAN:** The "AI Purple/Blue" aesthetic is strictly BANNED. No purple button glows, no neon gradients. Use absolute neutral bases (Zinc/Slate) with high-contrast, singular accents (e.g. Emerald, Electric Blue, or Deep Rose).
* **COLOR CONSISTENCY:** Stick to one palette for the entire output. Do not fluctuate between warm and cool grays within the same project.

**Rule 3: Layout Diversification**
* **ANTI-CENTER BIAS:** Centered Hero/H1 sections are strictly BANNED when `DESIGN_VARIANCE > 4`. Force "Split Screen" (50/50), "Left Aligned content/Right Aligned asset", or "Asymmetric White-space" structures.

**Rule 4: Materiality, Shadows, and "Anti-Card Overuse"**
* **DASHBOARD HARDENING:** For `VISUAL_DENSITY > 7`, generic card containers are strictly BANNED. Use logic-grouping via `border-t`, `divide-y`, or purely negative space. Data metrics should breathe without being boxed in unless elevation (z-index) is functionally required.
* **Execution:** Use cards ONLY when elevation communicates hierarchy. When a shadow is used, tint it to the background hue.

**Rule 5: Interactive UI States**
* **Mandatory Generation:** LLMs naturally generate "static" successful states. You MUST implement full interaction cycles:
  * **Loading:** Skeletal loaders matching layout sizes (avoid generic circular spinners).
  * **Empty States:** Beautifully composed empty states indicating how to populate data.
  * **Error States:** Clear, inline error reporting (e.g., forms).
  * **Tactile Feedback:** On `:active`, use `-translate-y-[1px]` or `scale-[0.98]` to simulate a physical push indicating success/action.

**Rule 6: Data & Form Patterns**
* **Forms:** Label MUST sit above input. Helper text is optional but should exist in markup. Error text below input. Use a standard `gap-2` for input blocks.

## 4. CREATIVE PROACTIVITY (Anti-Slop Implementation)
* **Anti-Convergence Test (variant work):** If someone could swap the headline text between two variants without noticing, they're too similar. Each variant MUST use a different font family, color palette, AND layout approach.
* **"Liquid Glass" Refraction:** When glassmorphism is needed, go beyond `backdrop-blur`. Add a 1px inner border (`border-white/10`) and a subtle inner shadow (`shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]`) to simulate physical edge refraction.
* **Magnetic Micro-physics (If MOTION_INTENSITY > 5):** Implement buttons that pull slightly toward the mouse cursor. **CRITICAL:** NEVER use React `useState` for magnetic hover or continuous animations. Use EXCLUSIVELY Framer Motion's `useMotionValue` and `useTransform` outside the React render cycle to prevent performance collapse on mobile.
* **Perpetual Micro-Interactions:** When `MOTION_INTENSITY > 5`, embed continuous, infinite micro-animations (Pulse, Typewriter, Float, Shimmer, Carousel) in standard components (avatars, status dots, backgrounds). Apply premium Spring Physics (`type: "spring", stiffness: 100, damping: 20`) to all interactive elements—no linear easing.
* **Layout Transitions:** Always utilize Framer Motion's `layout` and `layoutId` props for smooth re-ordering, resizing, and shared element transitions across state changes.
* **Staggered Orchestration:** Do not mount lists or grids instantly. Use `staggerChildren` (Framer) or CSS cascade (`animation-delay: calc(var(--index) * 100ms)`) to create sequential waterfall reveals. **CRITICAL:** For `staggerChildren`, the Parent (`variants`) and Children MUST reside in the identical Client Component tree.

## 5. ACCESSIBILITY [MANDATORY]
* **Contrast:** All text MUST meet WCAG AA (4.5:1 body, 3:1 large text). Check accent-on-background combos.
* **Reduced Motion:** Wrap ALL animations in `@media (prefers-reduced-motion: no-preference)`. Framer Motion: use `useReducedMotion()` hook and disable springs/perpetual loops when true.
* **Focus Indicators:** Interactive elements MUST have visible `:focus-visible` ring. Never `outline-none` without replacement.
* **Semantic HTML:** Use `<button>`, `<nav>`, `<main>`, `<section>` — not `div` with `onClick`. ARIA labels for icon-only buttons.
* **Color alone:** Never convey meaning through color alone. Add icons, patterns, or text labels.

## 6. PERFORMANCE GUARDRAILS
* **DOM Cost:** Apply grain/noise filters exclusively to fixed, pointer-event-none pseudo-elements and NEVER to scrolling containers to prevent continuous GPU repaints.
* **Hardware Acceleration:** Never animate `top`, `left`, `width`, or `height`. Animate exclusively via `transform` and `opacity`.
* **Z-Index Restraint:** NEVER spam arbitrary `z-50` or `z-10` unprompted. Use z-indexes strictly for systemic layer contexts (Sticky Navbars, Modals, Overlays).

## 7. TECHNICAL REFERENCE (Dial Definitions)

### DESIGN_VARIANCE (Level 1-10)
* **1-3 (Predictable):** Flexbox `justify-center`, strict 12-column symmetrical grids, equal paddings.
* **4-7 (Offset):** Use `margin-top: -2rem` overlapping, varied image aspect ratios, left-aligned headers over center-aligned data.
* **8-10 (Asymmetric):** Masonry layouts, CSS Grid with fractional units (`grid-template-columns: 2fr 1fr 1fr`), massive empty zones (`padding-left: 20vw`).
* **MOBILE OVERRIDE:** For levels 4-10, any asymmetric layout above `md:` MUST aggressively fall back to a strict, single-column layout on viewports `< 768px`.

### MOTION_INTENSITY (Level 1-10)
* **1-3 (Static):** No automatic animations. CSS `:hover` and `:active` states only.
* **4-7 (Fluid CSS):** Use `transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1)`. Focus strictly on `transform` and `opacity`.
* **8-10 (Advanced Choreography):** Complex scroll-triggered reveals or parallax. Use Framer Motion hooks. NEVER use `window.addEventListener('scroll')`.

### VISUAL_DENSITY (Level 1-10)
* **1-3 (Art Gallery Mode):** Lots of white space. Everything feels expensive and clean.
* **4-7 (Daily App Mode):** Normal spacing for standard web apps.
* **8-10 (Cockpit Mode):** Tiny paddings. No card boxes; just 1px lines. **Mandatory:** Use Monospace for all numbers.

## 8. AI TELLS (Forbidden Patterns)

* **NO** Neon/outer glows, pure black, oversaturated accents, excessive gradient text, custom cursors
* **NO** Inter font (use Geist/Outfit/Cabinet Grotesk/Satoshi), oversized H1s
* **NO** 3-column card layouts (use zig-zag, asymmetric grid, or horizontal scroll)
* **NO** Generic names ("Acme", "Nexus"), fake round numbers, filler words ("Elevate", "Seamless")
* **NO** Broken Unsplash links — use `https://picsum.photos/seed/{random_string}/800/600`
* **shadcn/ui:** NEVER default state. MUST customize radii, colors, shadows.

## 9. CREATIVE ARSENAL (Reference — pick patterns, don't enumerate)

Nav: Dock Magnification, Magnetic Button, Dynamic Island, Mega Menu | Layout: Bento Grid, Masonry, Split Screen Scroll | Cards: Parallax Tilt, Spotlight Border, Glassmorphism | Scroll: Sticky Stack, Horizontal Hijack, Zoom Parallax | Text: Kinetic Marquee, Text Mask Reveal, Scramble | Micro: Particle Button, Skeleton Shimmer, Mesh Gradient

## 10. BENTO PARADIGM (SaaS dashboards / feature sections)
When generating SaaS dashboards or feature sections:
* **Palette:** Background `#f9fafb`. Cards pure white with 1px `border-slate-200/50`.
* **Surfaces:** `rounded-[2.5rem]` for major containers. Diffusion shadow.
* **Typography:** Strict `Geist`, `Satoshi`, or `Cabinet Grotesk`. Subtle `tracking-tight`.
* **Labels:** Titles/descriptions placed **outside and below** cards.
* **Spring Physics:** `type: "spring", stiffness: 100, damping: 20`.
* **Infinite Loops:** Every card must have an "Active State" that loops infinitely.
* **Performance:** Perpetual motion MUST be memoized and isolated in its own Client Component.

### 5-Card Archetypes
1. **The Intelligent List** — auto-sorting loop with `layoutId`
2. **The Command Input** — typewriter + processing shimmer
3. **The Live Status** — breathing indicators + overshoot notifications
4. **The Wide Data Stream** — infinite horizontal carousel
5. **The Contextual UI** — staggered highlight + floating toolbar

## 11. FINAL PRE-FLIGHT CHECK
- [ ] Mobile layout collapse guaranteed for high-variance designs
- [ ] Full-height sections use `min-h-[100dvh]`
- [ ] `useEffect` animations contain strict cleanup functions
- [ ] Empty, loading, and error states provided
- [ ] Cards omitted in favor of spacing where possible
- [ ] CPU-heavy perpetual animations isolated in own Client Components
- [ ] `prefers-reduced-motion` respected for all animations
- [ ] Focus indicators visible on all interactive elements
- [ ] Color contrast meets WCAG AA (4.5:1 body, 3:1 large)
