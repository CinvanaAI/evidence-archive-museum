"""Validate or build an evidence archive museum."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .archive import load_archive
from .render import render_html, write_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a self-contained evidence archive museum.")
    parser.add_argument("command", choices=("validate", "build"))
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, default=Path("index.html"))
    parser.add_argument("--title", default="Evidence Archive Museum")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    archive = load_archive(args.archive)
    if args.command == "validate":
        print(json.dumps(archive.verification, indent=2))
        return
    output = args.output.resolve()
    if output.exists() and not args.force:
        raise FileExistsError("Output exists; use --force to replace it.")
    write_html(output, render_html(archive, title=args.title))
    print(json.dumps({"status": "complete", "output": str(output), **archive.verification}, indent=2))


if __name__ == "__main__":
    main()
