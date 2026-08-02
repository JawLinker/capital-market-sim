from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import models
from ..config import STARTING_CASH
from ..database import get_db
from ..services.auth import (
    generate_api_key,
    get_current_player,
    hash_password,
    player_dict,
    verify_password,
)
from ..i18n import get_lang

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AuthRequest(BaseModel):
    username: str = Field(min_length=2, max_length=24)
    password: str = Field(min_length=4, max_length=64)


@router.post("/register")
def register(
    body: AuthRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    username = body.username.strip()
    exists = (
        db.query(models.Player)
        .filter(models.Player.username == username)
        .first()
    )
    if exists is not None:
        detail = (
            "用户名已被占用"
            if get_lang(request) == "zh"
            else "Username already taken"
        )
        raise HTTPException(status_code=400, detail=detail)
    is_host = db.query(models.Player).count() == 0
    player = models.Player(
        name=username,
        username=username,
        password_hash=hash_password(body.password),
        api_key=generate_api_key(),
        is_host=1 if is_host else 0,
        starting_cash=STARTING_CASH,
        cash=STARTING_CASH,
    )
    db.add(player)
    db.flush()
    state = db.query(models.GameState).first()
    db.add(
        models.PortfolioHistory(
            player_id=player.id,
            day=0,
            date=state.date,
            value=STARTING_CASH,
            cash=STARTING_CASH,
            invested=0.0,
        )
    )
    db.commit()
    return player_dict(player)


@router.post("/login")
def login(
    body: AuthRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    player = (
        db.query(models.Player)
        .filter(models.Player.username == body.username.strip())
        .first()
    )
    if player is None or not verify_password(body.password, player.password_hash):
        detail = (
            "用户名或密码错误"
            if get_lang(request) == "zh"
            else "Invalid username or password"
        )
        raise HTTPException(status_code=401, detail=detail)
    return player_dict(player)


@router.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request)
    if player is None:
        detail = (
            "请先登录"
            if get_lang(request) == "zh"
            else "Not authenticated"
        )
        raise HTTPException(status_code=401, detail=detail)
    return player_dict(player)
