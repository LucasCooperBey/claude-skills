---
name: pdf-generation
description: Generates PDFs using Typst templates, handles print layouts, and processes images with Sharp.
---
# PDF Generation Skill

Professional PDF generation patterns using Typst, Puppeteer, and Sharp.

## When This Applies
- Creating or modifying PDF generation code
- Working with Typst templates
- Debugging PDF output issues (text overlap, image sizing, page breaks)
- Implementing print-ready HTML
- Processing images for print (Sharp, EXIF, DPI)

## Quick Reference

See adjacent files:
- `reference.md` - Typst syntax and patterns
- `troubleshooting.md` - Common issues and solutions

## Core Patterns

### 1. Always Escape User Content
```typescript
function escapeTypstString(str: string): string {
  if (!str) return "";
  return str
    .replace(/\\/g, "\\\\")  // Backslash first
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
    .replace(/\n/g, " ")     // Newlines break template
    .replace(/\r/g, "")
    .replace(/\t/g, " ");
}
```

### 2. Constrain Image Dimensions
```typst
// Always specify both width AND height with fit: "contain"
#image("photo.jpg", width: 100%, height: 6in, fit: "contain")
```

### 3. Add Page Break Hints
```typst
// Before potentially tall content
#pagebreak(weak: true)
```

### 4. Use CSS Grid for Complex Layouts (HTML)
```css
.page-one {
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto 1fr auto;
}
```

### 5. Five-Tier PDF Fallback Chain
```
1. Typst WASM (primary - <100ms, professional)
2. Cloud PDF API (optional production fallback)
3. Puppeteer (dev only - system Chrome)
4. Print HTML (universal - works everywhere)
5. Emergency JSON (last resort - manual)
```

## Key Libraries

| Library | Purpose | Notes |
|---------|---------|-------|
| `@myriaddreamin/typst.ts` | Typst WASM compiler | Singleton pattern, dynamic imports |
| `sharp` | Image processing | EXIF rotation, resize, color profiles |
| `puppeteer-core` | PDF rendering from HTML | Dev only, needs Chrome |

### Browser Tool Selection

| Use Case | Tool |
|----------|------|
| **PDF generation from HTML** | Puppeteer (specialized PDF APIs) |
| Testing/verifying PDF output | agent-browser |
| General browser automation | agent-browser |

**Note:** Puppeteer is still preferred for PDF generation because of its specialized `page.pdf()` API with precise control over margins, headers, footers, and print media. Use `agent-browser` for testing and verification.

## Photo Processing Pipeline

```typescript
// 1. Validate: Check data URI format
// 2. Resize: Max 2400px (8" @ 300dpi)
// 3. Fix EXIF: Auto-rotate based on orientation
// 4. Convert: sRGB color profile for print
// 5. Compress: JPEG 90% quality
// 6. Embed: Base64 data URI
```

## Debugging Tips

1. **Enable verbose logging:**
   ```typescript
   generatePdf(data, images, { verbose: true })  // your own PDF function
   ```

2. **Check Typst diagnostics:**
   ```typescript
   generatePdf(data, images, { includeDiagnostics: true })  // your own PDF function
   ```

3. **Common failure patterns:**
   - Empty PDF buffer → Typst syntax error
   - Text overlap → Unescaped special characters
   - Image cutoff → Missing height constraint
   - Sidebar drift → Absolute positioning instead of Grid
