from sundew.gating import gate_probability


def test_hard_gate_temperature_zero():
    # With temperature=0, the gate should behave deterministically
    assert gate_probability(0.9, 0.5, 0.0) == 1.0
    assert gate_probability(0.4, 0.5, 0.0) == 0.0


def test_soft_gate_monotonic():
    t = 0.1
    p1 = gate_probability(0.45, 0.5, t)
    p2 = gate_probability(0.50, 0.5, t)
    p3 = gate_probability(0.55, 0.5, t)
    # Probabilities should increase as sig surpasses the threshold
    assert 0.0 <= p1 < p2 < p3 <= 1.0
