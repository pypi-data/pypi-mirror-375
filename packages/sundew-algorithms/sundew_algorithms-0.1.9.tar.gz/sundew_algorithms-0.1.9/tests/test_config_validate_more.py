# tests/test_config_validate_more.py
import pytest

from sundew.config import SundewConfig


def test_invalid_alpha_rejected():
    cfg = SundewConfig(ema_alpha=-1.0)
    with pytest.raises(ValueError):
        cfg.validate()


def test_negative_energy_pressure_rejected():
    cfg = SundewConfig(energy_pressure=-0.1)
    with pytest.raises(ValueError):
        cfg.validate()
