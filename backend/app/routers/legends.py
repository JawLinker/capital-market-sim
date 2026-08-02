from fastapi import APIRouter, Request

from ..i18n import get_lang
from ..services.legends import LEGENDS, TIMELINE, localize_event, localize_legend

router = APIRouter(prefix="/api", tags=["legends"])


@router.get("/legends")
def list_legends(request: Request):
    lang = get_lang(request)
    return {
        "count": len(LEGENDS),
        "legends": [localize_legend(legend, lang) for legend in LEGENDS],
    }


@router.get("/timeline")
def list_timeline(request: Request):
    lang = get_lang(request)
    return {
        "count": len(TIMELINE),
        "events": [localize_event(event, lang) for event in TIMELINE],
    }
