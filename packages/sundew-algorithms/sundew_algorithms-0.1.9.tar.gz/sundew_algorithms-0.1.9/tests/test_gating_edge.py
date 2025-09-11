# tests/test_gating_edge.py
from sundew.gating import gate_probability


def test_threshold_and_temp_extremes():
    assert gate_probability(0.9, 0.5, 0.0) == 1.0  # hard gate accept
    assert gate_probability(0.4, 0.5, 0.0) == 0.0  # hard gate reject
    p_eq = gate_probability(0.5, 0.5, 0.1)  # equality at soft gate
    assert 0.0 <= p_eq <= 1.0
    p_hi = gate_probability(0.5, 0.5, 1e6)  # very high temp ~0.5
    assert 0.25 < p_hi < 0.75
