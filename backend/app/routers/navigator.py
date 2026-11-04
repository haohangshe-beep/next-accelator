from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.navigator import recommend
from app.schemas import NavigatorOut

router = APIRouter(prefix="/navigator", tags=["navigator"])


@router.get("", response_model=NavigatorOut)
def navigator(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    if user.role != "learner":
        raise HTTPException(status_code=403, detail="The career navigator is for learners.")
    return {
        "summary": "Recommendations follow the modules you have finished and the tracks you marked as interests.",
        "recommendations": recommend(db, user),
    }
