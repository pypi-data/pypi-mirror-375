from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .config import SundewConfig

@dataclass
class ProcessingResult:
    activated: bool
    significance: float
    processing_time: float
    energy_consumed: float
    output: Optional[Dict[str, Any]] = ...

@dataclass
class Metrics:
    processed: int
    activated: int
    total_processing_time: float
    energy_used: float
    ema_activation_rate: float

class SundewAlgorithm:
    threshold: float
    metrics: Metrics
    energy: Any

    def __init__(self, cfg: SundewConfig) -> None: ...
    def process(self, event: Dict[str, Any]) -> ProcessingResult | None: ...
    def report(self) -> Dict[str, float | int]: ...
