"""Daily challenges and legend NPC commissions that push the player onward."""

import hashlib
from datetime import date

from sqlalchemy.orm import Session

from .. import models
from .chronicle import ARCS, evaluate_objective

DAILY_POOL = [
    {
        "type": "tech_exposure",
        "target": 25,
        "label_zh": "科技板块仓位达到 25%",
        "label_en": "Hold 25% of your portfolio in tech",
        "reward_zh": "今日科技手",
        "reward_en": "Today's Tech Hand",
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
        "type": "tech_holdings",
        "target": 2,
        "label_zh": "至少持有 2 只科技股",
        "label_en": "Hold at least two tech stocks",
        "reward_zh": "今日双持仓",
        "reward_en": "Today's Double Grip",
    },
    {
        "type": "tech_return",
        "target": 3000,
        "label_zh": "科技持仓浮盈与已实现收益合计达到 3,000",
        "label_en": "Earn 3,000 combined realized and unrealized profit in tech",
        "reward_zh": "今日收成",
        "reward_en": "Today's Harvest",
    },
    {
        "type": "total_return",
        "target": 0,
        "label_zh": "总收益率不低于 0%",
        "label_en": "Keep your total return at or above 0%",
        "reward_zh": "今日不倒翁",
        "reward_en": "Today's Upright",
    },
    {
        "type": "tech_exposure",
        "target": 35,
        "label_zh": "科技板块仓位达到 35%",
        "label_en": "Hold 35% of your portfolio in tech",
        "reward_zh": "今日重仓手",
        "reward_en": "Today's Heavy Hand",
    },
]

COMMISSION_NPC = {
    "commando": {
        "name_zh": "甬城敢死队队长",
        "name_en": "The Commander",
        "icon": "trending-up",
        "reward_zh": "敢死队之友",
        "reward_en": "Friend of the Commandos",
    },
    "noodle": {
        "name_zh": "关灯吃面的男人",
        "name_en": "The Noodle Man",
        "icon": "moon",
        "reward_zh": "面馆常客",
        "reward_en": "Noodle Bar Regular",
    },
    "miner": {
        "name_zh": "麻袋装钱的矿工",
        "name_en": "The Sack Miner",
        "icon": "coins",
        "reward_zh": "矿工合伙人",
        "reward_en": "Mining Partner",
    },
    "glove": {
        "name_zh": "白手套庄家",
        "name_en": "The White Glove",
        "icon": "gem",
        "reward_zh": "桌上玩家",
        "reward_en": "Seated Player",
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
    arc = next(
        (item for item in ARCS if item["from"] <= state.date <= item["to"]),
        ARCS[-1],
    )
    if arc["key"] == "2026":
        npc = COMMISSION_NPC["commando"]
        objective = {
            "type": "tech_exposure",
            "target": 40,
            "label_zh": "科技板块仓位达到 40%",
            "label_en": "Hold 40% of your portfolio in tech",
        }
        description = (
            "龙头连板那几天我盯了很久，下一棒交给你。把科技仓位压到四成，我认你这个兄弟。"
            if zh
            else "I watched the leader run for days. The baton is yours now; push tech to 40% and I will call you a brother."
        )
    elif state.market_cycle == "bear":
        npc = COMMISSION_NPC["noodle"]
        objective = {
            "type": "cash_ratio",
            "target": 40,
            "label_zh": "现金占组合比例达到 40%",
            "label_en": "Keep 40% of your portfolio in cash",
        }
        description = (
            "跌成这样，别硬扛了。留四成现金，跟我一起吃碗面。"
            if zh
            else "Do not fight this tape. Keep 40% in cash and have a bowl of noodles with me."
        )
    elif state.market_cycle == "bull":
        npc = COMMISSION_NPC["miner"]
        objective = {
            "type": "tech_return",
            "target": 8000,
            "label_zh": "科技持仓浮盈与已实现收益合计达到 8,000",
            "label_en": "Earn 8,000 combined realized and unrealized profit in tech",
        }
        description = (
            "行情好得像矿里在掉钱。替我赚出 8,000，麻袋分你一只。"
            if zh
            else "The tape prints like money falling from the mine. Make me 8,000 and one sack is yours."
        )
    else:
        npc = COMMISSION_NPC["glove"]
        objective = {
            "type": "cash_ratio",
            "target": 50,
            "label_zh": "现金占组合比例达到 50%",
            "label_en": "Keep 50% of your portfolio in cash",
        }
        description = (
            "看不懂的时候，半仓现金就是最好的仓位。我不白教你。"
            if zh
            else "When the picture is unclear, half cash is the best position. I do not teach for free."
        )
    result = evaluate_objective(db, player, objective, lang)
    return {
        "kind": "commission",
        "npc": {
            "name": npc["name_zh"] if zh else npc["name_en"],
            "icon": npc["icon"],
        },
        "title": "NPC 委托" if zh else "NPC Commission",
        "description": description,
        "objective": result,
        "reward": {"label": npc["reward_zh"] if zh else npc["reward_en"]},
    }
