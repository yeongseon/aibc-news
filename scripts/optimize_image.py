#!/usr/bin/env python3
import argparse
from pathlib import Path
from PIL import Image


def optimize_image(input_path: Path, output_dir: Path, *, max_width: int, quality: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(input_path)
    img = img.convert("RGB")

    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    output_path = output_dir / (input_path.stem + ".webp")
    img.save(output_path, "WEBP", quality=quality, method=6)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to source image")
    parser.add_argument("--output-dir", default="assets/images", help="Output directory")
    parser.add_argument("--max-width", type=int, default=1200)
    parser.add_argument("--quality", type=int, default=82)
    args = parser.parse_args()

    output = optimize_image(
        Path(args.input),
        Path(args.output_dir),
        max_width=args.max_width,
        quality=args.quality,
    )
    print(f"Saved: {output}")
    print(f"Use in front matter: image: /{output.as_posix()}")


if __name__ == "__main__":
    main()
