"""Small in-app localization helpers for backend-generated content."""

from fastapi import Request

INDUSTRY_ZH = {
    "technology": "\u79d1\u6280",
    "healthcare": "\u533b\u7597\u5065\u5eb7",
    "energy": "\u80fd\u6e90",
    "finance": "\u91d1\u878d",
    "consumer": "\u6d88\u8d39",
}

CYCLE_ZH = {
    "bull": "\u725b\u5e02",
    "bear": "\u718a\u5e02",
    "recovery": "\u590d\u82cf",
    "recession": "\u8870\u9000",
}

COMPANY_ZH = {
    "CLSX": "\u6d77\u5149\u4fe1\u606f",
    "JYZX": "\u5bd2\u6b66\u7eaa",
    "GSLX": "\u4e2d\u9645\u65ed\u521b",
    "YHCC": "\u6c5f\u6ce2\u9f99",
    "XQGX": "\u65b0\u6613\u76db",
    "HTDL": "\u80dc\u5b8f\u79d1\u6280",
    "BCSC": "\u767e\u6d4e\u795e\u5dde",
    "BJZB": "\u5317\u65b9\u534e\u521b",
    "ZZLX": "\u5de5\u4e1a\u5bcc\u8054",
    "SCDL": "\u6caa\u7535\u80a1\u4efd",
    "HKZY": "\u6052\u745e\u533b\u836f",
    "TSXT": "\u5929\u5b5a\u901a\u4fe1",
    "MMYK": "\u7231\u5c14\u773c\u79d1",
    "MKYL": "\u8fc8\u745e\u533b\u7597",
    "YYHC": "\u836f\u660e\u5eb7\u5fb7",
    "BKZX": "\u8d1d\u8fbe\u836f\u4e1a",
    "KXHX": "\u51ef\u83b1\u82f1",
    "KCYY": "\u5eb7\u9f99\u5316\u6210",
    "ZYKY": "\u7d2b\u91d1\u77ff\u4e1a",
    "TYLC": "\u6cf0\u683c\u533b\u836f",
    "HXMY": "\u534e\u7199\u751f\u7269",
    "BYXT": "\u5317\u65b9\u7a00\u571f",
    "CHYQ": "\u4e2d\u56fd\u6d77\u6cb9",
    "TDYS": "\u94dc\u9675\u6709\u8272",
    "SZMT": "\u4e2d\u56fd\u795e\u534e",
    "JYTY": "\u6c5f\u897f\u94dc\u4e1a",
    "DZHJ": "\u5c71\u4e1c\u9ec4\u91d1",
    "DJDL": "\u957f\u6c5f\u7535\u529b",
    "LDMY": "\u6d1b\u9633\u94bc\u4e1a",
    "LPJR": "\u6307\u5357\u9488",
    "KLSY": "\u4e2d\u56fd\u77f3\u6cb9",
    "DYCW": "\u4e1c\u65b9\u8d22\u5bcc",
    "DXYZ": "\u4e1c\u65b9\u8bc1\u5238",
    "HKZT": "\u540c\u82b1\u987a",
    "ZYZQ": "\u4e2d\u4fe1\u8bc1\u5238",
    "ZXZQ": "\u62db\u5546\u8bc1\u5238",
    "JCYH": "\u5de5\u5546\u94f6\u884c",
    "DLYP": "\u4e1c\u9e4f\u996e\u6599",
    "HYBX": "\u4e2d\u56fd\u5e73\u5b89",
    "GZDQ": "\u683c\u529b\u7535\u5668",
    "ZHYH": "\u62db\u5546\u94f6\u884c",
    "HNZJ": "\u6d77\u5c14\u667a\u5bb6",
    "GHZQ": "\u56fd\u6cf0\u6d77\u901a",
    "YDQC": "\u6bd4\u4e9a\u8fea",
    "JCQC": "\u8d5b\u529b\u65af",
    "JXJD": "\u7f8e\u7684\u96c6\u56e2",
    "LJLN": "\u6cf8\u5dde\u8001\u7a96",
    "FCQN": "\u5c71\u897f\u6c7e\u9152",
    "XWFF": "\u6d77\u5929\u5473\u4e1a",
    "CYRX": "\u4f0a\u5229\u80a1\u4efd",
}

