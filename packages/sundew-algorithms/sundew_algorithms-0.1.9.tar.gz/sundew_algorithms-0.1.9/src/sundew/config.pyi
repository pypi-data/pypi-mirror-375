from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

@dataclass
class SundewConfig:
    activation_threshold: float
    target_activation_rate: float
    ema_alpha: float
    adapt_kp: float
    adapt_ki: float
    error_deadband: float
    integral_clamp: float
    min_threshold: float
    max_threshold: float
    energy_pressure: float
    gate_temperature: float
    max_energy: float
    dormant_tick_cost: float
    dormancy_regen: Tuple[float, float]
    eval_cost: float
    base_processing_cost: float
    w_magnitude: float
    w_anomaly: float
    w_context: float
    w_urgency: float
    rng_seed: int
    refractory: int
    probe_every: int

    def __init__(
        self,
        activation_threshold: float = ...,
        target_activation_rate: float = ...,
        ema_alpha: float = ...,
        adapt_kp: float = ...,
        adapt_ki: float = ...,
        error_deadband: float = ...,
        integral_clamp: float = ...,
        min_threshold: float = ...,
        max_threshold: float = ...,
        energy_pressure: float = ...,
        gate_temperature: float = ...,
        max_energy: float = ...,
        dormant_tick_cost: float = ...,
        dormancy_regen: Tuple[float, float] = ...,
        eval_cost: float = ...,
        base_processing_cost: float = ...,
        w_magnitude: float = ...,
        w_anomaly: float = ...,
        w_context: float = ...,
        w_urgency: float = ...,
        rng_seed: int = ...,
        refractory: int = ...,
        probe_every: int = ...,
    ) -> None: ...
    def validate(self) -> None: ...
