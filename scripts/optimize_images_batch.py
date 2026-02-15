#!/usr/bin/env python3
import subprocess
from pathlib import Path

from optimize_image import optimize_image


def changed_images() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            check=True,
            capture_output=True,
            text=True,
        )
        files = result.stdout.strip().splitlines()
    except subprocess.CalledProcessError:
        files = []
    image_ext = {".jpg", ".jpeg", ".png"}
    return [Path(f) for f in files if Path(f).suffix.lower() in image_ext]


def main() -> None:
    inputs = changed_images()
    if not inputs:
        return
    for path in inputs:
        if not path.exists():
            continue
        optimize_image(path, Path("assets/images"), max_width=1200, quality=82)


if __name__ == "__main__":
    main()
