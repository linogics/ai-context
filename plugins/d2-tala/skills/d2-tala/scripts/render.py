#!/usr/bin/env python3
"""Extract every d2 block from Markdown/MDX files and render each one to PNG + SVG with TALA.

Usage: render.py OUT_DIR FILE... [--vars VARS.d2] [--fonts FONT_DIR] [--dark]

Uses the d2 binary when it is on PATH, else the terrastruct/d2 Docker image.
A plain .d2 file is rendered as one block.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BLOCK = re.compile(r"^```d2[^\n]*\n(.*?)^```$", re.S | re.M)
IMAGE = "terrastruct/d2:latest"


def blocks(path: Path) -> list[str]:
    text = path.read_text()

    if path.suffix == ".d2":
        return [text]

    return BLOCK.findall(text)


def d2_cmd(out_dir: Path, extra_mounts: list[Path]) -> list[str]:
    if shutil.which("d2"):
        return ["d2"]

    cmd = ["docker", "run", "--rm", "-u", f"{os.getuid()}:{os.getgid()}", "-v", f"{out_dir}:{out_dir}"]

    for mount in extra_mounts:
        cmd += ["-v", f"{mount}:{mount}:ro"]

    return cmd + [IMAGE]


def font_args(font_dir: Path | None) -> list[str]:
    if not font_dir:
        return []

    args = []

    for kind in ("regular", "italic", "bold", "semibold"):
        found = sorted(font_dir.glob(f"*-{kind.capitalize()}.ttf"))

        if found:
            args += [f"--font-{kind}", str(found[0])]

    return args


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--vars", type=Path, help="d2 text prepended to every block, e.g. theme overrides")
    parser.add_argument("--fonts", type=Path, help="dir with *-Regular.ttf, *-Bold.ttf, ...")
    parser.add_argument("--dark", action="store_true", help="render with dark theme 200")
    args = parser.parse_args()

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    font_dir = args.fonts.resolve() if args.fonts else None
    prefix = args.vars.read_text() + "\n" if args.vars else ""
    mounts = [font_dir] if font_dir else []

    cmd = d2_cmd(out_dir, mounts)
    theme = ["--theme", "200"] if args.dark else ["--theme", "0"]
    failed = 0

    for path in args.files:
        for index, body in enumerate(blocks(path), start=1):
            name = f"{path.parent.name}-{path.stem}-{index}"
            source = out_dir / f"{name}.d2"
            source.write_text(prefix + body)

            for ext in ("svg", "png"):
                target = out_dir / f"{name}.{ext}"
                run = cmd + ["--layout", "tala", "--pad", "20", *theme, *font_args(font_dir), str(source), str(target)]
                result = subprocess.run(run, capture_output=True, text=True)

                if result.returncode != 0:
                    failed += 1
                    print(f"FAIL {path}#{index}: {result.stderr.strip()}", file=sys.stderr)
                    break
            else:
                print(f"ok   {path}#{index} -> {out_dir / name}.png")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
