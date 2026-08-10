"""Create a looping animated GIF from birthday-person.jpg."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent
SRC = ROOT / "assets" / "birthday-person.jpg"
OUT = ROOT / "assets" / "birthday-person.gif"


def main() -> None:
    src = Image.open(SRC).convert("RGBA")
    width, height = src.size
    side = min(width, height)
    left = (width - side) // 2 + int(side * 0.02)
    top = max(0, (height - side) // 2 - int(side * 0.08))
    crop = src.crop((left, top, left + side, top + side))

    size = 280
    base = crop.resize((size, size), Image.Resampling.LANCZOS)

    frames = []
    durations = []
    frame_count = 16

    for index in range(frame_count):
        t = index / frame_count
        bounce = math.sin(t * math.pi * 2) * 4
        zoom = 1.04 + 0.03 * math.sin(t * math.pi * 2)
        bright = 1.0 + 0.045 * math.sin(t * math.pi * 2 + 0.4)

        zoomed_size = int(size * zoom)
        frame_img = base.resize((zoomed_size, zoomed_size), Image.Resampling.LANCZOS)
        frame_img = ImageEnhance.Brightness(frame_img).enhance(bright)

        canvas = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        offset_x = (size - zoomed_size) // 2
        offset_y = (size - zoomed_size) // 2 + int(bounce)
        canvas.alpha_composite(frame_img, (offset_x, offset_y))

        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        margin = 6
        draw.ellipse((margin, margin, size - margin, size - margin), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(1.2))

        round_rgba = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        round_rgba.paste(canvas, (0, 0))
        round_rgba.putalpha(mask)

        sparkle = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        sparkle_draw = ImageDraw.Draw(sparkle)
        sparkles = [
            (0.18, 0.22, 3.2),
            (0.82, 0.28, 2.6),
            (0.14, 0.70, 2.4),
            (0.86, 0.68, 3.0),
            (0.50, 0.10, 2.2),
            (0.72, 0.86, 2.0),
        ]
        for sparkle_index, (sx, sy, radius) in enumerate(sparkles):
            phase = t * math.pi * 2 + sparkle_index * 0.9
            alpha = int(90 + 140 * (0.5 + 0.5 * math.sin(phase)))
            current_radius = radius * (
                0.75 + 0.35 * (0.5 + 0.5 * math.sin(phase + 0.5))
            )
            x = sx * size + math.cos(phase) * 3
            y = sy * size + math.sin(phase * 1.3) * 3
            color = (255, 255, 255, alpha)
            sparkle_draw.ellipse(
                (
                    x - current_radius,
                    y - current_radius,
                    x + current_radius,
                    y + current_radius,
                ),
                fill=color,
            )
            sparkle_draw.line(
                (x - current_radius * 2.2, y, x + current_radius * 2.2, y),
                fill=color,
                width=1,
            )
            sparkle_draw.line(
                (x, y - current_radius * 2.2, x, y + current_radius * 2.2),
                fill=color,
                width=1,
            )

        out = Image.alpha_composite(round_rgba, sparkle)
        framed = out.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=192)
        frames.append(framed)
        durations.append(90)

    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Saved {OUT} ({OUT.stat().st_size} bytes), frames={len(frames)}")


if __name__ == "__main__":
    main()
