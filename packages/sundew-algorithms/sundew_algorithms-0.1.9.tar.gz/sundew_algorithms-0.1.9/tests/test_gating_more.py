# tests/test_gating_more.py
from sundew.gating import gate_probability


def test_threshold_equality_boundary():
    # Exactly at threshold:
    assert 0.0 <= gate_probability(0.5, 0.5, 0.1) <= 1.0
    # With temperature=0, equality usually means reject (or defined behavior = 0)
    assert gate_probability(0.5, 0.5, 0.0) in (0.0, 1.0)


def test_extreme_temperatures_clip():
    # Very high temperature should tend towards ~0.5 when sig≈thr
    p = gate_probability(0.5, 0.5, 1e6)
    assert 0.25 < p < 0.75
