"""yt-playlist-mp3 — Lade YouTube-Playlists als MP3 herunter."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("yt-playlist-mp3")
except PackageNotFoundError:
    __version__ = "0.0.0+local"

__all__ = ["__version__"]
