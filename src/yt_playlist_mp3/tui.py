"""Geführter interaktiver Modus: fragt alle Optionen Schritt für Schritt ab."""

from __future__ import annotations

import sys
from pathlib import Path

from . import __version__
from .cli import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TEMPLATE,
    Options,
    print_environment_report,
    run_download,
)

RULE = "─" * 62
YES = ("j", "ja", "y", "yes")
NO = ("n", "nein", "no")


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        answer = input(f"{prompt}{suffix}: ").strip()
        if answer:
            return answer
        if default:
            return default
        print("  Eingabe erforderlich.")


def ask_optional(prompt: str) -> str | None:
    return input(f"{prompt}: ").strip() or None


def ask_yes_no(prompt: str, default: bool) -> bool:
    hint = "J/n" if default else "j/N"
    while True:
        answer = input(f"{prompt} [{hint}]: ").strip().lower()
        if not answer:
            return default
        if answer in YES:
            return True
        if answer in NO:
            return False
        print("  Bitte j oder n eingeben.")


def collect_options() -> Options:
    url = ask("Playlist- oder Video-URL")
    output_dir = ask("Zielordner", DEFAULT_OUTPUT_DIR)
    embed_thumbnail = ask_yes_no("Thumbnail in die MP3 einbetten?", True)
    cookies = ask_optional("Cookies aus Browser (leer = keine, z. B. chrome/firefox)")
    template = ask("Dateinamen-Template", DEFAULT_TEMPLATE)
    dry_run = ask_yes_no("Nur den yt-dlp-Befehl anzeigen (dry-run)?", False)
    return Options(
        url=url,
        output_dir=Path(output_dir).expanduser(),
        filename_template=template,
        cookies_from_browser=cookies,
        embed_thumbnail=embed_thumbnail,
        dry_run=dry_run,
    )


def print_summary(opts: Options) -> None:
    print(RULE)
    print("  Zusammenfassung")
    print(RULE)
    print(f"  URL:        {opts.url}")
    print(f"  Zielordner: {opts.output_dir}")
    print(f"  Template:   {opts.filename_template}")
    print(f"  Thumbnail:  {'ja' if opts.embed_thumbnail else 'nein'}")
    print(f"  Cookies:    {opts.cookies_from_browser or '—'}")
    print(f"  Dry-Run:    {'ja' if opts.dry_run else 'nein'}")
    print(RULE)
    print("")


def run() -> int:
    if not sys.stdin.isatty():
        print("Interaktiver Modus braucht ein Terminal (stdin ist kein TTY).", file=sys.stderr)
        print("Stattdessen: yt-playlist-mp3 <URL> [Optionen] — Hilfe mit --help", file=sys.stderr)
        return 2

    print(RULE)
    print(f"  yt-playlist-mp3 {__version__} — interaktiver Modus")
    print(RULE)
    print("")
    print("Systemcheck:")
    if not print_environment_report():
        return 1
    print("")
    print("Abbruch jederzeit mit Strg-C.")
    print("")

    try:
        opts = collect_options()
        print("")
        print_summary(opts)
        if not ask_yes_no("Jetzt starten?", True):
            print("Abgebrochen.")
            return 0
    except (EOFError, KeyboardInterrupt):
        print("\nAbgebrochen.")
        return 130

    print("")
    return run_download(opts)
