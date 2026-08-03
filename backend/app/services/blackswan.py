"""Random era-flavored black swan events that shake up a playthrough."""

import random

BLACK_SWANS = [
    {
        "id": "bs01",
        "from_date": "2021-03-01",
        "to_date": "2021-06-30",
        "sentiment_delta": 0.05,
        "title_zh": "北向资金异动",
        "title_en": "Northbound Money Stir",
        "prose_zh": "北向资金单日大幅净流入，龙虎榜上外资席位集体出现，市场传说“聪明钱回来了”。",
        "prose_en": "Northbound money floods in for the day, foreign seats crowd the rankings, and the market whispers that smart money is back.",
    },
    {
        "id": "bs02",
        "from_date": "2021-09-01",
        "to_date": "2021-12-31",
        "sentiment_delta": -0.08,
        "title_zh": "限电潮来袭",
        "title_en": "The Power-Cut Wave",
        "prose_zh": "多省份发布限电通知，生产链股票集体下挫，段子手连夜写稿：电停了，梦也停了。",
        "prose_en": "Provinces issue power-cut orders, supply-chain stocks slump, and the memes write themselves overnight.",
    },
    {
        "id": "bs03",
        "from_date": "2022-01-01",
        "to_date": "2022-06-30",
        "sentiment_delta": -0.08,
        "title_zh": "全球通胀冲击",
        "title_en": "Global Inflation Shock",
        "prose_zh": "海外通胀数据超预期，加息预期升温，全球风险资产一起打了个哆嗦。",
        "prose_en": "Overseas inflation overshoots, rate-hike bets firm up, and risk assets around the world shiver at once.",
    },
    {
        "id": "bs04",
        "from_date": "2022-04-01",
        "to_date": "2022-12-31",
        "sentiment_delta": 0.05,
        "title_zh": "政策密集期",
        "title_en": "The Policy Season",
        "prose_zh": "稳增长政策密集落地，基建与地产链集体反弹，营业部里又开始排起开户长队。",
        "prose_en": "Growth-support policies land in rapid succession, infrastructure and property chains bounce, and account queues reform at the branches.",
    },
    {
        "id": "bs05",
        "from_date": "2023-02-01",
        "to_date": "2023-12-31",
        "sentiment_delta": 0.06,
        "title_zh": "AI 概念潮",
        "title_en": "The AI Tide",
        "prose_zh": "大模型发布点燃算力板块，卖方连夜改模型，散户连夜改备注。",
        "prose_en": "A large-model launch ignites compute names; analysts rewrite models overnight and retail investors rewrite their watchlists.",
    },
    {
        "id": "bs06",
        "from_date": "2024-02-01",
        "to_date": "2024-04-30",
        "sentiment_delta": -0.07,
        "title_zh": "监管窗口",
        "title_en": "The Regulatory Window",
        "prose_zh": "交易所加强异常交易监控，部分席位被限制交易，市场短暂安静了一整天。",
        "prose_en": "Exchanges tighten surveillance on abnormal trading, several seats are restricted, and the market goes quiet for a day.",
    },
    {
        "id": "bs07",
        "from_date": "2024-05-01",
        "to_date": "2024-12-31",
        "sentiment_delta": 0.04,
        "title_zh": "玄学行情",
        "title_en": "The Mysticism Rally",
        "prose_zh": "市场开始认真讨论生肖、星座与 K 线形状，连分析师都分不清谁在开玩笑。",
        "prose_en": "The market seriously debates zodiac signs, star signs, and candle shapes, until even analysts cannot tell who is joking.",
    },
    {
        "id": "bs08",
        "from_date": "2025-01-01",
        "to_date": "2025-12-31",
        "sentiment_delta": 0.05,
        "title_zh": "估值修复共识",
        "title_en": "The Repair Consensus",
        "prose_zh": "“估值修复”成为主流叙事，连出租车司机都开始纠正别人的仓位结构。",
        "prose_en": "\"Valuation repair\" becomes the mainstream story, and even taxi drivers start correcting other people's position sizing.",
    },
    {
        "id": "bs09",
        "from_date": "2026-06-01",
        "to_date": "2026-07-31",
        "sentiment_delta": 0.09,
        "title_zh": "算力订单潮",
        "title_en": "The Compute Order Flood",
        "prose_zh": "多家科技公司发布算力订单相关消息，板块放量上涨，营业部里全是新面孔。",
        "prose_en": "Several tech firms release news tied to compute orders; the sector surges on volume and the brokerage floor fills with new faces.",
    },
    {
        "id": "bs10",
        "from_date": "2026-07-01",
        "to_date": "2026-08-31",
        "sentiment_delta": -0.07,
        "title_zh": "高位分歧",
        "title_en": "Divergence at the Top",
        "prose_zh": "龙头冲高回落，龙虎榜买卖双方互道保重，有人开始把麻袋换成现金。",
        "prose_en": "The leader spikes and fades; the buy and sell seats wish each other well as some start trading sacks for cash.",
    },
]


def eligible_black_swans(date: str):
    return [
        event
        for event in BLACK_SWANS
        if event["from_date"] <= date <= event["to_date"]
    ]


def pick_black_swan(date: str, rng: random.Random | None = None):
    pool = eligible_black_swans(date)
    if not pool:
        return None
    chooser = rng or random
    return chooser.choice(pool)


def localize_black_swan(event: dict, lang: str) -> dict:
    zh = lang == "zh"
    return {
        "id": event["id"],
        "date": event.get("date"),
        "title": event["title_zh"] if zh else event["title_en"],
        "prose": event["prose_zh"] if zh else event["prose_en"],
        "sentiment_delta": event["sentiment_delta"],
    }
