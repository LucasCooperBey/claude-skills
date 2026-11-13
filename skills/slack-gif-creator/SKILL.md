---
name: slack-gif-creator
description: Creates animated GIFs optimized for Slack including emoji animations and message GIFs with proper sizing and frame rates.
---
# Slack GIF Creator

Create animated GIFs optimized for Slack messaging.

## Size Requirements

| Type | Dimensions | Notes |
|------|------------|-------|
| Emoji GIFs | 128x128 px | Keep under 3 seconds |
| Message GIFs | 480x480 px | Larger accepted |
| Frame rate | 10-30 FPS | Lower = smaller file |

## Basic GIF Creation with PIL

```python
from PIL import Image, ImageDraw
import math

def create_pulse_gif(output_path, size=128, frames=20):
    images = []

    for i in range(frames):
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Pulsing circle
        progress = i / frames
        scale = 0.5 + 0.3 * math.sin(progress * 2 * math.pi)
        radius = int(size * scale / 2)
        center = size // 2

        draw.ellipse(
            [center - radius, center - radius,
             center + radius, center + radius],
            fill=(255, 100, 100, 255)
        )
        images.append(img)

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=50,  # ms per frame
        loop=0  # Infinite loop
    )
```

## Common Animation Effects

### Shake/Vibrate
```python
def shake_animation(base_image, frames=10, intensity=5):
    images = []
    for i in range(frames):
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        shifted = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
        shifted.paste(base_image, (offset_x, offset_y))
        images.append(shifted)
    return images
```

### Bounce
```python
def bounce_animation(base_image, frames=20, height=20):
    images = []
    w, h = base_image.size
    for i in range(frames):
        progress = i / frames
        # Easing function for bounce
        y_offset = int(height * abs(math.sin(progress * math.pi)))
        canvas = Image.new('RGBA', (w, h + height), (0, 0, 0, 0))
        canvas.paste(base_image, (0, height - y_offset))
        images.append(canvas)
    return images
```

### Rotation
```python
def rotate_animation(base_image, frames=36):
    images = []
    for i in range(frames):
        angle = (360 / frames) * i
        rotated = base_image.rotate(angle, resample=Image.BICUBIC, expand=False)
        images.append(rotated)
    return images
```

### Fade In/Out
```python
def fade_animation(base_image, frames=20):
    images = []
    for i in range(frames):
        alpha = int(255 * (1 - abs(2 * i / frames - 1)))
        faded = base_image.copy()
        faded.putalpha(alpha)
        images.append(faded)
    return images
```

## Easing Functions

```python
def ease_in_out(t):
    """Smooth start and end"""
    return t * t * (3 - 2 * t)

def ease_bounce(t):
    """Bouncy effect"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2

def ease_elastic(t):
    """Elastic snap"""
    c4 = (2 * math.pi) / 3
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
```

## Optimizing File Size

```python
from PIL import Image

def optimize_gif(input_path, output_path, colors=64):
    img = Image.open(input_path)
    frames = []

    for frame in range(img.n_frames):
        img.seek(frame)
        # Reduce colors
        quantized = img.convert('P', palette=Image.ADAPTIVE, colors=colors)
        frames.append(quantized)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=img.info.get('duration', 50),
        loop=0
    )
```

## Design Tips

- Use thicker lines (2-3px minimum at 128px)
- Layer shapes for depth
- Complementary colors pop in Slack's UI
- Test on both light and dark Slack themes
- Keep animations simple and loopable

## Source

Adapted from https://github.com/anthropics/skills (Apache-2.0, Copyright 2026 Anthropic, PBC.). Changed for this repo by Lucas Cooper-Bey in 2026: constraints rewritten, and the upstream core Python library is not included.
