"""Scripted era chronicles that turn the market replay into a story.

Each arc covers a real period of the replayed history (2021-2026). Beats fire
on real dates, and every beat carries an objective that is evaluated against
the player's live portfolio.
"""

from sqlalchemy.orm import Session

from .. import models

CHRONICLE_STAMP = {"zh": "时代纪事", "en": "ERA CHRONICLE"}

ARCS = [
    {
        "key": "2021",
        "from": "2021-01-01",
        "to": "2021-12-31",
        "title_zh": "抱团与新能源",
        "title_en": "Crowding and New Energy",
        "summary_zh": "核心资产抱团松动，新能源接过主线的火炬。",
        "summary_en": "The core-asset crowd fractures and new energy takes up the torch.",
        "beats": [
            {
                "id": "2021-b1",
                "date": "2021-04-12",
                "title_zh": "抱团出现裂缝",
                "title_en": "A Crack in the Crowd",
                "prose_zh": "白马股高位震荡，抱团叙事第一次出现裂缝，有人在观望，有人在抄底。",
                "prose_en": "Blue chips wobble near highs and the crowding narrative shows its first crack; some watch, some catch the falling knife.",
                "objective": {
                    "type": "cash_ratio",
                    "target": 15,
                    "label_zh": "现金占组合比例达到 15%",
                    "label_en": "Keep 15% of your portfolio in cash",
                },
            },
            {
                "id": "2021-b2",
                "date": "2021-07-05",
                "title_zh": "新能源主升浪",
                "title_en": "The New Energy Wave",
                "prose_zh": "锂电与光伏成为市场主线，卖方报告一页难求，散户开始背产业链名词。",
                "prose_en": "Batteries and solar become the market's main line; sell-side reports are scarce and retail investors start memorizing supply-chain terms.",
                "objective": {
                    "type": "tech_exposure",
                    "target": 25,
                    "label_zh": "科技板块仓位达到 25%",
                    "label_en": "Hold 25% of your portfolio in tech",
                },
            },
            {
                "id": "2021-b3",
                "date": "2021-09-27",
                "title_zh": "限电与缺货",
                "title_en": "Power Cuts and Shortages",
                "prose_zh": "周期品暴涨，抱团股松动，市场第一次认真讨论“缺电”两个字。",
                "prose_en": "Cyclicals surge, crowded trades loosen, and the market seriously discusses two words: power shortage.",
                "objective": {
                    "type": "cash_ratio",
                    "target": 20,
                    "label_zh": "现金占组合比例达到 20%",
                    "label_en": "Keep 20% of your portfolio in cash",
                },
            },
        ],
    },
    {
        "key": "2022",
        "from": "2022-01-01",
        "to": "2022-12-31",
        "title_zh": "熊市寒冬",
        "title_en": "The Bear Market Winter",
        "summary_zh": "开年就跌，一路跌到无人敢言抄底。",
        "summary_en": "Down from the first session, until nobody dares to call a bottom.",
        "beats": [
            {
                "id": "2022-b1",
                "date": "2022-01-25",
                "title_zh": "开年就跌",
                "title_en": "Down From Day One",
                "prose_zh": "新年没有新气象，指数一路下探，基金发行遇冷，券商营业部开始送鸡蛋。",
                "prose_en": "The new year brings no new luck; the index slides, fund launches freeze, and brokerages start giving away eggs.",
                "objective": {
                    "type": "cash_ratio",
                    "target": 30,
                    "label_zh": "现金占组合比例达到 30%",
                    "label_en": "Keep 30% of your portfolio in cash",
                },
            },
            {
                "id": "2022-b2",
                "date": "2022-04-25",
                "title_zh": "情绪冰点",
                "title_en": "The Emotional Freeze",
                "prose_zh": "沪指跌破关键点位，段子手比分析师先到岗：这是一场比谁活得久的比赛。",
                "prose_en": "The index breaks a key level and the memes arrive before the analysts: this is a contest of who survives longest.",
                "objective": {
                    "type": "total_return",
                    "target": -15,
                    "label_zh": "总收益率不低于 -15%",
                    "label_en": "Keep your total return above -15%",
                },
            },
            {
                "id": "2022-b3",
                "date": "2022-10-31",
                "title_zh": "最后一跌",
                "title_en": "The Last Drop",
                "prose_zh": "有人说这是最后一跌，有人说还要等一年。历史还没写，但筹码已经开始换手。",
                "prose_en": "Some call it the last drop, others say to wait another year. History has not been written, but chips are already changing hands.",
                "objective": {
                    "type": "cash_ratio",
                    "target": 25,
                    "label_zh": "现金占组合比例达到 25%",
                    "label_en": "Keep 25% of your portfolio in cash",
                },
            },
        ],
    },
    {
        "key": "2023",
        "from": "2023-01-01",
        "to": "2023-12-31",
        "title_zh": "存量博弈",
        "title_en": "Zero-Sum Year",
        "summary_zh": "指数原地踏步，题材轮动如走马灯。",
        "summary_en": "The index stays put while themes rotate like a merry-go-round.",
        "beats": [
            {
                "id": "2023-b1",
                "date": "2023-01-03",
                "title_zh": "哑铃策略",
                "title_en": "The Barbell Strategy",
                "prose_zh": "指数平淡，资金只在两头抱团：高股息与新技术，中间地带无人问津。",
                "prose_en": "The index is flat while money clusters at both ends of the barbell: high dividends and new tech, with nothing in between.",
                "objective": {
                    "type": "tech_exposure",
                    "target": 20,
                    "label_zh": "科技板块仓位达到 20%",
                    "label_en": "Hold 20% of your portfolio in tech",
                },
            },
            {
                "id": "2023-b2",
                "date": "2023-07-03",
                "title_zh": "AI 行情初起",
                "title_en": "AI Starts to Stir",
                "prose_zh": "大模型概念点燃算力板块，卖方连夜改模型，散户连夜改备注。",
                "prose_en": "Large-model hype ignites compute stocks; analysts rewrite models overnight and retail investors rewrite their watchlists.",
                "objective": {
                    "type": "tech_return",
                    "target": 3000,
                    "label_zh": "科技持仓浮盈与已实现收益合计达到 3,000",
                    "label_en": "Earn 3,000 combined realized and unrealized profit in tech",
                },
            },
            {
                "id": "2023-b3",
                "date": "2023-10-23",
                "title_zh": "深水区",
                "title_en": "The Deep End",
                "prose_zh": "增量资金没有来，存量资金开始互相伤害，追高的第二天准时挨打。",
                "prose_en": "No new money arrives; existing money starts hurting each other, and chasers get punished right on schedule.",
                "objective": {
                    "type": "cash_ratio",
                    "target": 20,
                    "label_zh": "现金占组合比例达到 20%",
                    "label_en": "Keep 20% of your portfolio in cash",
                },
            },
        ],
    },
    {
        "key": "2024",
        "from": "2024-01-01",
        "to": "2024-12-31",
        "title_zh": "AI 与玄学",
        "title_en": "AI and Mysticism",
        "summary_zh": "算力是真主线，玄学是最大的散户公约数。",
        "summary_en": "Compute is the real main line; mysticism is retail's greatest common denominator.",
        "beats": [
            {
                "id": "2024-b1",
                "date": "2024-02-19",
                "title_zh": "算力元年",
                "title_en": "The Year of Compute",
                "prose_zh": "节后开盘，算力概念集体躁动，龙虎榜上终于又出现了敢死队的影子。",
                "prose_en": "After the holiday, compute names surge together and the shadow of the commandos finally reappears on the seat rankings.",
                "objective": {
                    "type": "tech_exposure",
                    "target": 30,
                    "label_zh": "科技板块仓位达到 30%",
                    "label_en": "Hold 30% of your portfolio in tech",
                },
            },
            {
                "id": "2024-b2",
                "date": "2024-06-03",
                "title_zh": "玄学板块",
                "title_en": "The Mysticism Sector",
                "prose_zh": "市场开始认真讨论生肖、星座和 K 线形状，连分析师都分不清谁在开玩笑。",
                "prose_en": "The market seriously debates zodiac signs, star signs, and candlestick shapes, until even analysts can't tell who is joking.",
                "objective": {
                    "type": "tech_return",
                    "target": 5000,
                    "label_zh": "科技持仓浮盈与已实现收益合计达到 5,000",
                    "label_en": "Earn 5,000 combined realized and unrealized profit in tech",
                },
            },
            {
                "id": "2024-b3",
                "date": "2024-09-30",
                "title_zh": "政策转向",
                "title_en": "Policy Turns",
                "prose_zh": "一系列政策落地，指数放量拉升，散户的神经和账户一起被激活。",
                "prose_en": "A wave of policy lands, the index surges on volume, and both retail nerves and accounts come back to life.",
                "objective": {
                    "type": "total_return",
                    "target": 0,
                    "label_zh": "总收益率不低于 0%",
                    "label_en": "Keep your total return at or above 0%",
                },
            },
        ],
    },
    {
        "key": "2025",
        "from": "2025-01-01",
        "to": "2025-12-31",
        "title_zh": "修复之年",
        "title_en": "The Recovery Year",
        "summary_zh": "估值修复从犹豫开始，以共识结束。",
        "summary_en": "Valuation repair begins in hesitation and ends in consensus.",
        "beats": [
            {
                "id": "2025-b1",
                "date": "2025-02-10",
                "title_zh": "估值修复",
                "title_en": "Valuation Repair",
                "prose_zh": "指数缓慢爬坡，老股民说这是修复，新股民说这是牛市，两边都觉得自己赢了。",
                "prose_en": "The index climbs slowly; veterans call it repair, newcomers call it a bull, and both sides think they won.",
                "objective": {
                    "type": "tech_exposure",
                    "target": 20,
                    "label_zh": "科技板块仓位达到 20%",
                    "label_en": "Hold 20% of your portfolio in tech",
                },
            },
            {
                "id": "2025-b2",
                "date": "2025-06-09",
                "title_zh": "慢牛共识",
                "title_en": "The Consensus Crawl",
                "prose_zh": "“慢牛”成为主流叙事，连出租车司机都开始纠正别人的仓位结构。",
                "prose_en": "\"Slow bull\" becomes the mainstream story, and even taxi drivers start correcting other people's position sizing.",
                "objective": {
                    "type": "total_return",
                    "target": 10,
                    "label_zh": "总收益率不低于 10%",
                    "label_en": "Keep your total return at or above 10%",
                },
            },
            {
                "id": "2025-b3",
                "date": "2025-12-29",
                "title_zh": "年末守卫",
                "title_en": "The Year-End Defense",
                "prose_zh": "年末波动加大，有人守着利润过年，有人守着仓位赌博。",
                "prose_en": "Volatility returns at year-end; some defend their profits into the new year, others gamble their positions.",
                "objective": {
                    "type": "cash_ratio",
                    "target": 15,
                    "label_zh": "现金占组合比例达到 15%",
                    "label_en": "Keep 15% of your portfolio in cash",
                },
            },
        ],
    },
    {
        "key": "2026",
        "from": "2026-01-01",
        "to": "2026-12-31",
        "title_zh": "科技浪潮",
        "title_en": "The Tech Wave",
        "summary_zh": "算力、订单与传闻，把科技股推向聚光灯下。",
        "summary_en": "Compute, orders, and rumors push tech stocks into the spotlight.",
        "beats": [
            {
                "id": "2026-b1",
                "date": "2026-06-08",
                "title_zh": "算力订单潮",
                "title_en": "The Compute Order Flood",
                "prose_zh": "多家科技公司发布算力订单相关消息，板块放量上涨，营业部里全是新面孔。",
                "prose_en": "Several tech firms release news tied to compute orders; the sector surges on volume and the brokerage floor fills with new faces.",
                "objective": {
                    "type": "tech_exposure",
                    "target": 30,
                    "label_zh": "科技板块仓位达到 30%",
                    "label_en": "Hold 30% of your portfolio in tech",
                },
            },
            {
                "id": "2026-b2",
                "date": "2026-06-22",
                "title_zh": "龙头连板",
                "title_en": "The Leader Keeps Climbing",
                "prose_zh": "龙头连续涨停，席位榜上全是熟悉的名字，人人都在猜下一棒是谁。",
                "prose_en": "The leader racks up consecutive limit-ups; familiar names crowd the seat rankings and everyone guesses who takes the baton next.",
                "objective": {
                    "type": "tech_return",
                    "target": 8000,
                    "label_zh": "科技持仓浮盈与已实现收益合计达到 8,000",
                    "label_en": "Earn 8,000 combined realized and unrealized profit in tech",
                },
            },
            {
                "id": "2026-b3",
                "date": "2026-07-13",
                "title_zh": "分歧与监管窗口",
                "title_en": "Divergence and a Regulatory Window",
                "prose_zh": "涨势未歇，波动加大，有人开始兑现，也有人觉得这才刚开始。",
                "prose_en": "The rally persists but swings widen; some start taking profits while others insist it has only begun.",
                "objective": {
                    "type": "cash_ratio",
                    "target": 20,
                    "label_zh": "现金占组合比例达到 20%",
                    "label_en": "Keep 20% of your portfolio in cash",
                },
            },
            {
                "id": "2026-b4",
                "date": "2026-07-31",
                "title_zh": "年中复盘",
                "title_en": "The Midyear Review",
                "prose_zh": "半年过去，科技浪潮留下传说：有人麻袋装钱，也有人关灯吃面。",
                "prose_en": "Half a year later, the tech wave leaves its legends: someone carries sacks of cash, someone eats noodles in the dark.",
                "objective": {
                    "type": "total_return",
                    "target": 0,
                    "label_zh": "总收益率不低于 0%",
                    "label_en": "Keep your total return at or above 0%",
                },
            },
        ],
    },
]


