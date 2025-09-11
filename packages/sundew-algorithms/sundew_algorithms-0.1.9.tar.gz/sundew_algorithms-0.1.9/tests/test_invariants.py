# tests/test_invariants.py
from hypothesis import given
from hypothesis import strategies as st

from sundew.config import SundewConfig
from sundew.core import SundewAlgorithm

# Build synthetic event dicts matching your core’s expectations
events = st.fixed_dictionaries(
    {
        "magnitude": st.floats(min_value=0, max_value=100),  # core divides by 100
        "anomaly_score": st.floats(min_value=0, max_value=1),
        "context_relevance": st.floats(min_value=0, max_value=1),
        "urgency": st.floats(min_value=0, max_value=1),
    }
)


@given(events)
def test_significance_bounded(ev):
    cfg = SundewConfig()
    algo = SundewAlgorithm(cfg)
    s = algo._compute_significance(ev)  # private-ish, still ok for invariants
    assert 0.0 <= s <= 1.0


def test_threshold_clamped_over_steps():
    cfg = SundewConfig()
    algo = SundewAlgorithm(cfg)
    for _ in range(200):
        algo.process({"magnitude": 0, "anomaly_score": 0, "context_relevance": 0, "urgency": 0})
        assert cfg.min_threshold <= algo.threshold <= cfg.max_threshold
