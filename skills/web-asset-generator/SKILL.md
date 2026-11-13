---
name: web-asset-generator
description: Creates web assets including favicons, app icons, Open Graph images, social media cards, and other web graphics from source images or designs.
---
# Web Asset Generator

Generate favicons, app icons, Open Graph images, and social media cards.

## Favicon Generation

### From SVG (Preferred)

```bash
# Install sharp
bun add sharp

# Generate all sizes from SVG
```

```javascript
const sharp = require('sharp');

const sizes = [16, 32, 48, 64, 128, 256];

async function generateFavicons(inputSvg, outputDir) {
  for (const size of sizes) {
    await sharp(inputSvg)
      .resize(size, size)
      .png()
      .toFile(`${outputDir}/favicon-${size}x${size}.png`);
  }

  // Generate ICO (requires additional library)
  // Or use ImageMagick:
  // convert favicon-16x16.png favicon-32x32.png favicon-48x48.png favicon.ico
}
```

### HTML Reference

```html
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
```

## App Icons (PWA)

### Required Sizes

| Size | Purpose |
|------|---------|
| 192x192 | Android home screen |
| 512x512 | Android splash screen |
| 180x180 | iOS home screen |
| 152x152 | iPad |
| 120x120 | iPhone |

```javascript
const appSizes = [72, 96, 120, 128, 144, 152, 180, 192, 384, 512];

async function generateAppIcons(input, outputDir) {
  for (const size of appSizes) {
    await sharp(input)
      .resize(size, size)
      .png()
      .toFile(`${outputDir}/icon-${size}x${size}.png`);
  }
}
```

### Web Manifest

```json
{
  "name": "App Name",
  "short_name": "App",
  "icons": [
    { "src": "/icon-192x192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512x512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#ffffff",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

## Open Graph Images

### Standard Sizes

| Platform | Size | Aspect |
|----------|------|--------|
| Facebook | 1200x630 | 1.91:1 |
| Twitter | 1200x600 | 2:1 |
| LinkedIn | 1200x627 | 1.91:1 |

```javascript
async function generateOGImage(input, outputDir) {
  await sharp(input)
    .resize(1200, 630, { fit: 'cover' })
    .jpeg({ quality: 85 })
    .toFile(`${outputDir}/og-image.jpg`);
}
```

### HTML Meta Tags

```html
<meta property="og:image" content="https://example.com/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://example.com/og-image.jpg">
```

## Creating OG Images with Text

```javascript
const sharp = require('sharp');

async function createOGWithText(title, subtitle, outputPath) {
  const svg = `
    <svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#1a1a2e"/>
      <text x="100" y="280" font-family="Arial" font-size="64" font-weight="bold" fill="white">
        ${escapeXml(title)}
      </text>
      <text x="100" y="360" font-family="Arial" font-size="32" fill="#888">
        ${escapeXml(subtitle)}
      </text>
    </svg>
  `;

  await sharp(Buffer.from(svg))
    .png()
    .toFile(outputPath);
}

function escapeXml(str) {
  return str.replace(/[<>&'"]/g, c => ({
    '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;'
  })[c]);
}
```

## Image Optimization

```javascript
// Optimize for web
await sharp(input)
  .resize(800, 600, { fit: 'inside', withoutEnlargement: true })
  .jpeg({ quality: 80, progressive: true })
  .toFile(output);

// WebP for modern browsers
await sharp(input)
  .webp({ quality: 80 })
  .toFile(output.replace(/\.\w+$/, '.webp'));

// AVIF for cutting-edge compression
await sharp(input)
  .avif({ quality: 60 })
  .toFile(output.replace(/\.\w+$/, '.avif'));
```

## Complete Asset Generation Script

```javascript
async function generateAllAssets(sourceLogo, outputDir) {
  // Favicons
  await generateFavicons(sourceLogo, `${outputDir}/favicons`);

  // App icons
  await generateAppIcons(sourceLogo, `${outputDir}/icons`);

  // OG image (from template)
  await generateOGImage(sourceLogo, `${outputDir}/social`);

  console.log('All assets generated!');
}
```

## Source

Inspired by https://github.com/alonw0/web-asset-generator (MIT, Copyright (c) 2025 Web Asset Generator Contributors).