def _player_value(db: Session, player: models.Player) -> float:
    value = player.cash
    holdings = db.query(models.Holding).filter(models.Holding.player_id == player.id).all()
    for holding in holdings:
        stock = db.get(models.Stock, holding.stock_id)
        if stock:
            value += holding.shares * stock.price
    return value


def _tech_holdings(db: Session, player: models.Player):
    return (
        db.query(models.Holding, models.Stock)
        .join(models.Stock, models.Holding.stock_id == models.Stock.id)
        .filter(models.Holding.player_id == player.id, models.Stock.industry == "technology")
        .all()
    )


def _evaluate_objective(db: Session, player: models.Player, objective: dict, lang: str) -> dict:
    kind = objective["type"]
    target = objective["target"]
    current = 0.0
    zh = lang == "zh"

    if kind == "tech_exposure":
        total = _player_value(db, player)
        tech = 0.0
        for holding, stock in _tech_holdings(db, player):
            tech += holding.shares * stock.price
        current = (tech / total * 100) if total > 0 else 0.0
    elif kind == "tech_holdings":
        current = float(len(_tech_holdings(db, player)))
    elif kind == "tech_return":
        realized = (
            db.query(models.Transaction)
            .join(models.Stock, models.Transaction.stock_id == models.Stock.id)
            .filter(
                models.Transaction.player_id == player.id,
                models.Stock.industry == "technology",
            )
            .with_entities(models.Transaction.realized_pnl)
            .all()
        )
        current = sum(row[0] for row in realized if row[0])
        for holding, stock in _tech_holdings(db, player):
            current += (stock.price - holding.avg_cost) * holding.shares
    elif kind == "cash_ratio":
        total = _player_value(db, player)
        current = (player.cash / total * 100) if total > 0 else 0.0
    elif kind == "total_return":
        total = _player_value(db, player)
        current = (total / player.starting_cash - 1.0) * 100 if player.starting_cash else 0.0

    return {
        "label": objective.get("label_zh") if zh else objective.get("label_en"),
        "current": round(current, 2),
        "target": target,
        "met": current >= target,
    }


