"""Erlaubt `python -m yt_playlist_mp3 ...`."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
