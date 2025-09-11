# tests/test_cli_cover.py
import importlib
import json
import sys
import types

from sundew.config import SundewConfig


def test_stdout_supports_unicode_false(monkeypatch):
    """
    Force a non-UTF8 stdout encoding so cli._stdout_supports_unicode() returns False.
    This ensures the fallback ASCII symbols are selected and constants are defined.
    """
    fake_stdout = types.SimpleNamespace(encoding="ascii")
    monkeypatch.setattr(sys, "stdout", fake_stdout, raising=True)

    import sundew.cli as cli

    importlib.reload(cli)  # re-evaluate EMOJI_OK and symbol constants

    # We don't care about the exact glyphs; just verify non-empty strings exist.
    assert isinstance(cli.BULLET, str) and cli.BULLET
    assert isinstance(cli.CHECK, str) and cli.CHECK
    assert isinstance(cli.PAUSE, str) and cli.PAUSE
    assert isinstance(cli.FLAG_DONE, str) and cli.FLAG_DONE
    assert isinstance(cli.DISK, str) and cli.DISK


def test_cmd_list_presets_prints(monkeypatch, capsys):
    """
    Verify the list-presets command prints one name per line and exits 0.
    """
    import sundew.cli as cli

    monkeypatch.setattr("sundew.cli.list_presets", lambda: ["tuned_v2", "ecg_mitbih_best"])

    rc = cli.cmd_list_presets(types.SimpleNamespace())
    captured = capsys.readouterr().out.strip().splitlines()

    assert rc == 0
    assert captured == ["tuned_v2", "ecg_mitbih_best"]


def test_cmd_print_config_default(capsys):
    """
    Without a preset, cmd_print_config should serialize a default SundewConfig.
    """
    import sundew.cli as cli

    rc = cli.cmd_print_config(types.SimpleNamespace(preset=""))
    out = capsys.readouterr().out
    data = json.loads(out)

    assert rc == 0
    assert isinstance(data, dict)
    # Spot-check a couple of expected keys to ensure structure looks right.
    assert "min_threshold" in data
    assert "max_threshold" in data


def test_cmd_print_config_with_preset(monkeypatch, capsys):
    """
    With a preset provided, cmd_print_config should serialize the preset config.
    """
    import sundew.cli as cli

    # Return a small custom config to ensure the preset branch is covered
    monkeypatch.setattr(
        "sundew.cli.get_preset",
        lambda name: SundewConfig(min_threshold=0.2, max_threshold=0.9),
    )

    rc = cli.cmd_print_config(types.SimpleNamespace(preset="tuned_v2"))
    out = capsys.readouterr().out
    data = json.loads(out)

    assert rc == 0
    assert data["min_threshold"] == 0.2
    assert data["max_threshold"] == 0.9
