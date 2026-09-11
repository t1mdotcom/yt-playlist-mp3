"""Tests für den interaktiven Modus und den Systemcheck."""

from __future__ import annotations

from pathlib import Path

import pytest

from yt_playlist_mp3 import cli, tui

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLtest"


@pytest.fixture
def answers(monkeypatch: pytest.MonkeyPatch):
    """Speist eine Liste von Eingaben in input() ein."""

    def _feed(values: list[str]) -> None:
        it = iter(values)
        monkeypatch.setattr("builtins.input", lambda _prompt="": next(it))

    return _feed


def test_ask_uses_default(answers) -> None:
    answers([""])
    assert tui.ask("Zielordner", "downloads") == "downloads"


def test_ask_repeats_until_non_empty(answers) -> None:
    answers(["", "  ", "wert"])
    assert tui.ask("Pflichtfeld") == "wert"


def test_ask_yes_no_variants(answers) -> None:
    answers(["", "ja", "N", "quatsch", "y"])
    assert tui.ask_yes_no("?", True) is True
    assert tui.ask_yes_no("?", False) is True
    assert tui.ask_yes_no("?", True) is False
    assert tui.ask_yes_no("?", True) is True  # überspringt "quatsch"


def test_ask_optional_empty_is_none(answers) -> None:
    answers([" "])
    assert tui.ask_optional("Cookies") is None


def test_collect_options_maps_answers(answers, tmp_path: Path) -> None:
    answers([PLAYLIST_URL, str(tmp_path), "n", "firefox", "", "j"])
    opts = tui.collect_options()

    assert opts.url == PLAYLIST_URL
    assert opts.output_dir == tmp_path
    assert opts.embed_thumbnail is False
    assert opts.cookies_from_browser == "firefox"
    assert opts.filename_template == cli.DEFAULT_TEMPLATE
    assert opts.dry_run is True


def test_run_requires_tty(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(tui.sys.stdin, "isatty", lambda: False)

    assert tui.run() == 2
    assert "--help" in capsys.readouterr().err


def test_run_aborts_when_environment_incomplete(
    monkeypatch: pytest.MonkeyPatch, answers
) -> None:
    monkeypatch.setattr(tui.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(tui, "print_environment_report", lambda *_a, **_kw: False)
    answers([])

    assert tui.run() == 1


def test_run_happy_path(monkeypatch: pytest.MonkeyPatch, answers, tmp_path: Path) -> None:
    monkeypatch.setattr(tui.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(tui, "print_environment_report", lambda *_a, **_kw: True)

    captured: dict[str, cli.Options] = {}

    def fake_download(opts: cli.Options) -> int:
        captured["opts"] = opts
        return 0

    monkeypatch.setattr(tui, "run_download", fake_download)

    answers([PLAYLIST_URL, str(tmp_path), "", "", "", "", ""])

    assert tui.run() == 0
    assert captured["opts"].url == PLAYLIST_URL
    assert captured["opts"].embed_thumbnail is True


def test_run_cancelled_at_confirmation(
    monkeypatch: pytest.MonkeyPatch, answers, tmp_path: Path
) -> None:
    monkeypatch.setattr(tui.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(tui, "print_environment_report", lambda *_a, **_kw: True)
    monkeypatch.setattr(tui, "run_download", lambda _opts: pytest.fail("darf nicht laufen"))

    answers([PLAYLIST_URL, str(tmp_path), "", "", "", "", "n"])

    assert tui.run() == 0


def test_run_handles_ctrl_c(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tui.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(tui, "print_environment_report", lambda *_a, **_kw: True)

    def boom(_prompt: str = "") -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", boom)

    assert tui.run() == 130


def test_main_without_args_starts_interactive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.sys, "argv", ["yt-playlist-mp3"])
    monkeypatch.setattr(tui, "run", lambda: 42)

    assert cli.main() == 42


def test_check_reports_missing_binary(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.shutil, "which", lambda _name: None)

    rc = cli.main(["--check"])
    out = capsys.readouterr().out

    assert rc == 1
    assert "[FEHLT] yt-dlp" in out
    assert "brew install yt-dlp ffmpeg" in out


def test_check_ok_when_everything_present(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.shutil, "which", lambda _name: "/usr/bin/fake")

    rc = cli.main(["--check"])
    out = capsys.readouterr().out

    assert rc == 0
    assert "[FEHLT]" not in out


def test_environment_report_flags_old_python(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.shutil, "which", lambda _name: "/usr/bin/fake")
    monkeypatch.setattr(cli, "MIN_PYTHON", (99, 0))

    assert cli.print_environment_report() is False
    assert "benötigt wird mindestens 99.0" in capsys.readouterr().out
