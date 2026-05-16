#!/usr/bin/env python3
"""Download an entire YouTube playlist as MP3 files."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lade eine YouTube-Playlist als MP3-Dateien herunter."
    )
    parser.add_argument("url", help="YouTube-Playlist-URL")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="downloads",
        help="Zielordner fuer Downloads (Standard: downloads)",
    )
    parser.add_argument(
        "--filename-template",
        default="%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s",
        help=(
            "Dateinamen-Template fuer yt-dlp "
            "(Standard: %%(playlist_title)s/%%(playlist_index)03d - %%(title)s.%%(ext)s)"
        ),
    )
    parser.add_argument(
        "--cookies-from-browser",
        help="Optional, z. B. chrome oder firefox fuer private/age-restricted Inhalte",
    )
    parser.add_argument(
        "--no-embed-thumbnail",
        action="store_true",
        help="Thumbnail nicht in die MP3-Datei einbetten",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Zeigt nur den auszufuehrenden yt-dlp-Befehl an",
    )
    return parser.parse_args()


def validate_dependencies() -> list[str]:
    missing = []
    for binary in ("yt-dlp", "ffmpeg"):
        if shutil.which(binary) is None:
            missing.append(binary)
    return missing


def build_command(args: argparse.Namespace, output_dir: Path) -> list[str]:
    command = [
        "yt-dlp",
        "--yes-playlist",
        "--ignore-errors",
        "--continue",
        "--no-overwrites",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--add-metadata",
        "--embed-metadata",
        "--paths",
        str(output_dir),
        "-o",
        args.filename_template,
    ]
    if not args.no_embed_thumbnail:
        command.append("--embed-thumbnail")
    if args.cookies_from_browser:
        command.extend(["--cookies-from-browser", args.cookies_from_browser])
    command.append(args.url)
    return command


def print_missing_dependency_help(missing: list[str]) -> None:
    names = ", ".join(missing)
    print(f"Fehlende Abhaengigkeiten: {names}", file=sys.stderr)
    print("", file=sys.stderr)
    print("macOS (Homebrew):", file=sys.stderr)
    print("  brew install yt-dlp ffmpeg", file=sys.stderr)
    print("", file=sys.stderr)
    print("Ubuntu/Debian:", file=sys.stderr)
    print("  sudo apt update && sudo apt install -y yt-dlp ffmpeg", file=sys.stderr)


def main() -> int:
    args = parse_args()
    missing = validate_dependencies()
    if missing:
        print_missing_dependency_help(missing)
        return 1
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    command = build_command(args, output_dir)
    print("Starte Download:\n")
    print(" ".join(command))
    print("")
    if args.dry_run:
        return 0
    process = subprocess.run(command, check=False)
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
