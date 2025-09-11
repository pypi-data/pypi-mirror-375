# tests/test_core_branches.py
import numpy as np

from sundew.config_presets import get_preset
from sundew.core import SundewAlgorithm


def tiny_stream(n=200, hi_prob=0.15, seed=123):
    """
    Generates dict events compatible with SundewAlgorithm._compute_significance:
      - magnitude: ~[0,100] (algorithm divides by 100)
      - anomaly_score/context_relevance/urgency: [0,1]
    We create a base low-signal stream with occasional spikes to encourage activations.
    """
    rng = np.random.default_rng(seed)

    # Base “significance driver” in [0,1] with occasional spikes
    base = np.clip(rng.normal(0.10, 0.10, size=n), 0.0, 1.0)
    spikes = rng.random(n) < hi_prob
    base[spikes] = np.clip(base[spikes] + rng.uniform(0.6, 1.0, size=spikes.sum()), 0.0, 1.0)

    # Add a bit of independent noise for the other channels
    ctx_noise = np.clip(base * 0.6 + rng.normal(0.05, 0.05, size=n), 0.0, 1.0)
    urg_noise = np.clip(base * 0.5 + rng.normal(0.05, 0.05, size=n), 0.0, 1.0)

    for i in range(n):
        yield {
            "magnitude": float(base[i] * 100.0),  # ~[0,100]
            "anomaly_score": float(base[i]),  # [0,1]
            "context_relevance": float(ctx_noise[i]),  # [0,1]
            "urgency": float(urg_noise[i]),  # [0,1]
        }


def run_for(cfg, n=200, seed=123):
    """
    Runs n events through the algorithm and returns:
      - activated: count of activations (res != None)
      - energy_spent: derived from algo.report()
    """
    algo = SundewAlgorithm(cfg)
    out = {"activated": 0, "energy_spent": 0.0}

    for ev in tiny_stream(n=n, seed=seed):
        res = algo.process(ev)  # returns ProcessingResult or None
        if res is not None:
            out["activated"] += 1

    rep = algo.report()  # stable API: returns dict with totals & energy
    out["energy_spent"] = float(rep.get("total_energy_spent", 0.0))
    return out


def test_core_energy_pressure_and_gate_paths():
    # Softer gate to exercise gate_temperature path
    cfg = get_preset("tuned_v2", overrides=dict(gate_temperature=0.15, energy_pressure=0.04))
    stats = run_for(cfg, n=300)
    assert stats["activated"] >= 1  # we crossed the gate at least once


def test_core_integral_clamp_and_bounds():
    # Push the controller harder to touch integral clamp / threshold bounds
    cfg = get_preset(
        "tuned_v2",
        overrides=dict(adapt_kp=0.12, adapt_ki=0.05, min_threshold=0.2, max_threshold=0.9),
    )
    stats = run_for(cfg, n=350)
    assert stats["activated"] >= 1


def test_ecg_best_smoke():
    # New frozen preset should instantiate and run
    cfg = get_preset("ecg_mitbih_best")
    stats = run_for(cfg, n=200)
    # smoke: main loop executes without raising and returns a dict
    assert isinstance(stats, dict)
    assert stats["activated"] >= 0
