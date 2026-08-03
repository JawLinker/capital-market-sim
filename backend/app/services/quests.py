"""Daily challenges and legend NPC commissions that push the player onward."""

import hashlib
import json
import random
from datetime import date

from sqlalchemy.orm import Session

from .. import models
from .chronicle import ARCS, evaluate_objective

DAILY_POOL = [
    {
        "type": "sector_exposure",
        "industry": "energy",
        "target": 20,
        "label_zh": "能源板块仓位达到 20%",
        "label_en": "Hold 20% of your portfolio in energy",
        "reward_zh": "今日能源手",
        "reward_en": "Today's Energy Hand",
    },
    {
        "type": "cash_ratio",
        "target": 25,
        "label_zh": "现金占组合比例达到 25%",
        "label_en": "Keep 25% of your portfolio in cash",
        "reward_zh": "今日守财人",
        "reward_en": "Today's Keeper",
    },
    {
        "type": "trade_count",
        "target": 5,
        "label_zh": "完成 5 笔交易",
        "label_en": "Place five trades",
        "reward_zh": "今日勤劳手",
        "reward_en": "Today's Busy Hand",
    },
    {
        "type": "sector_return",
        "industry": "healthcare",
        "target": 2000,
        "label_zh": "医疗持仓浮盈与已实现收益合计达到 2,000",
        "label_en": "Earn 2,000 combined realized and unrealized profit in healthcare",
        "reward_zh": "今日药箱",
        "reward_en": "Today's Medicine Box",
    },
    {
        "type": "diversified",
        "target": 3,
        "label_zh": "持仓覆盖 3 个行业",
        "label_en": "Hold positions in three industries",
        "reward_zh": "今日布局人",
        "reward_en": "Today's Planner",
    },
    {
        "type": "daily_gain",
        "target": 1.5,
        "label_zh": "单日组合收益达到 1.5%",
        "label_en": "Gain 1.5% of portfolio value in a single day",
        "reward_zh": "今日手感王",
        "reward_en": "Today's Hot Hand",
    },
]

COMMISSION_NPC = {
    "commando": {
        "name_zh": "甬城敢死队队长",
        "name_en": "The Commander",
        "icon": "trending-up",
        "reward_zh": "敢死队之友",
        "reward_en": "Friend of the Commandos",
        "reject_zh": "敢死队不问第二遍。你不接，下个月有人替你接。",
        "reject_en": "The commandos do not ask twice. Refuse, and someone else takes your seat next month.",
    },
    "noodle": {
        "name_zh": "关灯吃面的男人",
        "name_en": "The Noodle Man",
        "icon": "moon",
        "reward_zh": "面馆常客",
        "reward_en": "Noodle Bar Regular",
        "reject_zh": "没事，面管够。你想清楚再来。",
        "reject_en": "No hard feelings; the noodles are always here. Come back when you are ready.",
    },
    "miner": {
        "name_zh": "麻袋装钱的矿工",
        "name_en": "The Sack Miner",
        "icon": "coins",
        "reward_zh": "矿工合伙人",
        "reward_en": "Mining Partner",
        "reject_zh": "矿上不缺人，缺的是敢下井的。",
        "reject_en": "The mine never lacks hands, only people willing to go down.",
    },
    "glove": {
        "name_zh": "白手套庄家",
        "name_en": "The White Glove",
        "icon": "gem",
        "reward_zh": "桌上玩家",
        "reward_en": "Seated Player",
        "reject_zh": "不懂规矩的人，上不了这张桌。",
        "reject_en": "People who do not know the rules never sit at this table.",
    },
}


def _hash_date(day: str) -> int:
    return int(hashlib.sha256(day.encode("utf-8")).hexdigest()[:8], 16)


def daily_challenge(db: Session, player: models.Player, lang: str) -> dict:
    zh = lang == "zh"
    today = date.today().isoformat()
    task = DAILY_POOL[_hash_date(today) % len(DAILY_POOL)]
    result = evaluate_objective(db, player, task, lang)
    return {
        "kind": "daily",
        "date": today,
        "title": "每日挑战" if zh else "Daily Challenge",
        "description": (
            "以今天为种子抽出的一个小目标，完成即得当日徽章。"
            if zh
            else "A small objective drawn from today's seed. Finish it to earn today's badge."
        ),
        "objective": result,
        "reward": {"label": task["reward_zh"] if zh else task["reward_en"]},
    }


def commission(db: Session, player: models.Player, state: models.GameState, lang: str) -> dict:
    zh = lang == "zh"
    latest = (
        db.query(models.Decision)
        .filter(
            models.Decision.player_id == player.id,
            models.Decision.kind == "commission",
        )
        .order_by(models.Decision.id.desc())
        .first()
    )
    if latest is not None:
        payload = json.loads(latest.payload)
        if latest.status == "rejected":
            cooldown_until = payload.get("cooldown_until", 0)
            if state.day < cooldown_until:
                return {
                    "kind": "commission",
                    "status": "rejected",
                    "decision_id": latest.id,
                    "npc": payload["npc"],
                    "title": "NPC 委托" if zh else "NPC Commission",
                    "message": payload["reject_message"],
                    "cooldown_days": cooldown_until - state.day,
                }
        if latest.status in {"open", "accepted"}:
            return _commission_card(db, player, payload, latest.status, latest.id, lang)

    npc_key, objective, description = _base_commission(state, zh)
    npc = COMMISSION_NPC[npc_key]
    payload = {
        "npc_key": npc_key,
        "npc": {
            "name": npc["name_zh"] if zh else npc["name_en"],
            "icon": npc["icon"],
        },
        "description": description,
        "objective": objective,
        "reward": {"label": npc["reward_zh"] if zh else npc["reward_en"]},
        "options": [
            {
                "key": "accept",
                "label": "接受" if zh else "Accept",
                "detail": "按原目标完成" if zh else "Do it as offered",
            },
            {
                "key": "bargain",
                "label": "讨价还价" if zh else "Bargain",
                "detail": "随机调整目标与奖励" if zh else "Target and reward may change",
            },
            {
                "key": "reject",
                "label": "拒绝" if zh else "Refuse",
                "detail": "NPC 会记仇几天" if zh else "The NPC remembers for a while",
            },
        ],
    }
    decision = models.Decision(
        player_id=player.id,
        kind="commission",
        payload=json.dumps(payload, ensure_ascii=False),
        created_day=state.day,
    )
    db.add(decision)
    db.commit()
    return _commission_card(db, player, payload, "open", decision.id, lang)


