import json
import logging
from pathlib import Path
from typing import List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, conint

from .model_api import compute_score

logger = logging.getLogger(__name__)
router = APIRouter()


class Preferences(BaseModel):
    climate: Literal["tropical", "cold", "moderate"]
    duration: conint(ge=1, le=14)
    budget: conint(ge=500, le=5000)
    interests: List[Literal["adventure", "culture", "relaxation", "food"]]


DATA_FILE = Path(__file__).resolve().parent.parent / "sample_output.json"

try:
    RAW_DESTS = json.loads(DATA_FILE.read_text(encoding="utf-8"))["recommendations"]
except Exception as exc:  # pragma: no cover
    logger.error("Could not load %s – %s", DATA_FILE, exc)
    RAW_DESTS: list[dict] = []

COSTS = {
    "Kyoto, Japan": 1800,
    "Queenstown, New Zealand": 2000,
    "Reykjavík, Iceland": 3500,
}


def _parse_meta(reason: str) -> tuple[Optional[str], list[str]]:
    r = reason.lower()
    climate = next((c for c in ("tropical", "cold", "moderate") if c in r), None)
    tags = [t for t in ("adventure", "culture", "relaxation", "food") if t in r]
    return climate, tags


DESTINATIONS = [
    {
        "name": row["name"],
        "description": row["description"],
        "climate": (_c := _parse_meta(row["reason"])[0]),
        "tags": (_t := _parse_meta(row["reason"])[1]),
        "cost": COSTS.get(row["name"], 3000),
    }
    for row in RAW_DESTS
]
logger.info("Loaded %d destinations", len(DESTINATIONS))


def build_reason(dest: dict, pref: Preferences) -> str:
    pieces: list[str] = []

    if dest["climate"] == pref.climate:
        pieces.append(f"{pref.climate.capitalize()} climate")

    overlap = [t for t in dest["tags"] if t in pref.interests]
    if overlap:
        pieces.append(" / ".join(overlap) + " activities")

    if pref.duration > 9:
        pieces.append(f"ideal for {pref.duration}-day trip")
    elif pref.duration < 3:
        pieces.append("works even for a quick break")

    return ", ".join(pieces) if pieces else "Good overall fit"


def _is_viable(dest: dict, pref: Preferences) -> bool:
    return dest["climate"] == pref.climate and any(t in dest["tags"] for t in pref.interests)


@router.get("/health_api")
async def health():
    return {"status": "ok"}


@router.post("/recommendations_api")
async def recommend(pref: Preferences):
    viable = [d for d in DESTINATIONS if _is_viable(d, pref)]
    if not viable:
        return {"recommendations": []}

    ranked = []
    for d in viable:
        reason = build_reason(d, pref)
        ranked.append(
            {
                "name": d["name"],
                "description": d["description"],
                "reason": reason,
                "satisfaction_score": compute_score(d, pref),
            }
        )

    ranked.sort(key=lambda x: x["satisfaction_score"], reverse=True)
    return {"recommendations": ranked[:3]}
