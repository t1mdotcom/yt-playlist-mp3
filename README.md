# yt-playlist-mp3

[![CI](https://github.com/t1mdotcom/Youtube-Playlist-MP3-Download/actions/workflows/ci.yml/badge.svg)](https://github.com/t1mdotcom/Youtube-Playlist-MP3-Download/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Schlanker CLI-Wrapper um [`yt-dlp`](https://github.com/yt-dlp/yt-dlp), der eine ganze YouTube-Playlist als MP3-Dateien herunterlädt — inklusive Metadaten und eingebettetem Thumbnail.

```text
$ yt-playlist-mp3 "https://www.youtube.com/playlist?list=PL..."

Starte Download:

yt-dlp --yes-playlist --ignore-errors --continue --no-overwrites --extract-audio
       --audio-format mp3 --audio-quality 0 --add-metadata --embed-metadata
       --paths downloads -o "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s"
       --embed-thumbnail "https://www.youtube.com/playlist?list=PL..."

[download] Playlist Beispiel: Downloading 12 items …
```

## Features

- **Best-Quality MP3** (`--audio-quality 0`) direkt aus dem besten verfügbaren Audio-Stream
- **Playlist-Ordner** und nummerierte Tracks via Default-Template
- **Metadaten + Thumbnail** in jede MP3-Datei eingebettet (`--add-metadata`, `--embed-thumbnail`)
- **Resume-fähig** dank `--continue` und `--no-overwrites`
- **Browser-Cookies** für private oder altersbeschränkte Inhalte (`--cookies-from-browser`)
- **`--dry-run`** zeigt den `yt-dlp`-Befehl, ohne ihn auszuführen
- **Klare Fehlermeldungen** wenn `yt-dlp` oder `ffmpeg` fehlen

## Installation

### Systemvoraussetzungen

`yt-dlp` und `ffmpeg` müssen im `PATH` liegen:

```bash
# macOS
brew install yt-dlp ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install -y yt-dlp ffmpeg
```

### Aus dem Repo

```bash
git clone https://github.com/t1mdotcom/Youtube-Playlist-MP3-Download.git
cd Youtube-Playlist-MP3-Download
pip install .
```

Oder direkt mit [`pipx`](https://pipx.pypa.io/):

```bash
pipx install git+https://github.com/t1mdotcom/Youtube-Playlist-MP3-Download.git
```

## Verwendung

```bash
yt-playlist-mp3 "https://www.youtube.com/playlist?list=DEINE_PLAYLIST_ID"
```

Eigener Zielordner:

```bash
yt-playlist-mp3 "https://www.youtube.com/playlist?list=..." -o ~/Music/youtube
```

Nur den Befehl anzeigen (ohne Download):

```bash
yt-playlist-mp3 "https://www.youtube.com/playlist?list=..." --dry-run
```

Mit Browser-Cookies für private Playlists:

```bash
yt-playlist-mp3 "https://www.youtube.com/playlist?list=..." --cookies-from-browser firefox
```

Auch als Modul aufrufbar:

```bash
python -m yt_playlist_mp3 "https://www.youtube.com/playlist?list=..."
```

### Optionen

| Flag                          | Standard                                                         | Beschreibung                                            |
| ----------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------- |
| `url` *(positional)*          | —                                                                | YouTube-Playlist-URL                                    |
| `-o`, `--output-dir`          | `downloads`                                                      | Zielordner für die Downloads                            |
| `--filename-template`         | `%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s`    | `yt-dlp`-Output-Template                                |
| `--cookies-from-browser`      | —                                                                | Browser für Cookies (`chrome`, `firefox`, …)            |
| `--no-embed-thumbnail`        | *aus*                                                            | Thumbnail nicht in die MP3 einbetten                    |
| `--dry-run`                   | *aus*                                                            | Nur Befehl anzeigen, nichts herunterladen               |
| `-V`, `--version`             | —                                                                | Version ausgeben                                        |

## Entwicklung

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

ruff check .
pytest
```

### Projektstruktur

```
.
├── src/yt_playlist_mp3/
│   ├── __init__.py        # Package + Version
│   ├── __main__.py        # python -m yt_playlist_mp3
│   └── cli.py             # Argument-Parsing, Command-Bau, Entry-Point
├── tests/
│   └── test_cli.py        # pytest
├── .github/
│   ├── workflows/ci.yml   # Lint + Tests auf 3.9–3.13 (Linux + macOS)
│   ├── ISSUE_TEMPLATE/    # Bug + Feature
│   └── dependabot.yml
├── pyproject.toml
├── LICENSE
└── README.md
```

CI läuft auf Ubuntu **und** macOS gegen Python 3.9 bis 3.13.

## Troubleshooting

**`Fehlende Abhängigkeiten: yt-dlp` / `ffmpeg`**
Eines der externen Tools liegt nicht im `PATH`. Installation siehe oben.

**`HTTP Error 403` oder `Sign in to confirm`**
Playlist ist privat oder altersbeschränkt. `--cookies-from-browser firefox` (oder ein anderer Browser, in dem du eingeloggt bist) hilft.

**`ERROR: unable to download video data`**
Meist eine `yt-dlp`-Version, die hinter Änderungen auf YouTube hinterherhinkt. Aktualisieren:

```bash
yt-dlp -U          # oder:
pipx upgrade yt-dlp
```

## Lizenz

[MIT](LICENSE)
