# YouTube Playlist MP3 Downloader

Kleine CLI-Anwendung, um eine komplette YouTube-Playlist als MP3-Dateien herunterzuladen.

## Voraussetzungen

- `yt-dlp`
- `ffmpeg`
- Python 3.9+

Beispielinstallation auf macOS:

```bash
brew install yt-dlp ffmpeg
```

## Verwendung

```bash
./yt_playlist_mp3.py "https://www.youtube.com/playlist?list=DEINE_PLAYLIST_ID"
```

Optional mit Zielordner:

```bash
./yt_playlist_mp3.py "https://www.youtube.com/playlist?list=DEINE_PLAYLIST_ID" -o musik
```

Nur Befehl anzeigen (ohne Download):

```bash
./yt_playlist_mp3.py "https://www.youtube.com/playlist?list=DEINE_PLAYLIST_ID" --dry-run
```

Weitere Optionen:

```bash
./yt_playlist_mp3.py --help
```
