import random

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import get_lang
from ..services.stories import STORIES, localize_story

router = APIRouter(prefix="/api", tags=["stories"])


@router.get("/stories/today")
def get_today_story(request: Request, db: Session = Depends(get_db)):
    state = db.query(models.GameState).first()
    day = state.day if state else 0
    story = STORIES[day % len(STORIES)]
    return {"day": day, **localize_story(story, get_lang(request))}


@router.get("/stories/random")
def get_random_story(request: Request):
    story = random.choice(STORIES)
    return {"day": None, **localize_story(story, get_lang(request))}
