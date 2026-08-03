"""Head-to-head return bets against rival NPCs: win their money."""

from sqlalchemy.orm import Session

from .. import models
from . import portfolio


def create_duel(
    db: Session,
    player: models.Player,
    rival: models.Rival,
    stake: float,
    days: int,
) -> models.Duel:
    stake = round(stake, 2)
    days = int(days)
    if stake <= 0 or stake > player.cash + 1e-6:
        raise ValueError("Stake exceeds available cash")
    if days < 1 or days > 60:
        raise ValueError("Duel horizon must be between 1 and 60 days")
    existing = (
        db.query(models.Duel)
        .filter(
            models.Duel.player_id == player.id,
            models.Duel.rival_id == rival.id,
            models.Duel.status == "open",
        )
        .first()
    )
    if existing is not None:
        raise ValueError("You already have an open duel with this rival")
    state = db.query(models.GameState).first()
    player.cash = round(player.cash - stake, 2)
    duel = models.Duel(
        player_id=player.id,
        rival_id=rival.id,
        stake=stake,
        start_day=state.day,
        end_day=state.day + days,
    )
    db.add(duel)
    db.commit()
    return duel


def list_duels(db: Session, player: models.Player) -> list:
    rows = (
        db.query(models.Duel, models.Rival)
        .join(models.Rival, models.Duel.rival_id == models.Rival.id)
        .filter(models.Duel.player_id == player.id)
        .order_by(models.Duel.id.desc())
        .all()
    )
    return [
        {
            "id": duel.id,
            "rival": rival.name,
            "stake": duel.stake,
            "start_day": duel.start_day,
            "end_day": duel.end_day,
            "status": duel.status,
            "player_return": duel.player_return,
            "rival_return": duel.rival_return,
        }
        for duel, rival in rows
    ]


def settle_duels(db: Session) -> list:
    state = db.query(models.GameState).first()
    duels = (
        db.query(models.Duel)
        .filter(models.Duel.status == "open", models.Duel.end_day <= state.day)
        .all()
    )
    results = []
    for duel in duels:
        player = db.get(models.Player, duel.player_id)
        rival = db.get(models.Rival, duel.rival_id)
        if player is None or rival is None:
            duel.status = "cancelled"
            continue
        player_return = portfolio.portfolio_value(db, player) / player.starting_cash - 1.0
        rival_return = rival.total_value / 100_000.0 - 1.0
        duel.player_return = round(player_return * 100, 2)
        duel.rival_return = round(rival_return * 100, 2)
        duel.settled_day = state.day
        if player_return > rival_return:
            duel.status = "won"
            payout = duel.stake * 2
            player.cash = round(player.cash + payout, 2)
        elif player_return < rival_return:
            duel.status = "lost"
            payout = 0.0
        else:
            duel.status = "tied"
            payout = duel.stake
            player.cash = round(player.cash + payout, 2)
        results.append(
            {
                "duel_id": duel.id,
                "rival": rival.name,
                "result": duel.status,
                "payout": round(payout, 2),
                "player_return": duel.player_return,
                "rival_return": duel.rival_return,
            }
        )
    db.commit()
    return results
