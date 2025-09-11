# tests/test_gating_boundaries.py
from sundew.gating import gate_probability


def test_boundaries_and_extremes():
    # equality at threshold should be defined and bounded
    assert 0.0 <= gate_probability(0.5, 0.5, 0.1) <= 1.0
    # hard gate edge cases
    assert gate_probability(0.5, 0.5, 0.0) in (0.0, 1.0)
    # extremely high temperature tends ~0.5 near threshold
    p = gate_probability(0.5, 0.5, 1e6)
    assert 0.25 < p < 0.75
