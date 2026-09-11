"""Kommandozeilen-Frontend für yt-dlp, spezialisiert auf MP3-Downloads von Playlists."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from . import __version__

REQUIRED_BINARIES: tuple[str, ...] = ("yt-dlp", "ffmpeg")
MIN_PYTHON: tuple[int, int] = (3, 9)
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
    interactive: bool = False
    check: bool = False


def parse_args(argv: Sequence[str] | None = None) -> Options:
    parser = argparse.ArgumentParser(
        prog="yt-playlist-mp3",
        description=(
            "Lade eine YouTube-Playlist als MP3-Dateien herunter. "
            "Ohne Argumente startet der geführte interaktive Modus."
        ),
    )
    parser.add_argument("url", nargs="?", help="YouTube-Playlist-URL")
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Geführter Modus: fragt alle Optionen Schritt für Schritt ab",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Prüft Python-Version und externe Tools und beendet sich",
    )
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
    if not ns.url and not (ns.interactive or ns.check):
        parser.error(
            "URL fehlt — ohne Argumente oder mit --interactive startet der geführte Modus."
        )

    return Options(
        url=ns.url or "",
        output_dir=Path(ns.output_dir).expanduser(),
        filename_template=ns.filename_template,
        cookies_from_browser=ns.cookies_from_browser,
        embed_thumbnail=not ns.no_embed_thumbnail,
        dry_run=ns.dry_run,
        interactive=ns.interactive,
        check=ns.check,
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


def print_install_help(stream: TextIO | None = None) -> None:
    out = stream if stream is not None else sys.stderr
    print("So installierst du die Voraussetzungen:", file=out)
    print("", file=out)
    print(f"  Python >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]}", file=out)
    print("    macOS:         brew install python@3.13", file=out)
    print("    Ubuntu/Debian: sudo apt install -y python3", file=out)
    print("", file=out)
    print("  yt-dlp und ffmpeg", file=out)
    print("    macOS:         brew install yt-dlp ffmpeg", file=out)
    print("    Ubuntu/Debian: sudo apt update && sudo apt install -y yt-dlp ffmpeg", file=out)
    print("    plattformweit: pipx install yt-dlp   (ffmpeg separat installieren)", file=out)


def print_missing_dependency_help(missing: Sequence[str]) -> None:
    names = ", ".join(missing)
    print(f"Fehlende Abhängigkeiten: {names}", file=sys.stderr)
    print("", file=sys.stderr)
    print_install_help()


def print_environment_report(stream: TextIO | None = None) -> bool:
    """Listet Python-Version und externe Tools auf. True, wenn alles erfüllt ist."""
    out = stream if stream is not None else sys.stdout
    ok = True

    current = ".".join(str(part) for part in sys.version_info[:3])
    needed = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    if sys.version_info >= MIN_PYTHON:
        print(f"  [OK]    Python {current}", file=out)
    else:
        ok = False
        print(f"  [FEHLT] Python {current} — benötigt wird mindestens {needed}", file=out)

    for binary in REQUIRED_BINARIES:
        path = shutil.which(binary)
        if path:
            print(f"  [OK]    {binary} ({path})", file=out)
        else:
            ok = False
            print(f"  [FEHLT] {binary} — nicht im PATH", file=out)

    if not ok:
        print("", file=out)
        print_install_help(out)
    return ok


def run_download(opts: Options) -> int:
    output_dir = opts.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    command = build_command(opts, output_dir)
    print("Starte Download:\n")
    print(" ".join(command))
    print("")

    if opts.dry_run:
        return 0

    return subprocess.run(command, check=False).returncode


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        args = ["--interactive"]

    opts = parse_args(args)

    if opts.check:
        print("Systemcheck:")
        return 0 if print_environment_report() else 1

    if opts.interactive:
        from .tui import run as run_interactive

        return run_interactive()

    missing = find_missing_dependencies()
    if missing:
        print_missing_dependency_help(missing)
        return 1

    return run_download(opts)


if __name__ == "__main__":
    raise SystemExit(main())
