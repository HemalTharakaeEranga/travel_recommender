from __future__ import annotations
import math


W_CLIMATE = 40
W_INTEREST = 20
W_BUDGET = 25
INTERCEPT = 5


DEFAULT_COST = 3_000


def _budget_score(user_budget: int, dest_cost: int) -> float:

    diff_ratio = abs(user_budget - dest_cost) / user_budget
    return max(0.0, 1.0 - diff_ratio)


def compute_score(dest: dict, pref) -> int:
    climate_pts = W_CLIMATE if dest.get("climate") == pref.climate else 0

    hits = sum(tag in dest.get("tags", []) for tag in pref.interests)
    interest_pts = min(hits * W_INTEREST, 60)

    cost = dest.get("cost", DEFAULT_COST)
    budget_pts = _budget_score(pref.budget, cost) * W_BUDGET

    raw = climate_pts + interest_pts + budget_pts + INTERCEPT
    return max(0, min(100, math.floor(raw)))