COMPANY_EN = {
    "CLSX": "Hygon Information Technology",
    "JYZX": "Cambricon Technologies",
    "GSLX": "Zhongji Innolight",
    "YHCC": "Longsys Electronics",
    "XQGX": "Eoptolink Technology",
    "HTDL": "Victory Giant Technology",
    "BCSC": "BeiGene",
    "BJZB": "NAURA Technology",
    "ZZLX": "Foxconn Industrial Internet",
    "SCDL": "WUS Printed Circuit",
    "HKZY": "Hengrui Medicine",
    "TSXT": "TFC Optical Communication",
    "MMYK": "Aier Eye Hospital",
    "MKYL": "Mindray Bio-Medical",
    "YYHC": "WuXi AppTec",
    "BKZX": "Betta Pharmaceuticals",
    "KXHX": "Asymchem Laboratories",
    "KCYY": "Pharmaron",
    "ZYKY": "Zijin Mining Group",
    "TYLC": "Hangzhou Tigermed",
    "HXMY": "Bloomage Biotech",
    "BYXT": "China Northern Rare Earth",
    "CHYQ": "CNOOC",
    "TDYS": "Tongling Nonferrous Metals",
    "SZMT": "China Shenhua Energy",
    "JYTY": "Jiangxi Copper",
    "DZHJ": "Shandong Gold Mining",
    "DJDL": "China Yangtze Power",
    "LDMY": "CMOC Group",
    "LPJR": "Beijing Compass Technology",
    "KLSY": "PetroChina",
    "DYCW": "East Money Information",
    "DXYZ": "Orient Securities",
    "HKZT": "Hithink RoyalFlush",
    "ZYZQ": "CITIC Securities",
    "ZXZQ": "China Merchants Securities",
    "JCYH": "Industrial and Commercial Bank of China",
    "DLYP": "Dongpeng Beverage",
    "HYBX": "Ping An Insurance",
    "GZDQ": "Gree Electric Appliances",
    "ZHYH": "China Merchants Bank",
    "HNZJ": "Haier Smart Home",
    "GHZQ": "Guotai Haitong Securities",
    "YDQC": "BYD Company",
    "JCQC": "Seres Group",
    "JXJD": "Midea Group",
    "LJLN": "Luzhou Laojiao",
    "FCQN": "Shanxi Xinghuacun Fen Wine Factory",
    "XWFF": "Foshan Haitian Flavouring & Food",
    "CYRX": "Inner Mongolia Yili Industrial",
}





RIVAL_ZH = {
    "Aurora Capital": "\u6781\u5149\u8d44\u672c",
    "Hawk Momentum Fund": "\u9e70\u52bf\u52a8\u91cf\u57fa\u91d1",
    "Granite Value Partners": "\u82b1\u5c97\u5ca9\u4ef7\u503c\u4f19\u4f34",
    "Sector Rotation Group": "\u884c\u4e1a\u8f6e\u52a8\u96c6\u56e2",
    "Turtle Income Trust": "\u7a33\u5065\u6536\u76ca\u4fe1\u6258",
    "Nimbus Growth Fund": "\u96e8\u4e91\u6210\u957f\u57fa\u91d1",
    "Palisade Hedge Fund": "\u6805\u680f\u5bf9\u51b2\u57fa\u91d1",
    "Cipher Quant Lab": "\u5bc6\u6587\u91cf\u5316\u5b9e\u9a8c\u5ba4",
    "Chase Retail Fund": "\u8ffd\u98ce\u6563\u6237",
    "Panic Retail Fund": "\u6050\u614c\u5272\u8089",
    "All-In Retail Fund": "\u6ee1\u4ed3\u68ad\u54c8",
    "Limit-Up Chaser Fund": "\u6253\u677f\u5ba2",
    "Knife Catcher Fund": "\u63a5\u76d8\u4fa0",
    "Follower Retail Fund": "\u8ddf\u98ce\u5927\u5988",
    "Margin Retail Fund": "\u6760\u6746\u5ba2",
    "Sleeper Retail Fund": "\u8eba\u5e73\u517b\u8001",
    "Equal-Weight Benchmark": "\u7b49\u6743\u57fa\u51c6\u6307\u6570",
}

