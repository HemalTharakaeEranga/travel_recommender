from __future__ import annotations

import json, logging, os, re, requests
from pathlib import Path
from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel, conint

from .model import compute_score

log = logging.getLogger(__name__)
router = APIRouter()


class Preferences(BaseModel):
    climate: Literal["tropical", "cold", "moderate"]
    duration: conint(ge=1, le=14)
    budget: conint(ge=500, le=5000)
    interests: List[Literal["adventure", "culture", "relaxation", "food"]]


DATA_FILE = Path(__file__).resolve().parent.parent / "sample_output.json"
_FALLBACK_RAW = json.loads(DATA_FILE.read_text("utf-8"))["recommendations"]

_CLIMATE_SYNS = {
    "tropical": ("tropical", "warm", "humid", "equatorial"),
    "cold": ("cold", "cool", "snow", "arctic"),
    "moderate": ("moderate", "mild", "temperate", "spring"),
}
_TAGS = ("adventure", "culture", "relaxation", "food")


def _infer_climate(text: str) -> str | None:
    t = text.lower()
    for key, words in _CLIMATE_SYNS.items():
        if any(w in t for w in words):
            return key
    return None


def _enrich(row: dict) -> dict:
    clim = _infer_climate(row["reason"])
    tags = [t for t in _TAGS if t in row["reason"].lower()]
    return {**row, "climate": clim, "tags": tags, "cost": 3_000}


_FALLBACK = [_enrich(r) for r in _FALLBACK_RAW]

CF_ACC_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CF_API_KEY = os.getenv("CLOUDFLARE_AI_TOKEN")
CF_MODEL = "@cf/meta/llama-3-8b-instruct"

_CF_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACC_ID}/ai/run/{CF_MODEL}"
_CF_HEADERS = {"Authorization": f"Bearer {CF_API_KEY}"}


def _call_cloudflare(prompt: str, max_tokens: int = 180) -> str:
    body = {
        "messages": [
            {"role": "system", "content": "You are a helpful travel expert."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    r = requests.post(_CF_URL, headers=_CF_HEADERS, json=body, timeout=45)
    r.raise_for_status()
    data = r.json()

    if "result" in data:
        res = data["result"]
        if "response" in res:
            return res["response"].strip()
        if "choices" in res and res["choices"]:  # legacy schema
            return res["choices"][0]["message"]["content"].strip()

    raise ValueError(f"Unexpected Cloudflare schema → {data}")


_RE_LINE = re.compile(
    r"^\s*\d+\.\s*(?P<name>.+?)\s*[-–]\s*(?P<desc>.+?)\.\s*Why:\s*(?P<reason>.+)$",
    re.I,
)


def _filter_and_score(rows: list[dict], pref: Preferences) -> list[dict]:
    good = [
        r for r in rows
        if r["climate"] == pref.climate and any(t in r["tags"] for t in pref.interests)
    ]
    for r in good:
        r["satisfaction_score"] = compute_score(r, pref)
    good.sort(key=lambda x: x["satisfaction_score"], reverse=True)
    return good[:3]


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/recommendations")
async def recommendations(pref: Preferences):
    prompt = (
        f"Recommend exactly 3 destinations for a {pref.duration}-day trip.\n"
        f"Preferred climate: {pref.climate}; budget: ${pref.budget}; "
        f"interests: {', '.join(pref.interests)}.\n"
        "Return each destination on its own line in the format:\n"
        "1. <Name> – <Short description>. Why: <reason>\n"
    )

    try:
        raw = _call_cloudflare(prompt)
        log.debug("Cloudflare output:\n%s", raw)
        parsed: list[dict] = []
        for line in raw.splitlines():
            m = _RE_LINE.match(line)
            if m:
                name, desc, reason = m.group("name"), m.group("desc"), m.group("reason")
                parsed.append(_enrich({"name": name, "description": desc, "reason": reason}))

        if parsed:
            top3 = _filter_and_score(parsed, pref)
            if top3:
                return {"recommendations": top3}

    except Exception as exc:
        log.warning("Cloudflare AI failed – %s", exc)

    # fallback path
    log.info("Serving filtered fallback recommendations")
    return {"recommendations": _filter_and_score(_FALLBACK, pref)}
