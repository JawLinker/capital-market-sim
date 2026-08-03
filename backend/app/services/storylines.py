"""Multi-chapter storyline quests for the four legend NPCs."""

from sqlalchemy.orm import Session

from .. import models
from .chronicle import evaluate_objective

STORYLINES = [
    {
        "key": "commando",
        "name_zh": "甬城敢死队队长",
        "name_en": "The Commander",
        "icon": "trending-up",
        "chapters": [
            {
                "id": "cm1",
                "title_zh": "第一课：看盘口",
                "title_en": "Lesson 1: Read the Book",
                "prose_zh": "盘口就是战场地图。先学会分辨谁在买，谁在喊单。",
                "prose_en": "The book is your battlefield map. First learn who is buying and who is just shouting.",
                "objective": {"type": "tech_exposure", "target": 20, "label_zh": "科技板块仓位达到 20%", "label_en": "Hold 20% of your portfolio in tech"},
                "reward_zh": "菜鸟敢死队员",
                "reward_en": "Rookie Commando",
            },
            {
                "id": "cm2",
                "title_zh": "第二课：打板",
                "title_en": "Lesson 2: Chase the Limit",
                "prose_zh": "敢死队的规矩：只在最热闹的时候出手。",
                "prose_en": "Commando rule: strike only when the crowd is loudest.",
                "objective": {"type": "trade_count", "target": 5, "label_zh": "完成 5 笔交易", "label_en": "Place five trades"},
                "reward_zh": "打板练习生",
                "reward_en": "Limit-Up Trainee",
            },
            {
                "id": "cm3",
                "title_zh": "第三课：龙头",
                "title_en": "Lesson 3: The Leader",
                "prose_zh": "板块可以轮动，龙头只有一个。找到它，跟住它。",
                "prose_en": "Sectors rotate, but there is only one leader. Find it and stay with it.",
                "objective": {"type": "tech_return", "target": 3000, "label_zh": "科技持仓浮盈与已实现收益合计达到 3,000", "label_en": "Earn 3,000 combined realized and unrealized profit in tech"},
                "reward_zh": "龙头观察员",
                "reward_en": "Leader Watcher",
            },
            {
                "id": "cm4",
                "title_zh": "第四课：龙虎榜",
                "title_en": "Lesson 4: The Rankings",
                "prose_zh": "上了龙虎榜，你就有了名字。但名字也是靶子。",
                "prose_en": "Make the rankings and you have a name. But a name is also a target.",
                "objective": {"type": "daily_gain", "target": 2.5, "label_zh": "单日组合收益达到 2.5%", "label_en": "Gain 2.5% of portfolio value in a single day"},
                "reward_zh": "龙虎榜常客",
                "reward_en": "Rankings Regular",
            },
            {
                "id": "cm5",
                "title_zh": "毕业：封神之路",
                "title_en": "Graduation: The Legend Road",
                "prose_zh": "最后一课没有板书，只有一句：记住你从哪里来。",
                "prose_en": "The final lesson has no chalkboard, only one line: remember where you came from.",
                "objective": {"type": "tech_return", "target": 8000, "label_zh": "科技持仓浮盈与已实现收益合计达到 8,000", "label_en": "Earn 8,000 combined realized and unrealized profit in tech"},
                "reward_zh": "敢死队名誉队长",
                "reward_en": "Honorary Commander",
            },
        ],
    },
    {
        "key": "noodle",
        "name_zh": "关灯吃面的男人",
        "name_en": "The Noodle Man",
        "icon": "moon",
        "chapters": [
            {
                "id": "nm1",
                "title_zh": "第一课：先吃面",
                "title_en": "Lesson 1: Eat the Noodles First",
                "prose_zh": "亏钱之后别急着加仓，先吃饱再说。",
                "prose_en": "After a loss, do not rush to add. Eat first.",
                "objective": {"type": "cash_ratio", "target": 20, "label_zh": "现金占组合比例达到 20%", "label_en": "Keep 20% of your portfolio in cash"},
                "reward_zh": "面馆学徒",
                "reward_en": "Noodle Shop Apprentice",
            },
            {
                "id": "nm2",
                "title_zh": "第二课：活着",
                "title_en": "Lesson 2: Stay Alive",
                "prose_zh": "市场会淘汰很多人，活下来的才有资格讲故事。",
                "prose_en": "The market retires many. Only survivors get to tell stories.",
                "objective": {"type": "sector_exposure", "industry": "finance", "target": 15, "label_zh": "金融板块仓位达到 15%", "label_en": "Hold 15% of your portfolio in finance"},
                "reward_zh": "夜宵摊主",
                "reward_en": "Midnight Snack Owner",
            },
            {
                "id": "nm3",
                "title_zh": "第三课：回本",
                "title_en": "Lesson 3: Break Even",
                "prose_zh": "回本不是终点，只是另一碗面的开始。",
                "prose_en": "Breaking even is not the end, just the start of another bowl.",
                "objective": {"type": "total_return", "target": -10, "label_zh": "总收益率不低于 -10%", "label_en": "Keep your total return above -10%"},
                "reward_zh": "回本信徒",
                "reward_en": "Break-Even Believer",
            },
            {
                "id": "nm4",
                "title_zh": "第四课：不追高",
                "title_en": "Lesson 4: Do Not Chase",
                "prose_zh": "追高的人吃面，等回调的人也吃面，区别是前者加辣。",
                "prose_en": "Chasers eat noodles, pullback waiters eat noodles too. The difference is the chili.",
                "objective": {"type": "cash_ratio", "target": 45, "label_zh": "现金占组合比例达到 45%", "label_en": "Keep 45% of your portfolio in cash"},
                "reward_zh": "不追高人",
                "reward_en": "No-Chase Regular",
            },
            {
                "id": "nm5",
                "title_zh": "毕业：关灯自由",
                "title_en": "Graduation: Lights-Off Freedom",
                "prose_zh": "最后你发现，能关灯安心睡觉，就是散户最好的回报。",
                "prose_en": "In the end you learn that sleeping with the lights off is the retail investor's best return.",
                "objective": {"type": "total_return", "target": 0, "label_zh": "总收益率不低于 0%", "label_en": "Keep your total return at or above 0%"},
                "reward_zh": "关灯自由人",
                "reward_en": "Lights-Off Free Man",
            },
        ],
    },
    {
        "key": "miner",
        "name_zh": "麻袋装钱的矿工",
        "name_en": "The Sack Miner",
        "icon": "coins",
        "chapters": [
            {
                "id": "mi1",
                "title_zh": "第一课：找矿",
                "title_en": "Lesson 1: Find the Ore",
                "prose_zh": "景气来了，先找到矿脉在哪。",
                "prose_en": "When the cycle turns, first find where the ore lives.",
                "objective": {"type": "sector_exposure", "industry": "energy", "target": 20, "label_zh": "能源板块仓位达到 20%", "label_en": "Hold 20% of your portfolio in energy"},
                "reward_zh": "找矿人",
                "reward_en": "Ore Finder",
            },
            {
                "id": "mi2",
                "title_zh": "第二课：挖矿",
                "title_en": "Lesson 2: Dig",
                "prose_zh": "好矿要挖深一点，仓位要拿稳一点。",
                "prose_en": "Rich ore needs deeper digging and steadier hands.",
                "objective": {"type": "hold_count", "target": 4, "label_zh": "同时持有 4 只股票", "label_en": "Hold four positions at once"},
                "reward_zh": "挖矿工",
                "reward_en": "Shaft Digger",
            },
            {
                "id": "mi3",
                "title_zh": "第三课：装钱",
                "title_en": "Lesson 3: Fill the Sack",
                "prose_zh": "赚到的钱只有装进麻袋才算数。",
                "prose_en": "Profit only counts once it is in the sack.",
                "objective": {"type": "sector_return", "industry": "energy", "target": 5000, "label_zh": "能源持仓浮盈与已实现收益合计达到 5,000", "label_en": "Earn 5,000 combined realized and unrealized profit in energy"},
                "reward_zh": "装钱手",
                "reward_en": "Sack Filler",
            },
            {
                "id": "mi4",
                "title_zh": "第四课：麻袋",
                "title_en": "Lesson 4: The Sack",
                "prose_zh": "仓位像麻袋，太满会漏，太空会飘。",
                "prose_en": "Position is a sack: too full it leaks, too empty it floats.",
                "objective": {"type": "sector_exposure", "industry": "energy", "target": 40, "label_zh": "能源板块仓位达到 40%", "label_en": "Hold 40% of your portfolio in energy"},
                "reward_zh": "麻袋管理员",
                "reward_en": "Sack Keeper",
            },
            {
                "id": "mi5",
                "title_zh": "毕业：分你一袋",
                "title_en": "Graduation: One Sack Is Yours",
                "prose_zh": "行情会走，矿会枯，但手艺是你的。分你一袋，下山吧。",
                "prose_en": "Rallies fade and mines dry up, but the craft stays yours. Take a sack and head down the mountain.",
                "objective": {"type": "sector_return", "industry": "energy", "target": 12000, "label_zh": "能源持仓浮盈与已实现收益合计达到 12,000", "label_en": "Earn 12,000 combined realized and unrealized profit in energy"},
                "reward_zh": "矿主合伙人",
                "reward_en": "Mine Partner",
            },
        ],
    },
    {
        "key": "glove",
        "name_zh": "白手套庄家",
        "name_en": "The White Glove",
        "icon": "gem",
        "chapters": [
            {
                "id": "gl1",
                "title_zh": "第一课：筹码",
                "title_en": "Lesson 1: Chips",
                "prose_zh": "先看筹码在谁手里，再决定你要不要上桌。",
                "prose_en": "See whose hands hold the chips before deciding to sit down.",
                "objective": {"type": "sector_exposure", "industry": "finance", "target": 20, "label_zh": "金融板块仓位达到 20%", "label_en": "Hold 20% of your portfolio in finance"},
                "reward_zh": "筹码学徒",
                "reward_en": "Chip Apprentice",
            },
            {
                "id": "gl2",
                "title_zh": "第二课：控盘",
                "title_en": "Lesson 2: Control",
                "prose_zh": "真正的控盘不是买多少，而是留多少。",
                "prose_en": "Real control is not how much you buy, but how much you keep.",
                "objective": {"type": "cash_ratio", "target": 25, "label_zh": "现金占组合比例达到 25%", "label_en": "Keep 25% of your portfolio in cash"},
                "reward_zh": "控盘练习生",
                "reward_en": "Control Trainee",
            },
            {
                "id": "gl3",
                "title_zh": "第三课：出货",
                "title_en": "Lesson 3: Distribution",
                "prose_zh": "会买是徒弟，会卖是师傅，会离场是庄家。",
                "prose_en": "Buying makes a student, selling makes a master, leaving makes the house.",
                "objective": {"type": "sector_return", "industry": "finance", "target": 3000, "label_zh": "金融持仓浮盈与已实现收益合计达到 3,000", "label_en": "Earn 3,000 combined realized and unrealized profit in finance"},
                "reward_zh": "出货员",
                "reward_en": "Distributor",
            },
            {
                "id": "gl4",
                "title_zh": "第四课：半仓",
                "title_en": "Lesson 4: Half Position",
                "prose_zh": "看不懂的时候，半仓就是最重的仓位。",
                "prose_en": "When the picture is unclear, half position is the heaviest you should go.",
                "objective": {"type": "cash_ratio", "target": 50, "label_zh": "现金占组合比例达到 50%", "label_en": "Keep 50% of your portfolio in cash"},
                "reward_zh": "半仓信徒",
                "reward_en": "Half-Position Believer",
            },
            {
                "id": "gl5",
                "title_zh": "毕业：桌上说话",
                "title_en": "Graduation: Speak at the Table",
                "prose_zh": "毕业没有证书。能活着坐回这张桌子，就是全部。",
                "prose_en": "There is no diploma. Returning to this table alive is the whole thing.",
                "objective": {"type": "total_return", "target": 15, "label_zh": "总收益率不低于 15%", "label_en": "Keep your total return at or above 15%"},
                "reward_zh": "桌上玩家",
                "reward_en": "Seated Player",
            },
        ],
    },
]


