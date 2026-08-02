"""Simple password hashing and API-key player lookup for LAN multiplayer."""

import hashlib
import hmac
import secrets

from fastapi import Request
from sqlalchemy.orm import Session

from .. import models


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    if not stored or "$" not in stored:
        return False
    salt, digest = stored.split("$", 1)
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
    ).hex()
    return hmac.compare_digest(candidate, digest)


def generate_api_key() -> str:
    return secrets.token_urlsafe(24)


def get_current_player(db: Session, request: Request) -> models.Player:
    key = request.headers.get("x-api-key")
    if key:
        player = (
            db.query(models.Player)
            .filter(models.Player.api_key == key)
            .first()
        )
        if player is not None:
            return player
    return db.query(models.Player).first()


def player_dict(player: models.Player) -> dict:
    return {
        "id": player.id,
        "name": player.name,
        "username": player.username,
        "is_host": bool(player.is_host),
        "starting_cash": player.starting_cash,
        "api_key": player.api_key,
    }
