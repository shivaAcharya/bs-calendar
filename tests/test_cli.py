"""Unit tests for bs_calendar CLI interface."""

from pathlib import Path
import pytest
from bs_calendar.cli import main


def test_cli_generate_command(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    exit_code = main(["generate", "--years", "1", "--start-year", "2082", "--out", str(out_dir), "--quiet"])
    assert exit_code == 0

    en_file = out_dir / "bs-calendar-en.ics"
    ne_file = out_dir / "bs-calendar-ne.ics"
    html_file = out_dir / "index.html"

    assert en_file.is_file()
    assert ne_file.is_file()
    assert html_file.is_file()

    assert en_file.stat().st_size > 0
    assert ne_file.stat().st_size > 0
    assert "Bikram Sambat" in html_file.read_text(encoding="utf-8")


def test_cli_direct_args_without_subcommand(tmp_path: Path) -> None:
    out_dir = tmp_path / "out_direct"
    exit_code = main(["--years", "1", "--start-year", "2082", "--out", str(out_dir), "-q"])
    assert exit_code == 0
    assert (out_dir / "bs-calendar-en.ics").is_file()


def test_cli_out_of_range_error(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    out_dir = tmp_path / "out_err"
    exit_code = main(["generate", "--start-year", "2150", "--out", str(out_dir)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "out of supported bounds" in captured.err


def test_cli_invalid_years(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    out_dir = tmp_path / "out_err"
    exit_code = main(["generate", "--years", "0", "--out", str(out_dir)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "--years must be at least 1" in captured.err