STRATEGY_ZH = {
    "index": "\u6307\u6570",
    "momentum": "\u52a8\u91cf",
    "value": "\u4ef7\u503c",
    "rotation": "\u8f6e\u52a8",
    "low volatility": "\u4f4e\u6ce2\u52a8",
    "growth": "\u6210\u957f",
    "dynamic": "\u52a8\u6001",
    "quant": "\u91cf\u5316",
    "retail_chase": "\u8ffd\u6da8\u6740\u8dcc",
    "retail_panic": "\u6050\u614c\u79bb\u573a",
    "retail_allin": "\u6ee1\u4ed3\u68ad\u54c8",
    "retail_limit": "\u6253\u677f\u8ffd\u9ad8",
    "retail_knife": "\u63a5\u76d8\u6284\u5e95",
    "retail_follower": "\u8ddf\u98ce\u8ffd\u6da8",
    "retail_margin": "\u6760\u6746\u878d\u8d44",
    "retail_sleeper": "\u8eba\u5e73\u6301\u6709",
    "Commando of the Ningbo Floor": "\u752c\u57ce\u6562\u6b7b\u961f\u961f\u957f",
    "The Noodle Man": "\u5173\u706f\u5403\u9762\u7684\u7537\u4eba",
    "The Sack Miner": "\u9ebb\u888b\u88c5\u94b1\u7684\u77ff\u5de5",
    "The White Glove": "\u767d\u624b\u5957\u5e84\u5bb6",
    "active": "\u4e3b\u52a8",
}

