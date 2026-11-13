---
name: algorithmic-art
description: Creates generative and computational art using p5.js with seeded randomness, particle systems, and interactive exploration. Covers creative coding and procedural aesthetics.
---
# Algorithmic Art Creation

Create computational art using p5.js with seeded randomness and interactive exploration.

## Core Process

### Phase 1: Algorithmic Philosophy
Create a manifesto describing the computational aesthetic (4-6 paragraphs):
- Emphasize emergent behavior
- Focus on mathematical beauty
- Express craftsmanship philosophy

### Phase 2: P5.js Implementation
Express the philosophy through a single self-contained HTML artifact.

## Key Principles

**On Craftsmanship:** The algorithm must feel meticulously crafted, refined through countless iterations by someone at the absolute top of their field.

**On Generative Art:** Focus on process over product. Each seed run produces unique outputs. Beauty emerges from algorithmic execution, not static composition.

## Technical Requirements

### Seeded Randomness (Art Blocks Pattern)
```javascript
let seed;

function setup() {
  createCanvas(800, 800);
  seed = parseInt(getURLParams().seed) || floor(random(999999));
  randomSeed(seed);
  noiseSeed(seed);
}
```

### Self-Contained HTML Structure
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>
  <style>
    body { margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #111; }
    canvas { display: block; }
    .controls { position: fixed; bottom: 20px; left: 20px; color: white; font-family: monospace; }
  </style>
</head>
<body>
  <div class="controls">
    <button onclick="prevSeed()">Prev</button>
    <span id="seedDisplay">Seed: 0</span>
    <button onclick="nextSeed()">Next</button>
    <button onclick="randomSeed()">Random</button>
  </div>
  <script>
    // Your generative algorithm here
  </script>
</body>
</html>
```

### Common Generative Techniques

**Particle Systems:**
```javascript
class Particle {
  constructor(x, y) {
    this.pos = createVector(x, y);
    this.vel = p5.Vector.random2D().mult(random(1, 3));
    this.life = 255;
  }

  update() {
    this.pos.add(this.vel);
    this.life -= 2;
  }

  draw() {
    noStroke();
    fill(255, this.life);
    circle(this.pos.x, this.pos.y, 4);
  }
}
```

**Flow Fields:**
```javascript
function flowField(x, y, scale) {
  let angle = noise(x * scale, y * scale) * TWO_PI * 2;
  return p5.Vector.fromAngle(angle);
}
```

**Recursive Subdivision:**
```javascript
function subdivide(x, y, w, h, depth) {
  if (depth === 0 || random() < 0.2) {
    rect(x, y, w, h);
    return;
  }

  if (random() < 0.5) {
    let split = random(0.3, 0.7) * w;
    subdivide(x, y, split, h, depth - 1);
    subdivide(x + split, y, w - split, h, depth - 1);
  } else {
    let split = random(0.3, 0.7) * h;
    subdivide(x, y, w, split, depth - 1);
    subdivide(x, y + split, w, h - split, depth - 1);
  }
}
```

## Color Palettes

```javascript
const palettes = {
  midnight: ['#0d1b2a', '#1b263b', '#415a77', '#778da9', '#e0e1dd'],
  sunset: ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff'],
  forest: ['#2d3436', '#636e72', '#b2bec3', '#dfe6e9', '#00b894'],
  ocean: ['#0a3d62', '#1e5f74', '#289672', '#38ada9', '#82ccdd'],
};
```

## Output

Every artwork produces:
1. Markdown explaining the generative aesthetic philosophy
2. Single HTML artifact containing algorithm, UI, and all functionality

## Source

Adapted from https://github.com/anthropics/skills (Apache-2.0, Copyright 2026 Anthropic, PBC.). Changed for this repo by Lucas Cooper-Bey in 2026: condensed from 302 lines to 111, keeping the two-phase algorithmic philosophy then p5.js flow.
