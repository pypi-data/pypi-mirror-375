# tests/test_cli_smoke.py
# import os
import subprocess
import sys


def test_cli_help_runs():
    r = subprocess.run(
        [sys.executable, "-m", "sundew.cli", "--help"], capture_output=True, text=True
    )
    assert r.returncode == 0
    assert "Sundew Algorithm CLI" in r.stdout


def test_cli_list_presets_smoke():
    r = subprocess.run(
        [sys.executable, "-m", "sundew.cli", "list-presets"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert r.stdout.strip()  # prints something