def build_chronicle(db: Session, player: models.Player, date: str, lang: str) -> dict:
    zh = lang == "zh"
    arc = next((item for item in ARCS if item["from"] <= date <= item["to"]), ARCS[-1])
    beats = []
    current_beat = None
    completed = True
    for index, beat in enumerate(arc["beats"]):
        if beat["date"] <= date:
            status = "passed"
        elif current_beat is None:
            status = "current"
            current_beat = beat["id"]
            completed = False
        else:
            status = "locked"
        objective = None
        if status == "current":
            result = _evaluate_objective(db, player, beat["objective"], lang)
            objective = {
                "type": beat["objective"]["type"],
                "label": result["label"],
                "current": result["current"],
                "target": result["target"],
                "met": result["met"],
            }
        beats.append(
            {
                "id": beat["id"],
                "date": beat["date"],
                "index": index + 1,
                "status": status,
                "title": beat["title_zh"] if zh else beat["title_en"],
                "prose": beat["prose_zh"] if zh else beat["prose_en"],
                "objective": objective,
            }
        )
    if current_beat is None:
        current_beat = arc["beats"][-1]["id"]
    total = _player_value(db, player)
    total_return = (total / player.starting_cash - 1.0) * 100 if player.starting_cash else 0.0
    if total_return >= 20:
        grade_key = "gold"
        grade_label = "黄金时代" if zh else "Golden Age"
    elif total_return >= 0:
        grade_key = "silver"
        grade_label = "白银时代" if zh else "Silver Age"
    elif total_return >= -20:
        grade_key = "bronze"
        grade_label = "青铜时代" if zh else "Bronze Age"
    else:
        grade_key = "dark"
        grade_label = "黑暗时代" if zh else "Dark Age"

    return {
        "arc_key": arc["key"],
        "title": arc["title_zh"] if zh else arc["title_en"],
        "summary": arc["summary_zh"] if zh else arc["summary_en"],
        "stamp": CHRONICLE_STAMP["zh" if zh else "en"],
        "current_beat": current_beat,
        "completed": completed,
        "grade": {
            "key": grade_key,
            "label": grade_label,
            "return_pct": round(total_return, 2),
        },
        "beats": beats,
    }


