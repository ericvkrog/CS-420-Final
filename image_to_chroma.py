#!/usr/bin/env python3
"""
ChromaCode Image Interpreter
Reads a horizontal strip of colored squares and outputs a ChromaCode skeleton.

Requires:  pip install Pillow

Usage:
    python image_to_chroma.py <image.png>        # interpret a color strip image
    python image_to_chroma.py --sample           # generate a sample FizzBuzz strip
    python image_to_chroma.py --sample out.png   # save sample to specific path
    python image_to_chroma.py --run <image.png>  # interpret and immediately execute
"""

import sys
import math
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow is required:  pip install Pillow", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────
#  Reference RGB values for each ChromaCode color
# ─────────────────────────────────────────────

CHROMA_COLORS = {
    "BLUE":   (70,  130, 180),
    "GREEN":  (50,  200,  80),
    "YELLOW": (255, 215,   0),
    "PURPLE": (150,   0, 200),
    "RED":    (220,  50,  50),
}

BLOCK_PX = 80   # default block size for generated images


# ─────────────────────────────────────────────
#  Color matching
# ─────────────────────────────────────────────

def _rgb_distance(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def nearest_color(rgb) -> str:
    """Return the ChromaCode color name whose reference RGB is closest to rgb."""
    return min(CHROMA_COLORS, key=lambda name: _rgb_distance(rgb[:3], CHROMA_COLORS[name]))


# ─────────────────────────────────────────────
#  Strip reader
# ─────────────────────────────────────────────

def read_strip(image_path: str) -> list[str]:
    """
    Open a PNG and walk the center row left-to-right.
    Returns an ordered list of ChromaCode color names, one per distinct colored block.
    Skips very dark pixels (separators/background) and pixels too far from any reference color.
    """
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pixels = img.load()
    cy = height // 2

    sequence = []
    prev = None
    for x in range(width):
        r, g, b = pixels[x, cy]
        # Skip dark pixels (separators, background)
        if (r + g + b) / 3 < 40:
            continue
        color = nearest_color((r, g, b))
        # Skip if the pixel isn't close enough to any reference color
        if _rgb_distance((r, g, b), CHROMA_COLORS[color]) > 150:
            continue
        if color != prev:
            sequence.append(color)
            prev = color

    return sequence


# ─────────────────────────────────────────────
#  Skeleton generator
# ─────────────────────────────────────────────

def generate_skeleton(colors: list[str]) -> str:
    """
    Turn a color sequence into indented ChromaCode with ?placeholder expressions.
    The user fills in the ?placeholders before running.
    """
    lines = []
    indent = 0
    # None = no open chain; "if"/"elif" = chain in progress (next YELLOW is elif)
    yellow_state = None
    var_count = 0

    def pad():
        return "  " * indent

    for color in colors:
        if color == "RED":
            indent = max(0, indent - 1)
            lines.append(f"{pad()}RED end")
            yellow_state = None

        elif color == "PURPLE":
            lines.append(f"{pad()}PURPLE for i in 1..10")
            indent += 1
            yellow_state = None

        elif color == "YELLOW":
            if yellow_state is None:
                # Start a fresh if chain
                lines.append(f"{pad()}YELLOW if ?condition:")
                yellow_state = "if"
                indent += 1
            else:
                # Continue chain: step back one level, add elif, step back in
                indent = max(0, indent - 1)
                lines.append(f"{pad()}YELLOW elif ?condition:")
                yellow_state = "elif"
                indent += 1

        elif color == "GREEN":
            lines.append(f"{pad()}GREEN print(?expr)")
            # GREEN is inside a branch — yellow chain stays open for the next YELLOW

        elif color == "BLUE":
            var_count += 1
            lines.append(f"{pad()}BLUE var{var_count} = ?expr")
            yellow_state = None

    return "\n".join(lines)


# ─────────────────────────────────────────────
#  Sample image generator
# ─────────────────────────────────────────────

FIZZBUZZ_STRIP = [
    "PURPLE",           # for i in 1..100
    "YELLOW",           # if i % 15 == 0
    "GREEN",            # print("FizzBuzz")
    "YELLOW",           # elif i % 3 == 0
    "GREEN",            # print("Fizz")
    "YELLOW",           # elif i % 5 == 0
    "GREEN",            # print("Buzz")
    "YELLOW",           # else
    "GREEN",            # print(i)
    "RED",              # end loop
]


def generate_sample_image(path: str = "sample_strip.png",
                           colors: list[str] = None,
                           block_px: int = BLOCK_PX):
    """
    Write a PNG color strip that encodes a ChromaCode program structure.
    Defaults to a FizzBuzz skeleton.
    """
    if colors is None:
        colors = FIZZBUZZ_STRIP

    width = block_px * len(colors)
    img = Image.new("RGB", (width, block_px), (20, 20, 20))
    draw = ImageDraw.Draw(img)

    for i, name in enumerate(colors):
        x0 = i * block_px
        x1 = x0 + block_px
        draw.rectangle([x0, 0, x1 - 1, block_px - 1], fill=CHROMA_COLORS[name])
        draw.line([x0, 0, x0, block_px - 1], fill=(0, 0, 0), width=2)
        # Label each block with the color name in small white text
        try:
            font = ImageFont.load_default(size=10)
        except TypeError:
            font = ImageFont.load_default()
        draw.text((x0 + 4, block_px - 18), name, fill=(255, 255, 255), font=font)

    img.save(path)
    print(f"Saved: {path}  ({len(colors)} blocks: {' → '.join(colors)})")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return

    if args[0] == "--sample":
        out = args[1] if len(args) > 1 else "sample_strip.png"
        generate_sample_image(out)
        colors = FIZZBUZZ_STRIP
        print("\nGenerated skeleton:\n")
        print(generate_skeleton(colors))
        return

    run_mode = False
    image_path = args[0]
    if args[0] == "--run" and len(args) > 1:
        run_mode = True
        image_path = args[1]

    if not Path(image_path).exists():
        print(f"File not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    colors = read_strip(image_path)
    print(f"// Detected: {' → '.join(colors)}\n")
    skeleton = generate_skeleton(colors)
    print(skeleton)

    if run_mode:
        if "?condition" in skeleton or "?expr" in skeleton:
            print("\n// Cannot run: skeleton contains unfilled ?placeholders.", file=sys.stderr)
            sys.exit(1)
        import chromacode
        print("\n// --- Output ---")
        chromacode.interpret_source(skeleton)


if __name__ == "__main__":
    main()
