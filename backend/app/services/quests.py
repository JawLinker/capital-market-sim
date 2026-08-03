"""Daily challenges and legend NPC commissions that push the player onward."""

import hashlib
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
            "type": "sector_return",
            "industry": "energy",
            "target": 8000,
            "label_zh": "能源持仓浮盈与已实现收益合计达到 8,000",
            "label_en": "Earn 8,000 combined realized and unrealized profit in energy",
        }
        description = (
            "行情好得像矿里在掉钱。去资源里替我赚出 8,000，麻袋分你一只。"
            if zh
            else "The tape prints like money falling from the mine. Make 8,000 in resources and one sack is yours."
        )
    else:
        npc = COMMISSION_NPC["glove"]
        objective = {
            "type": "diversified",
            "target": 4,
            "label_zh": "持仓覆盖 4 个行业",
            "label_en": "Hold positions in four industries",
        }
        description = (
            "看不懂的时候，分散就是最好的仓位。四个行业起步，我不白教你。"
            if zh
            else "When the picture is unclear, diversification is the best position. Start with four industries; I do not teach for free."
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
