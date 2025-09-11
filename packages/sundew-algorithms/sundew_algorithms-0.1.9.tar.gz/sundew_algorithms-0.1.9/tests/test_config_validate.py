import pytest

from sundew.config import SundewConfig


def test_invalid_threshold_bounds():
    cfg = SundewConfig(min_threshold=0.8, max_threshold=0.2)
    with pytest.raises(ValueError):
        cfg.validate()


def test_negative_gate_temperature():
    cfg = SundewConfig(gate_temperature=-0.1)
    with pytest.raises(ValueError):
        cfg.validate()


def test_negative_costs_rejected():
    cfg = SundewConfig(eval_cost=-1.0)
    with pytest.raises(ValueError):
        cfg.validate()