ACHIEVEMENT_ZH = {
    "first_trade": ("\u7b2c\u4e00\u7b14\u4ea4\u6613", "\u5b8c\u6210\u4f60\u7684\u7b2c\u4e00\u7b14\u4e70\u5165\u3002"),
    "first_sell": ("\u5b8c\u6574\u4ea4\u6613", "\u5b8c\u6210\u4f60\u7684\u7b2c\u4e00\u7b14\u5356\u51fa\u3002"),
    "trade_10": ("\u6d3b\u8dc3\u4ea4\u6613\u8005", "\u7d2f\u8ba1\u6210\u4ea4 10 \u7b14\u3002"),
    "trade_50": ("\u6d41\u52a8\u6027\u63d0\u4f9b\u8005", "\u7d2f\u8ba1\u6210\u4ea4 50 \u7b14\u3002"),
    "trade_100": ("\u5e02\u573a\u8001\u624b", "\u7d2f\u8ba1\u6210\u4ea4 100 \u7b14\u3002"),
    "five_sectors": ("\u5206\u6563\u5e03\u5c40", "\u540c\u65f6\u6301\u6709\u5168\u90e8\u4e94\u4e2a\u884c\u4e1a\u7684\u4ed3\u4f4d\u3002"),
    "concentrated": ("\u5b64\u6ce8\u4e00\u6387", "\u67d0\u53ea\u80a1\u7968\u5360\u7ec4\u5408\u8d85\u8fc7 60%\u3002"),
    "cash_king": ("\u73b0\u91d1\u6307\u6325\u5b98", "\u7b2c 20 \u4e2a\u4ea4\u6613\u65e5\u540e\uff0c\u73b0\u91d1\u5360\u7ec4\u5408\u8d85\u8fc7 70%\u3002"),
    "value_finder": ("\u4ef7\u503c\u53d1\u73b0\u8005", "\u6301\u6709\u987e\u95ee\u8bc4\u7ea7\u4e3a\u4f4e\u4f30\u7684\u80a1\u7968\u3002"),
    "momentum_rider": ("\u52a8\u91cf\u9a91\u624b", "\u6301\u6709 20 \u65e5\u52a8\u91cf\u4e3a\u6b63\u7684\u80a1\u7968\u4e14\u8d85\u8fc7 10%\u3002"),
    "bear_survivor": ("\u718a\u5e02\u5e78\u5b58\u8005", "\u5728\u718a\u5e02\u5468\u671f\u4e2d\u5b8c\u6574\u5ea6\u8fc7\u4e00\u4e2a\u4ea4\u6613\u5468\u3002"),
    "green_day": ("\u7eff\u8272\u4e00\u5929", "\u5355\u65e5\u7ec4\u5408\u6536\u76ca\u8d85\u8fc7 1.5%\u3002"),
    "red_day": ("\u98ce\u9669\u627f\u53d7\u529b", "\u5355\u65e5\u7ec4\u5408\u4e8f\u635f\u8d85\u8fc7 2%\u3002"),
    "milestone_110k": ("\u9996\u4e2a\u91cc\u7a0b\u7891", "\u7ec4\u5408\u5e02\u503c\u8fbe\u5230 ¥110,000\u3002"),
    "milestone_150k": ("\u575a\u5b9a\u53cc\u624b", "\u7ec4\u5408\u5e02\u503c\u8fbe\u5230 ¥150,000\u3002"),
    "milestone_200k": ("\u516d\u4f4d\u6570\u4ff1\u4e50\u90e8", "\u7ec4\u5408\u5e02\u503c\u8fbe\u5230 ¥200,000\u3002"),
    "day_30": ("\u5165\u5e02\u6ee1\u6708", "\u5b8c\u6210 30 \u4e2a\u4ea4\u6613\u65e5\u3002"),
    "day_100": ("\u8d44\u6df1\u6295\u8d44\u8005", "\u5b8c\u6210 100 \u4e2a\u4ea4\u6613\u65e5\u3002"),
    "chronicle_tech": ("\u79d1\u6280\u5148\u950b", "\u5b8c\u6210\u4e00\u4e2a\u4e0e\u79d1\u6280\u4ed3\u4f4d\u6709\u5173\u7684\u7ae0\u8282\u76ee\u6807\u3002"),
    "chronicle_profit": ("\u843d\u888b\u4e3a\u5b89", "\u5b8c\u6210\u4e00\u4e2a\u4e0e\u79d1\u6280\u6536\u76ca\u6709\u5173\u7684\u7ae0\u8282\u76ee\u6807\u3002"),
    "chronicle_cash": ("\u73b0\u91d1\u5b88\u536b\u8005", "\u5b8c\u6210\u4e00\u4e2a\u4e0e\u73b0\u91d1\u4ed3\u4f4d\u6709\u5173\u7684\u7ae0\u8282\u76ee\u6807\u3002"),
    "chronicle_survivor": ("\u8d2f\u8d8a\u5468\u671f", "\u5b8c\u6210\u4e00\u4e2a\u4e0e\u603b\u6536\u76ca\u6709\u5173\u7684\u7ae0\u8282\u76ee\u6807\u3002"),
    "noodle_last": ("\u5173\u706f\u5403\u9762", "\u8d5b\u5b63\u57ab\u5e95\uff0c\u9762\u9986\u514d\u8d39\u9001\u4e00\u7897\u3002"),
    "three_peat": ("\u4e09\u8fde\u51a0", "\u8fde\u7eed\u4e09\u4e2a\u4ea4\u6613\u65e5\u6392\u540d\u7b2c\u4e00\u3002"),
    "stock_god": ("\u80a1\u7968\u5927\u624b\u5b50", "\u8fde\u7eed\u4e94\u4e2a\u4ea4\u6613\u65e5\u6392\u540d\u7b2c\u4e00\u3002"),
    "seer_3": ("\u534a\u4ed9", "\u8fde\u7eed 3 \u6b21\u5224\u65ad\u6b63\u786e\u3002"),
    "seer_5": ("\u795e\u673a\u5999\u7b97", "\u8fde\u7eed 5 \u6b21\u5224\u65ad\u6b63\u786e\u3002"),
}


def get_lang(request: Request) -> str:
    header = request.headers.get("accept-language", "")
    return "zh" if header.lower().startswith("zh") else "en"


def company_name(lang: str, ticker: str, fallback: str) -> str:
    if lang == "zh":
        return COMPANY_ZH.get(ticker, fallback)
    return COMPANY_EN.get(ticker, fallback)


def industry_label(lang: str, industry: str) -> str:
    if lang == "zh":
        return INDUSTRY_ZH.get(industry, industry)
    return industry


def cycle_label(lang: str, cycle: str) -> str:
    if lang == "zh":
        return CYCLE_ZH.get(cycle, cycle)
    return cycle


def rival_name(lang: str, name: str) -> str:
    if lang == "zh":
        if name.startswith("Retail Trader "):
            return "\u6563\u6237" + name[-2:]
        return RIVAL_ZH.get(name, name)
    return name


def strategy_label(lang: str, strategy: str) -> str:
    if lang == "zh":
        return STRATEGY_ZH.get(strategy, strategy)
    return strategy


def achievement_text(lang: str, code: str, title: str, description: str) -> tuple[str, str]:
    if lang == "zh" and code in ACHIEVEMENT_ZH:
        return ACHIEVEMENT_ZH[code]
    return title, description
