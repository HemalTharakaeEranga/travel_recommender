from __future__ import annotations
import math
from typing import Sequence

COEF_ = [40, 35, 25]
INTERCEPT_ = 5
DEFAULT_COST = 3000


def _extract_features(dest: dict,
                      pref
                      ) -> Sequence[float]:
    climate_match = 1.0 if dest.get("climate") == pref.climate else 0.0

    hits = sum(tag in dest.get("tags", []) for tag in pref.interests)
    interest_ratio = hits / len(pref.interests) if pref.interests else 0.0

    cost = dest.get("cost", DEFAULT_COST)
    diff_ratio = abs(pref.budget - cost) / pref.budget
    budget_affinity = max(0.0, 1.0 - diff_ratio)

    return climate_match, interest_ratio, budget_affinity


def compute_score(dest: dict, pref) -> int:
    f1, f2, f3 = _extract_features(dest, pref)
    raw = COEF_[0] * f1 + COEF_[1] * f2 + COEF_[2] * f3 + INTERCEPT_
    return max(0, min(100, math.floor(raw)))
