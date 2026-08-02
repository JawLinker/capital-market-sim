"""Fetch real A-share daily data and convert it into the game's snapshot format.

Source: Tencent public quote API (for simulation/learning only).
The snapshot keeps real company names and exchange codes, plus optional
fictional names for anonymized display.
"""

import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests

OUTPUT = Path(__file__).resolve().parent.parent / "app" / "data" / "a_share_snapshot.json"
REAL_NAMES = json.loads(
    (Path(__file__).resolve().parent / "real_names.json").read_text(encoding="utf-8")
)

INDEX_SYMBOL = "sh000001"
KLINE_URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
QUOTE_URL = "https://qt.gtimg.cn/q="
SINA_KLINE_URL = "https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData"
PERIODS = [
    ("2019-01-01", "2020-03-31"),
    ("2020-04-01", "2021-06-30"),
    ("2021-07-01", "2022-09-30"),
    ("2022-10-01", "2023-12-31"),
    ("2024-01-01", "2025-03-31"),
    ("2025-04-01", "2026-12-31"),
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://gu.qq.com/",
}

UNIVERSE = [
    # (internal_code, name_zh, name_en, industry, exchange code)
    ("JYZX", "纪元智芯", "EpochAI Chip", "technology", "688256"),
    ("GSLX", "光速互联", "Lightspeed Link", "technology", "300308"),
    ("XQGX", "星桥光电", "StarBridge Optic", "technology", "300502"),
    ("CLSX", "沧澜算芯", "Canglan Compute", "technology", "688041"),
    ("ZZLX", "智造互联", "SmartFab Link", "technology", "601138"),
    ("BJZB", "北疆装备", "NorthRealm Equipment", "technology", "002371"),
    ("SCDL", "申城电路", "Shencheng Circuit", "technology", "002463"),
    ("HTDL", "宏图电路", "MacroWin PCB", "technology", "300476"),
    ("TSXT", "天枢通信", "TianShu Comms", "technology", "300394"),
    ("YHCC", "云湖存储", "CloudLake Storage", "technology", "301308"),
    ("BCSC", "百川生科", "Bichuan Bio", "healthcare", "688235"),
    ("HKZY", "恒康制药", "Everwell Pharma", "healthcare", "600276"),
    ("YYHC", "药研合创", "DrugLab Alliance", "healthcare", "603259"),
    ("MKYL", "迈康医疗", "MedCare Health", "healthcare", "300760"),
    ("MMYK", "明眸眼科", "BrightVision Eye", "healthcare", "300015"),
    ("KCYY", "康成医药", "KangCheng Medicine", "healthcare", "300759"),
    ("TYLC", "泰岳临床", "TaiYue Clinical", "healthcare", "300347"),
    ("KXHX", "凯旋化学", "KaiXuan Chem", "healthcare", "002821"),
    ("BKZX", "贝康创新", "BeiKang Innovation", "healthcare", "300558"),
    ("HXMY", "华曦美妍", "HuaXi Beauty", "healthcare", "688363"),
    ("ZYKY", "紫岳矿业", "ZiYue Mining", "energy", "601899"),
    ("TDYS", "铜都有色", "Tongdu Metals", "energy", "000630"),
    ("JYTY", "江右铜业", "Jiangyou Copper", "energy", "600362"),
    ("BYXT", "北原稀土", "NorthPlain Rare", "energy", "600111"),
    ("LDMY", "洛都钼业", "Luodu Moly", "energy", "603993"),
    ("DZHJ", "岱宗黄金", "Daizong Gold", "energy", "600547"),
    ("SZMT", "神州煤炭", "Cathay Coal", "energy", "601088"),
    ("KLSY", "昆仑石油", "Kunlun Petroleum", "energy", "601857"),
    ("CHYQ", "沧海油气", "Canghai Oil & Gas", "energy", "600938"),
    ("DJDL", "大江电力", "GreatRiver Power", "energy", "600900"),
    ("DYCW", "东隅财富", "EastCorner Wealth", "finance", "300059"),
    ("HKZT", "花开智投", "Blossom Invest", "finance", "300033"),
    ("LPJR", "罗盘金融", "Compass Finance", "finance", "300803"),
    ("ZYZQ", "中岳证券", "Zhongyue Securities", "finance", "600030"),
    ("ZXZQ", "招航证券", "Zhaohang Securities", "finance", "600999"),
    ("DXYZ", "东曦证券", "Dongxi Securities", "finance", "600958"),
    ("HYBX", "海晏保险", "Haiyan Insurance", "finance", "601318"),
    ("JCYH", "金城银行", "GoldenCity Bank", "finance", "601398"),
    ("ZHYH", "招惠银行", "Zhaohui Bank", "finance", "600036"),
    ("GHZQ", "国衡证券", "Guoheng Securities", "finance", "601211"),
    ("DLYP", "东岭饮品", "Dongling Drinks", "consumer", "605499"),
    ("JCQC", "骏程汽车", "Juncheng Auto", "consumer", "601127"),
    ("YDQC", "驭电汽车", "Yudian Auto", "consumer", "002594"),
    ("JXJD", "匠心家电", "ArtisanHome", "consumer", "000333"),
    ("GZDQ", "格致电器", "Gezhi Electric", "consumer", "000651"),
    ("HNZJ", "海纳智家", "Haina Smart Home", "consumer", "600690"),
    ("FCQN", "汾川清酿", "FenRiver Clear", "consumer", "600809"),
    ("LJLN", "泸江老酿", "Lujiang Vintage", "consumer", "000568"),
    ("CYRX", "草原乳香", "PrairieMilk", "consumer", "600887"),
    ("XWFF", "鲜味坊", "FreshFlavor", "consumer", "603288"),
]


