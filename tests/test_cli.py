"""Tests für yt_playlist_mp3.cli."""

from __future__ import annotations

from pathlib import Path

import pytest

from yt_playlist_mp3 import cli

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLtest"


def test_parse_args_defaults() -> None:
    opts = cli.parse_args([PLAYLIST_URL])

    assert opts.url == PLAYLIST_URL
    assert opts.output_dir == Path(cli.DEFAULT_OUTPUT_DIR).expanduser()
    assert opts.filename_template == cli.DEFAULT_TEMPLATE
    assert opts.cookies_from_browser is None
    assert opts.embed_thumbnail is True
    assert opts.dry_run is False


def test_parse_args_overrides(tmp_path: Path) -> None:
    opts = cli.parse_args(
        [
            PLAYLIST_URL,
            "-o",
            str(tmp_path),
            "--filename-template",
            "%(title)s.%(ext)s",
            "--cookies-from-browser",
            "firefox",
            "--no-embed-thumbnail",
            "--dry-run",
        ]
    )

    assert opts.output_dir == tmp_path
    assert opts.filename_template == "%(title)s.%(ext)s"
    assert opts.cookies_from_browser == "firefox"
    assert opts.embed_thumbnail is False
    assert opts.dry_run is True


def test_parse_args_requires_url() -> None:
    with pytest.raises(SystemExit):
        cli.parse_args([])


def test_build_command_default(tmp_path: Path) -> None:
    opts = cli.parse_args([PLAYLIST_URL])
    cmd = cli.build_command(opts, tmp_path)

    assert cmd[0] == "yt-dlp"
    assert cmd[-1] == PLAYLIST_URL
    assert "--extract-audio" in cmd
    assert "--audio-format" in cmd and cmd[cmd.index("--audio-format") + 1] == "mp3"
    assert "--paths" in cmd and cmd[cmd.index("--paths") + 1] == str(tmp_path)
    assert "--embed-thumbnail" in cmd
    assert "--cookies-from-browser" not in cmd


def test_build_command_without_thumbnail_and_with_cookies(tmp_path: Path) -> None:
    opts = cli.parse_args(
        [PLAYLIST_URL, "--no-embed-thumbnail", "--cookies-from-browser", "chrome"]
    )
    cmd = cli.build_command(opts, tmp_path)

    assert "--embed-thumbnail" not in cmd
    idx = cmd.index("--cookies-from-browser")
    assert cmd[idx + 1] == "chrome"


def test_find_missing_dependencies_all_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.shutil, "which", lambda _: "/usr/bin/fake")
    assert cli.find_missing_dependencies(("yt-dlp", "ffmpeg")) == []


def test_find_missing_dependencies_partial(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cli.shutil, "which", lambda name: "/usr/bin/yt-dlp" if name == "yt-dlp" else None
    )
    assert cli.find_missing_dependencies(("yt-dlp", "ffmpeg")) == ["ffmpeg"]


def test_main_reports_missing_dependencies(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "find_missing_dependencies", lambda *_a, **_kw: ["yt-dlp"])
    rc = cli.main([PLAYLIST_URL])

    captured = capsys.readouterr()
    assert rc == 1
    assert "yt-dlp" in captured.err


def test_main_dry_run_skips_subprocess(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "find_missing_dependencies", lambda *_a, **_kw: [])

    called: dict[str, bool] = {"ran": False}

    def fake_run(*_a, **_kw):  # pragma: no cover — should not run in dry-run
        called["ran"] = True

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    rc = cli.main([PLAYLIST_URL, "-o", str(tmp_path), "--dry-run"])
    out = capsys.readouterr().out

    assert rc == 0
    assert called["ran"] is False
    assert "yt-dlp" in out
    assert PLAYLIST_URL in out
