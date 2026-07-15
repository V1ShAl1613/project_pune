from __future__ import annotations

from typing import Iterable


def clamp_score(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def normalize_codes(values: Iterable[str]) -> list[str]:
    return sorted({str(value).strip() for value in values if str(value).strip()})


def score_percent(total: int, covered: int) -> float:
    if total <= 0:
        return 0.0
    return clamp_score((covered / total) * 100.0)
