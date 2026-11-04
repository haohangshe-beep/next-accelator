from __future__ import annotations

from fastapi import APIRouter

from app.schemas import TrackOut
from app.tracks import TRACK_LABELS

router = APIRouter(tags=["meta"])


@router.get("/tracks", response_model=list[TrackOut])
def list_tracks() -> list[dict[str, str]]:
    return [{"code": code, "label": label} for code, label in TRACK_LABELS.items()]
