# src/sundew/cli.py
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict

from . import get_preset, list_presets
from .config import SundewConfig
from .core import ProcessingResult, SundewAlgorithm
from .demo import synth_event


def _stdout_supports_unicode() -> bool:
    enc = getattr(sys.stdout, "encoding", None) or ""
    try:
        "🌿".encode(enc or "utf-8", errors="strict")
        return True
    except Exception:
        return False


EMOJI_OK = _stdout_supports_unicode()
BULLET = "🌿" if EMOJI_OK else "[sundew]"
CHECK = "✅" if EMOJI_OK else "[ok]"
PAUSE = "⏸" if EMOJI_OK else "[idle]"
FLAG_DONE = "🏁" if EMOJI_OK else "[done]"
DISK = "💾" if EMOJI_OK else "[saved]"


def _energy_float(algo: SundewAlgorithm) -> float:
    e = getattr(algo, "energy", 0.0)
    v = getattr(e, "value", e)
    try:
        return float(v)
    except Exception:
        return 0.0


def _to_plain(obj: object) -> Dict[str, Any]:
    """
    Dataclass-safe serializer (works with slots=True).
    Falls back to __dict__ if not a dataclass.
    """
    if is_dataclass(obj):
        return asdict(obj)  # type: ignore[arg-type]
    d = getattr(obj, "__dict__", {})
    return dict(d) if isinstance(d, dict) else {}


def cmd_list_presets(_: argparse.Namespace) -> int:
    for p in list_presets():
        print(p)
    return 0


def cmd_print_config(ns: argparse.Namespace) -> int:
    cfg: SundewConfig = get_preset(ns.preset) if ns.preset else SundewConfig()
    print(json.dumps(_to_plain(cfg), indent=2))
    return 0


def cmd_demo(ns: argparse.Namespace) -> int:  # pragma: no cover
    """
    Inline demo (interactive printout) with optional save.
    """
    cfg = SundewConfig(gate_temperature=ns.temperature)
    algo = SundewAlgorithm(cfg)

    print(f"{BULLET} Sundew Algorithm — Demo")
    print("=" * 60)
    print(f"Initial threshold: {algo.threshold:.3f} | Energy: {_energy_float(algo):.1f}\n")

    processed: list[ProcessingResult] = []
    for i in range(ns.events):
        x = synth_event(i)
        res = algo.process(x)
        if res is None:
            print(
                f"{i + 1:02d}. {x['type']:<15} {PAUSE} dormant "
                f"| energy {_energy_float(algo):6.1f} | thr {algo.threshold:.3f}"
            )
        else:
            processed.append(res)
            print(
                f"{i + 1:02d}. {x['type']:<15} {CHECK} processed "
                f"(sig={res.significance:.3f}, {res.processing_time:.3f}s, ΔE≈{res.energy_consumed:.1f}) "
                f"| energy {_energy_float(algo):6.1f} | thr {algo.threshold:.3f}"
            )

    print(f"\n{FLAG_DONE} Final Report")
    report = algo.report()
    for k, v in report.items():
        if isinstance(v, float):
            if "pct" in k:
                print(f"  {k:30s}: {v:7.2f}%")
            else:
                print(f"  {k:30s}: {v:10.3f}")
        else:
            print(f"  {k:30s}: {v}")

    if ns.save:
        out = {
            "config": _to_plain(cfg),
            "report": report,
            "processed_events": [_to_plain(r) for r in processed],
        }
        path = Path(ns.save)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"\n{DISK} Results saved to {path}")

    return 0


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    """
    Sundew Algorithm CLI entrypoint.
    Tests look for 'Sundew Algorithm CLI' or 'Sundew Algorithm' in help text.
    """
    ap = argparse.ArgumentParser(description="Sundew Algorithm CLI")
    sub = ap.add_subparsers(dest="cmd")

    # list-presets
    ap_list = sub.add_parser("list-presets", help="List available configuration presets")
    ap_list.set_defaults(func=cmd_list_presets)

    # print-config
    ap_print = sub.add_parser("print-config", help="Print a preset config as JSON")
    ap_print.add_argument(
        "--preset", type=str, default="", help="Preset name (default: inline defaults)"
    )
    ap_print.set_defaults(func=cmd_print_config)

    # demo flags (top-level shortcut)
    ap.add_argument(
        "--demo",
        action="store_true",
        help="Run the interactive demo (shortcut without subcommand)",
    )
    ap.add_argument("--events", type=int, default=40, help="Number of demo events")
    ap.add_argument("--temperature", type=float, default=0.1, help="Gating temperature (0=hard)")
    ap.add_argument("--save", type=str, default="", help="Optional path to save demo results JSON")

    # demo subcommand (explicit)
    ap_demo = sub.add_parser("demo", help="Run the interactive demo")
    ap_demo.add_argument("--events", type=int, default=40)
    ap_demo.add_argument("--temperature", type=float, default=0.1)
    ap_demo.add_argument("--save", type=str, default="")
    ap_demo.set_defaults(func=cmd_demo)

    ns = ap.parse_args(argv)

    if ns.cmd in ("list-presets", "print-config"):
        return ns.func(ns)

    if ns.cmd == "demo" or getattr(ns, "demo", False):
        # Support both `sundew demo` and `sundew --demo`
        return cmd_demo(ns)

    # No subcommand → print help and exit 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