def symbol(code: str) -> str:
    prefix = "sh" if code.startswith(("6", "9")) else "sz"
    return f"{prefix}{code}"


def get_json(url: str, params: dict, tries: int = 3):
    last_error = None
    for attempt in range(tries):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=20)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1.0 * (attempt + 1))
    raise last_error


def fetch_kline(sym: str, adjusted: bool = True):
    response = requests.get(
        SINA_KLINE_URL,
        params={"symbol": sym, "scale": "240", "ma": "no", "datalen": "1800"},
        headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/"},
        timeout=25,
    )
    response.raise_for_status()
    rows = response.json()
    parsed = []
    for row in rows:
        parsed.append(
            {
                "date": row["day"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            }
        )
    return parsed


def fetch_index_series() -> list[dict]:
    response = requests.get(
        SINA_KLINE_URL,
        params={"symbol": INDEX_SYMBOL, "scale": "240", "ma": "no", "datalen": "1800"},
        headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/"},
        timeout=25,
    )
    response.raise_for_status()
    rows = response.json()
    parsed = []
    for row in rows:
        parsed.append(
            {
                "date": row["day"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            }
        )
    return parsed


def fetch_metadata(codes: list[str]):
    symbols = ",".join(symbol(code) for code in codes)
    response = requests.get(QUOTE_URL + symbols, headers=HEADERS, timeout=20)
    response.raise_for_status()
    text = response.content.decode("gbk", errors="ignore")
    result = {}
    for line in text.split(";"):
        if "=" not in line:
            continue
        fields = line.split("=", 1)[1].strip().strip('"').split("~")
        if len(fields) < 46:
            continue
        code = fields[2]
        try:
            result[code] = {
                "price": float(fields[3]),
                "pe": float(fields[39]) if fields[39] else None,
                "market_cap": float(fields[45]) * 1e8 if fields[45] else None,
            }
        except (TypeError, ValueError):
            result[code] = {}
    return result


def clamp(value, low, high):
    return max(low, min(high, value))


def main():
    print("Fetching index history...", flush=True)
    try:
        index_rows = fetch_index_series()
    except Exception:  # noqa: BLE001
        index_rows = fetch_kline(INDEX_SYMBOL, adjusted=False)
    index_ret_by_date = dict(_returns_with_dates(index_rows))
    index_rets = [ret for _, ret in index_ret_by_date.items()]
    index_meta = {
        "daily_volatility": round(_std(index_rets), 5),
        "avg_abs_return": round(statistics.mean([abs(r) for r in index_rets]), 5),
        "days": len(index_rets),
    }
    index_series = [
        {
            "d": row["date"],
            "o": round(row["open"], 2),
            "h": round(row["high"], 2),
            "l": round(row["low"], 2),
            "c": round(row["close"], 2),
            "v": int(row["volume"]),
        }
        for row in index_rows
    ]

    codes = [entry[4] for entry in UNIVERSE]
    print("Fetching metadata for", len(codes), "stocks...", flush=True)
    metadata = fetch_metadata(codes)

    stocks = []
    failures = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(_build_stock, entry, metadata, index_ret_by_date): entry
            for entry in UNIVERSE
        }
        for index, future in enumerate(as_completed(futures), start=1):
            ticker, _, name, _, code = futures[future]
            try:
                stocks.append(future.result())
                print(f"[{index:02d}/50] ok {ticker} {name}", flush=True)
            except Exception as exc:  # noqa: BLE001
                failures.append((code, str(exc)))
                print(f"[{index:02d}/50] FAIL {code} {name}: {exc}", flush=True)

    snapshot = {
        "meta": {
            "source": "Tencent public quote API (learning/simulation only)",
            "fetched_at": datetime.now().isoformat(timespec="seconds"),
            "index": index_meta,
            "index_series": index_series,
            "universe_size": len(stocks),
        },
        "stocks": stocks,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if len(stocks) < 40:
        raise RuntimeError(f"refusing to write snapshot with only {len(stocks)} stocks")
    temp_output = OUTPUT.with_suffix(".json.tmp")
    temp_output.write_text(
        json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    temp_output.replace(OUTPUT)
    print("Saved", OUTPUT, "stocks:", len(stocks), flush=True)
    print("Index meta:", index_meta, flush=True)
    if failures:
        print("Failures:", failures)


def _build_stock(entry, metadata, index_ret_by_date) -> dict:
    ticker, name, name_en, industry, code = entry
    rows = fetch_kline(symbol(code))
    if len(rows) < 200:
        raise ValueError(f"only {len(rows)} rows")
    closes = [row["close"] for row in rows]
    rets = _returns_from_rows(rows)
    real_vol = _std(rets)
    beta = _beta(_returns_with_dates(rows), index_ret_by_date)

    meta = metadata.get(code, {})
    real_price = meta.get("price") or closes[-1]
    real_pe = meta.get("pe")
    real_mcap = meta.get("market_cap")

    base_price = round(real_price, 2)

    avg_volume = int(statistics.mean([row["volume"] for row in rows]))
    pe = clamp(real_pe or 20.0, 4.0, 90.0)
    if real_mcap:
        game_mcap = real_mcap
    else:
        game_mcap = base_price * 2_000_000_000

    series = []
    for row in rows:
        series.append(
            {
                "d": row["date"],
                "o": round(row["open"], 2),
                "h": round(row["high"], 2),
                "l": round(row["low"], 2),
                "c": round(row["close"], 2),
                "v": int(row["volume"]),
            }
        )

    scaled = [row["c"] for row in series]
    recent = scaled[-252:]
    return {
        "ticker": ticker,
        "name": name,
        "real_name": REAL_NAMES.get(code, {}).get("zh", name),
        "real_name_en": REAL_NAMES.get(code, {}).get("en", name_en),
        "name_en": name_en,
        "industry": industry,
        "real_code": code,
        "base_price": base_price,
        "volatility": round(min(0.06, real_vol * 1.25), 4),
        "beta": round(clamp(beta, 0.3, 2.0), 3),
        "market_cap": round(game_mcap, 0),
        "pe_ratio": round(pe, 2),
        "avg_volume": avg_volume,
        "fifty_two_week_high": round(max(recent), 2),
        "fifty_two_week_low": round(min(recent), 2),
        "momentum_20d": round(scaled[-1] / scaled[-21] - 1.0, 6),
        "momentum_60d": round(scaled[-1] / scaled[-61] - 1.0, 6),
        "last_daily_ret": round(rets[-1], 6),
        "series": series,
    }


def _returns_with_dates(rows: list[dict]) -> list[tuple[str, float]]:
    return [
        (rows[i]["date"], rows[i]["close"] / rows[i - 1]["close"] - 1.0)
        for i in range(1, len(rows))
    ]


def _returns_from_rows(rows: list[dict]) -> list[float]:
    return [rows[i]["close"] / rows[i - 1]["close"] - 1.0 for i in range(1, len(rows))]


def _std(values: list[float]) -> float:
    return statistics.pstdev(values) if values else 0.0


def _beta(
    stock_rets_dated: list[tuple[str, float]],
    index_ret_by_date: dict[str, float],
) -> float:
    paired = [
        (ret, index_ret_by_date[day])
        for day, ret in stock_rets_dated
        if day in index_ret_by_date
    ]
    if len(paired) < 60:
        return 1.0
    stock_vals = [pair[0] for pair in paired]
    index_vals = [pair[1] for pair in paired]
    var_index = statistics.pvariance(index_vals)
    if var_index == 0:
        return 1.0
    cov = sum(
        (a - statistics.mean(stock_vals)) * (b - statistics.mean(index_vals))
        for a, b in paired
    ) / len(paired)
    return cov / var_index


if __name__ == "__main__":
    main()
