# Yash Poojary's Teardown Examples

Real examples demonstrating how strategic teardowns translate into building decisions.

## Example 1: ChatGPT macOS App

**Purpose:** Learn how a $100B company builds a Mac chat app

**Findings → Strategic Insight:**
- **LiveKit framework** → They bought real-time voice infrastructure, didn't build it
- **Sparkle framework** → Distributes outside App Store
- **Sentry** → Error tracking outsourced
- **Markdown parsing packages** → Solved problem, don't reinvent

**Takeaway:** Even at $100B, they buy aggressively. Custom effort goes into AI model and UX, not plumbing.

## Example 2: Spotify macOS App

**Purpose:** Understand native vs. web architecture at scale

**Findings → Strategic Insight:**
- **Not native** → Web technology packaged as Mac app
- **Only native: audio framework** → The one thing that MUST be performant
- **Web for everything else** → UI, navigation, playlists, search

**Takeaway:** The 80/20 rule. Identify your "audio equivalent" — the ONE thing that must be native — and use web/off-the-shelf for everything else.

## Example 3: Sparkle File Organizer

**Problem:** Needed duplicate file detection — computationally expensive, technically complex.

**Process:**
1. Found app with duplicate detection feature
2. Tore it down to find the algorithm/package
3. Integrated the package

**Result:** 3 days → 3 hours

**Takeaway:** Before building expensive algorithms, tear down an app that solved it. The package exists.

## Yash's Workflow Pattern

```
1. Identify feature to build
2. Find 1-3 apps with that feature (any category)
3. /teardown each one
4. Extract: packages, patterns, scope implications
5. Save to ./teardowns/ in project repo
6. Reference when building: "How did [App] do [feature]?"
```
