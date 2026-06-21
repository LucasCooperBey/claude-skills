# PDF Generation Troubleshooting Guide

## Issue: Text Layering / Overlapping

### Symptoms
- Text appears on top of other text
- Content renders behind images
- Layout looks "broken" or scrambled

### Root Causes
1. **Unescaped special characters** in user content
2. **Newlines/tabs** in content breaking template structure
3. **Unclosed content blocks** due to stray `]` in content

### Solutions

```typescript
// ALWAYS escape user content before Typst interpolation
function escapeTypstString(str: string): string {
  if (!str) return "";
  return str
    .replace(/\\/g, "\\\\")  // Backslash first!
    .replace(/"/g, '\\"')
    .replace(/\[/g, "\\[")
    .replace(/\]/g, "\\]")
    .replace(/#/g, "\\#")
    .replace(/\$/g, "\\$")
    .replace(/_/g, "\\_")
    .replace(/\*/g, "\\*")
    .replace(/@/g, "\\@")
    .replace(/</g, "\\<")
    .replace(/>/g, "\\>")
    .replace(/`/g, "\\`")
    .replace(/\n/g, " ")     // Critical: newlines break template
    .replace(/\r/g, "")
    .replace(/\t/g, " ");
}
```

### Test Cases
Always test with content containing:
- Email addresses: `test@example.com`
- Prices: `$500 budget`
- Math: `2 + 2 = 4`
- Brackets: `[See note]`
- Asterisks: `**important**`
- Multi-line text

---

## Issue: Photo Overflow / Cutoff

### Symptoms
- Portrait photos extend beyond page
- Images cut off at page boundary
- Photos overlap with footer

### Root Cause
Only specifying `width` without `height` constraint. A portrait photo at 65% page width can be 7+ inches tall.

### Solution

```typst
// Always constrain BOTH dimensions with fit: "contain"
#image("photo.jpg", width: 65%, height: 6.5in, fit: "contain")
```

```typescript
// In code, add height based on orientation
let maxHeight: string;
if (layout.orientation === "portrait") {
  maxHeight = "6.5in";
} else if (layout.orientation === "square") {
  maxHeight = "5.5in";
} else {
  maxHeight = "5in";
}

// Use Typst's fit parameter
`#image("${path}", width: ${width}, height: ${maxHeight}, fit: "contain")`
```

### Page Break Hint
Add weak page break before large photos:

```typst
#if layout.isLargeFormat [#pagebreak(weak: true)]
```

---

## Issue: Sidebar Positioning (HTML Fallback)

### Symptoms
- Contact sidebar appears on wrong page
- Sidebar drifts when content overflows
- Sidebar hidden behind content

### Root Cause
Absolute positioning (`position: absolute; bottom: 0.5in`) breaks when content overflows the reference element.

### Solution
Use CSS Grid instead:

```css
.page-one {
  display: grid;
  grid-template-columns: 1fr 0.9in;
  grid-template-rows: auto 1fr auto;
}

.main-content {
  grid-column: 1;
  grid-row: 1 / 3;
}

.contact-sidebar {
  grid-column: 2;
  grid-row: 2;
  align-self: end;
  position: static; /* Override absolute */
}

.footer {
  grid-column: 1 / -1;
  grid-row: 3;
}
```

---

## Issue: Page Breaks at Wrong Places

### Symptoms
- Headings orphaned at page bottom
- Single lines isolated on new page
- Sections split awkwardly

### Solutions

**CSS (HTML/Puppeteer):**
```css
section { break-inside: avoid; page-break-inside: avoid; }
h2 { break-after: avoid; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
```

**Typst:**
```typst
// Keep heading with following content
#show heading: it => {
  block(breakable: false)[#it]
}

// Force page break before section
#pagebreak()
```

---

## Issue: Empty PDF Buffer

### Symptoms
- `result.pdf` is empty or null
- Compilation returns no output
- Fallback chain activates

### Debugging

1. **Enable diagnostics:**
   ```typescript
   const result = await generateFieldReportPdf(report, photos, {
     includeDiagnostics: true,
     verbose: true
   });
   console.log(result.diagnostics);
   ```

2. **Check Typst source for syntax errors:**
   - Missing closing brackets `]`
   - Unmatched function calls `#func[`
   - Invalid escape sequences

3. **Common causes:**
   - Unescaped `#` triggers invalid function call
   - Unescaped `$` starts invalid math mode
   - Newline in middle of string interpolation

---

## Issue: Fonts Not Rendering

### Symptoms
- Wrong font in PDF
- Tofu boxes (□□□) instead of characters
- Different font than expected

### Solution

Typst WASM only includes bundled fonts. Use preloading:

```typescript
await compiler.init({
  getModule: () => wasmModule,
  beforeBuild: [
    preloadFontAssets({ assets: ["text"] }),  // LibertinusSerif
    // Optional: preloadFontAssets({ assets: ["cjk", "emoji"] })
  ],
});
```

If you need custom fonts, embed them as shadow files.

---

## Issue: Image Processing Failures

### Symptoms
- Photos appear rotated
- Colors look wrong
- Images too large / slow loading

### Solution: Sharp Pipeline

```typescript
import sharp from 'sharp';

const processed = await sharp(inputBuffer)
  .rotate()                        // Auto-rotate based on EXIF
  .resize(2400, 2400, {           // 8" @ 300dpi
    fit: 'inside',
    withoutEnlargement: true
  })
  .toColorspace('srgb')           // Consistent color for print
  .jpeg({ quality: 90 })
  .toBuffer();
```

---

## Diagnostic Checklist

When PDF generation fails:

1. [ ] Check TypeScript compilation errors
2. [ ] Enable verbose logging
3. [ ] Verify photos have valid data URIs
4. [ ] Look for special characters in content
5. [ ] Check for newlines in text fields
6. [ ] Verify image dimensions
7. [ ] Test with minimal content first
8. [ ] Check circuit breaker status

```typescript
// Quick diagnostic
console.log({
  photos: photos.length,
  validPhotos: photos.filter(p => p.dataUri?.startsWith('data:image/')).length,
  contentLength: JSON.stringify(report).length,
});
```