def arc_book(db: Session, player: models.Player, date: str, lang: str) -> dict:
    zh = lang == "zh"
    arcs = []
    for arc in ARCS:
        beats = []
        current_beat = None
        for index, beat in enumerate(arc["beats"]):
            if date > arc["to"]:
                status = "passed"
            elif date < arc["from"]:
                status = "locked"
            elif beat["date"] <= date:
                status = "passed"
            elif current_beat is None:
                status = "current"
                current_beat = beat["id"]
            else:
                status = "locked"
            objective = None
            if status == "current":
                result = _evaluate_objective(db, player, beat["objective"], lang)
                objective = {
                    "type": beat["objective"]["type"],
                    "label": result["label"],
                    "current": result["current"],
                    "target": result["target"],
                    "met": result["met"],
                }
            beats.append(
                {
                    "id": beat["id"],
                    "date": beat["date"],
                    "index": index + 1,
                    "status": status,
                    "title": beat["title_zh"] if zh else beat["title_en"],
                    "prose": beat["prose_zh"] if zh else beat["prose_en"],
                    "objective": objective,
                }
            )
        arcs.append(
            {
                "key": arc["key"],
                "title": arc["title_zh"] if zh else arc["title_en"],
                "summary": arc["summary_zh"] if zh else arc["summary_en"],
                "from": arc["from"],
                "to": arc["to"],
                "current_beat": current_beat,
                "beats": beats,
            }
        )
    return {"arcs": arcs}
