"""Kommandozeilen-Frontend für yt-dlp, spezialisiert auf MP3-Downloads von Playlists."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from . import __version__

REQUIRED_BINARIES: tuple[str, ...] = ("yt-dlp", "ffmpeg")
DEFAULT_OUTPUT_DIR = "downloads"
DEFAULT_TEMPLATE = "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s"


@dataclass(frozen=True)
class Options:
    url: str
    output_dir: Path
    filename_template: str
    cookies_from_browser: str | None
    embed_thumbnail: bool
    dry_run: bool


def parse_args(argv: Sequence[str] | None = None) -> Options:
    parser = argparse.ArgumentParser(
        prog="yt-playlist-mp3",
        description="Lade eine YouTube-Playlist als MP3-Dateien herunter.",
    )
    parser.add_argument("url", help="YouTube-Playlist-URL")
    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Zielordner für Downloads (Standard: %(default)s)",
    )
    parser.add_argument(
        "--filename-template",
        default=DEFAULT_TEMPLATE,
        help="Dateinamen-Template für yt-dlp (Standard: %(default)s)",
    )
    parser.add_argument(
        "--cookies-from-browser",
        metavar="BROWSER",
        help="z. B. 'chrome' oder 'firefox' für private/altersbeschränkte Inhalte",
    )
    parser.add_argument(
        "--no-embed-thumbnail",
        action="store_true",
        help="Thumbnail nicht in die MP3-Datei einbetten",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Zeigt nur den auszuführenden yt-dlp-Befehl an",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    ns = parser.parse_args(argv)
    return Options(
        url=ns.url,
        output_dir=Path(ns.output_dir).expanduser(),
        filename_template=ns.filename_template,
        cookies_from_browser=ns.cookies_from_browser,
        embed_thumbnail=not ns.no_embed_thumbnail,
        dry_run=ns.dry_run,
    )


def find_missing_dependencies(binaries: Sequence[str] = REQUIRED_BINARIES) -> list[str]:
    return [b for b in binaries if shutil.which(b) is None]


def build_command(opts: Options, output_dir: Path) -> list[str]:
    command: list[str] = [
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
        opts.filename_template,
    ]
    if opts.embed_thumbnail:
        command.append("--embed-thumbnail")
    if opts.cookies_from_browser:
        command.extend(["--cookies-from-browser", opts.cookies_from_browser])
    command.append(opts.url)
    return command


def print_missing_dependency_help(missing: Sequence[str]) -> None:
    names = ", ".join(missing)
    print(f"Fehlende Abhängigkeiten: {names}", file=sys.stderr)
    print("", file=sys.stderr)
    print("macOS (Homebrew):", file=sys.stderr)
    print("  brew install yt-dlp ffmpeg", file=sys.stderr)
    print("", file=sys.stderr)
    print("Ubuntu/Debian:", file=sys.stderr)
    print("  sudo apt update && sudo apt install -y yt-dlp ffmpeg", file=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    opts = parse_args(argv)

    missing = find_missing_dependencies()
    if missing:
        print_missing_dependency_help(missing)
        return 1

    output_dir = opts.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    command = build_command(opts, output_dir)
    print("Starte Download:\n")
    print(" ".join(command))
    print("")

    if opts.dry_run:
        return 0

    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