def get_storylines(db: Session, player: models.Player, lang: str) -> dict:
    zh = lang == "zh"
    progress_rows = {
        row.npc_key: row
        for row in db.query(models.StorylineProgress)
        .filter(models.StorylineProgress.player_id == player.id)
        .all()
    }
    result = []
    for storyline in STORYLINES:
        row = progress_rows.get(storyline["key"])
        chapter_index = row.chapter if row else 0
        total = len(storyline["chapters"])
        while chapter_index < total:
            objective = storyline["chapters"][chapter_index]["objective"]
            outcome = evaluate_objective(db, player, objective, lang)
            if not outcome["met"]:
                break
            chapter_index += 1
        if row is None:
            row = models.StorylineProgress(
                player_id=player.id,
                npc_key=storyline["key"],
                chapter=chapter_index,
            )
            db.add(row)
        elif row.chapter != chapter_index:
            row.chapter = chapter_index
        db.commit()

        chapters = []
        for index, chapter in enumerate(storyline["chapters"]):
            if index < chapter_index:
                status = "passed"
            elif index == chapter_index and chapter_index < total:
                status = "current"
            else:
                status = "locked"
            objective = None
            if status == "current":
                outcome = evaluate_objective(db, player, chapter["objective"], lang)
                objective = {
                    "label": outcome["label"],
                    "current": outcome["current"],
                    "target": outcome["target"],
                    "met": outcome["met"],
                }
            chapters.append(
                {
                    "id": chapter["id"],
                    "index": index + 1,
                    "status": status,
                    "title": chapter["title_zh"] if zh else chapter["title_en"],
                    "prose": chapter["prose_zh"] if zh else chapter["prose_en"],
                    "reward": chapter["reward_zh"] if zh else chapter["reward_en"],
                    "objective": objective,
                }
            )
        result.append(
            {
                "key": storyline["key"],
                "name": storyline["name_zh"] if zh else storyline["name_en"],
                "icon": storyline["icon"],
                "current_chapter": min(chapter_index + 1, total) if chapter_index < total else total,
                "completed": chapter_index >= total,
                "chapters": chapters,
            }
        )
    return {"storylines": result}