def _base_commission(state: models.GameState, zh: bool):
    arc = next(
        (item for item in ARCS if item["from"] <= state.date <= item["to"]),
        ARCS[-1],
    )
    if arc["key"] == "2026":
        return "commando", {
            "type": "tech_exposure",
            "target": 40,
            "label_zh": "科技板块仓位达到 40%",
            "label_en": "Hold 40% of your portfolio in tech",
        }, (
            "龙头连板那几天我盯了很久，下一棒交给你。把科技仓位压到四成，我认你这个兄弟。"
            if zh
            else "I watched the leader run for days. The baton is yours now; push tech to 40% and I will call you a brother."
        )
    if state.market_cycle == "bear":
        return "noodle", {
            "type": "cash_ratio",
            "target": 40,
            "label_zh": "现金占组合比例达到 40%",
            "label_en": "Keep 40% of your portfolio in cash",
        }, (
            "跌成这样，别硬扛了。留四成现金，跟我一起吃碗面。"
            if zh
            else "Do not fight this tape. Keep 40% in cash and have a bowl of noodles with me."
        )
    if state.market_cycle == "bull":
        return "miner", {
            "type": "sector_return",
            "industry": "energy",
            "target": 8000,
            "label_zh": "能源持仓浮盈与已实现收益合计达到 8,000",
            "label_en": "Earn 8,000 combined realized and unrealized profit in energy",
        }, (
            "行情好得像矿里在掉钱。去资源里替我赚出 8,000，麻袋分你一只。"
            if zh
            else "The tape prints like money falling from the mine. Make 8,000 in resources and one sack is yours."
        )
    return "glove", {
        "type": "diversified",
        "target": 4,
        "label_zh": "持仓覆盖 4 个行业",
        "label_en": "Hold positions in four industries",
    }, (
        "看不懂的时候，分散就是最好的仓位。四个行业起步，我不白教你。"
        if zh
        else "When the picture is unclear, diversification is the best position. Start with four industries; I do not teach for free."
    )


def _commission_card(db, player, payload, status, decision_id, lang):
    result = evaluate_objective(db, player, payload["objective"], lang)
    return {
        "kind": "commission",
        "status": status,
        "decision_id": decision_id,
        "npc": payload["npc"],
        "title": "NPC 委托" if lang == "zh" else "NPC Commission",
        "description": payload["description"],
        "objective": result,
        "reward": payload["reward"],
        "options": payload.get("options", []),
    }


def resolve_commission_decision(
    db: Session,
    player: models.Player,
    decision_id: int,
    option_key: str,
    lang: str,
) -> dict:
    zh = lang == "zh"
    decision = (
        db.query(models.Decision)
        .filter(
            models.Decision.id == decision_id,
            models.Decision.player_id == player.id,
            models.Decision.kind == "commission",
            models.Decision.status == "open",
        )
        .first()
    )
    if decision is None:
        raise ValueError("Open commission decision not found")
    payload = json.loads(decision.payload)
    if option_key == "accept":
        decision.status = "accepted"
        message = "委托已接受，目标已锁定。" if zh else "Commission accepted. Objective locked."
    elif option_key == "bargain":
        objective = payload["objective"]
        if random.random() < 0.5:
            objective["target"] = round(objective["target"] * 0.75, 2)
            payload["reward"] = {
                "label": (
                    f"{payload['reward']['label']}（减半）"
                    if zh
                    else f"{payload['reward']['label']} (halved)"
                )
            }
            message = "谈成了：目标降低，奖励减半。" if zh else "Deal: target lowered, reward halved."
        else:
            objective["target"] = round(objective["target"] * 1.25, 2)
            message = "谈崩了：NPC 加码，目标反而提高。" if zh else "No deal: the NPC raises the target."
        payload["objective"] = objective
        decision.status = "accepted"
    elif option_key == "reject":
        npc = COMMISSION_NPC.get(payload.get("npc_key"))
        payload["cooldown_until"] = db.query(models.GameState).first().day + 5
        payload["reject_message"] = (
            npc["reject_zh"] if zh else npc["reject_en"]
        ) if npc else ("NPC 记住了。" if zh else "The NPC remembers.")
        decision.status = "rejected"
        message = "你拒绝了委托。" if zh else "You refused the commission."
    else:
        raise ValueError("Invalid commission option")
    state = db.query(models.GameState).first()
    decision.payload = json.dumps(payload, ensure_ascii=False)
    db.commit()
    cooldown_days = (
        payload.get("cooldown_until", 0) - state.day
        if decision.status == "rejected"
        else 0
    )
    return {
        "status": decision.status,
        "message": message,
        "cooldown_days": cooldown_days,
    }
