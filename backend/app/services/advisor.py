import re
from statistics import median

from sqlalchemy.orm import Session

from .. import models
from ..i18n import industry_label
from .portfolio import allocation, holdings_detail, portfolio_summary


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _industry_pe(db: Session, industry: str) -> float:
    values = [
        row[0]
        for row in db.query(models.Stock.pe_ratio)
        .filter(models.Stock.industry == industry)
        .all()
    ]
    return median(values) if values else 20.0


def _valuation_score(
    stock: models.Stock, industry_median_pe: float, lang: str = "en"
) -> tuple[int, str, str]:
    pe_score = 50.0 - (stock.pe_ratio - industry_median_pe) / industry_median_pe * 40.0
    span = max(0.01, stock.fifty_two_week_high - stock.fifty_two_week_low)
    position = (stock.price - stock.fifty_two_week_low) / span
    range_score = (1.0 - position) * 100.0
    score = _clamp_score(pe_score * 0.55 + range_score * 0.45)
    industry = industry_label(lang, stock.industry)
    if lang == "zh":
        if score >= 70:
            label = "低估"
            detail = f"市盈率 {stock.pe_ratio:.1f} 低于{industry}行业中位数 {industry_median_pe:.1f}，且股价位于52周区间的低位。"
        elif score >= 40:
            label = "估值合理"
            detail = f"市盈率 {stock.pe_ratio:.1f} 接近{industry}行业中位数 {industry_median_pe:.1f}，市场给出的估值较为理性。"
        else:
            label = "高估"
            detail = f"市盈率 {stock.pe_ratio:.1f} 高于{industry}行业中位数 {industry_median_pe:.1f}，且股价接近52周高点，容错空间有限。"
        return score, label, detail

    if score >= 70:
        label = "Undervalued"
        detail = f"P/E of {stock.pe_ratio:.1f} sits below the {stock.industry} median of {industry_median_pe:.1f} and the price is in the lower part of its 52-week range."
    elif score >= 40:
        label = "Fairly valued"
        detail = f"The P/E of {stock.pe_ratio:.1f} is close to the {stock.industry} median of {industry_median_pe:.1f}, suggesting the market is paying a reasonable multiple."
    else:
        label = "Overvalued"
        detail = f"A P/E of {stock.pe_ratio:.1f} above the {stock.industry} median of {industry_median_pe:.1f} plus a price near the 52-week high leaves little margin for error."
    return score, label, detail


def _momentum_score(stock: models.Stock, lang: str = "en") -> tuple[int, str, str]:
    m20 = stock.momentum_20d or 0.0
    m60 = stock.momentum_60d or 0.0
    raw = m20 * 140.0 + m60 * 60.0 + 50.0
    score = _clamp_score(raw)
    if lang == "zh":
        if score >= 68:
            label = "动能强劲"
            detail = f"20日收益 {m20 * 100:.1f}%、60日收益 {m60 * 100:.1f}%，买方占据主导。"
        elif score >= 35:
            label = "动能中性"
            detail = f"20日收益 {m20 * 100:.1f}%、60日收益 {m60 * 100:.1f}%，股价处于横盘震荡。"
        else:
            label = "动能偏弱"
            detail = f"20日收益 {m20 * 100:.1f}%、60日收益 {m60 * 100:.1f}%，卖方仍占优势。"
        return score, label, detail

    if score >= 68:
        label = "Strong momentum"
        detail = f"20-day return of {m20 * 100:.1f}% and 60-day return of {m60 * 100:.1f}% show buyers in control."
    elif score >= 35:
        label = "Neutral momentum"
        detail = f"Returns of {m20 * 100:.1f}% over 20 days and {m60 * 100:.1f}% over 60 days put the stock in a sideways trend."
    else:
        label = "Weak momentum"
        detail = f"Negative trends of {m20 * 100:.1f}% (20d) and {m60 * 100:.1f}% (60d) suggest sellers remain dominant."
    return score, label, detail


def _risk_score(stock: models.Stock, lang: str = "en") -> tuple[int, str, str]:
    drawdown = (stock.price - stock.fifty_two_week_high) / stock.fifty_two_week_high
    raw = 100.0 - (stock.volatility * 100.0 * 7.5 + stock.beta * 16.0 + max(0.0, -drawdown) * 100.0 * 1.3)
    score = _clamp_score(raw)
    if lang == "zh":
        if score >= 66:
            label = "低风险"
            detail = f"日波动率 {stock.volatility * 100:.1f}%、beta {stock.beta:.2f}，属于组合中较稳健的仓位。"
        elif score >= 38:
            label = "中等风险"
            detail = f"日波动率 {stock.volatility * 100:.1f}%、beta {stock.beta:.2f}，日内波动较为明显。"
        else:
            label = "高风险"
            detail = f"日波动率 {stock.volatility * 100:.1f}%、beta {stock.beta:.2f}，且距52周高点回撤 {abs(drawdown) * 100:.0f}%，下行暴露较大。"
        return score, label, detail

    if score >= 66:
        label = "Low risk"
        detail = f"Daily volatility of {stock.volatility * 100:.1f}% and beta of {stock.beta:.2f} make this one of the steadier positions."
    elif score >= 38:
        label = "Moderate risk"
        detail = f"Volatility of {stock.volatility * 100:.1f}% and beta of {stock.beta:.2f} imply meaningful day-to-day swings."
    else:
        label = "High risk"
        detail = f"Volatility of {stock.volatility * 100:.1f}%, beta of {stock.beta:.2f}, and a {abs(drawdown) * 100:.0f}% drawdown from the 52-week high create large downside exposure."
    return score, label, detail


def portfolio_report(db: Session, player: models.Player, lang: str = "en") -> dict:
    summary = portfolio_summary(db, player)
    holdings = holdings_detail(db, player, lang)
    allocation_data = allocation(db, player)

    holding_analyses = []
    for item in holdings:
        stock = db.query(models.Stock).filter(models.Stock.ticker == item["ticker"]).first()
        median_pe = _industry_pe(db, stock.industry)
        val_score, val_label, val_detail = _valuation_score(stock, median_pe, lang)
        mom_score, mom_label, mom_detail = _momentum_score(stock, lang)
        risk_score, risk_label, risk_detail = _risk_score(stock, lang)
        composite = _clamp_score(val_score * 0.3 + mom_score * 0.3 + risk_score * 0.25 + 60 * 0.15)
        holding_analyses.append(
            {
                "ticker": stock.ticker,
                "name": item["name"],
                "industry": item["industry"],
                "weight": item["weight"],
                "price": stock.price,
                "pe_ratio": stock.pe_ratio,
                "volatility": stock.volatility,
                "beta": stock.beta,
                "composite_score": composite,
                "dimensions": {
                    "valuation": {"score": val_score, "label": val_label, "detail": val_detail},
                    "momentum": {"score": mom_score, "label": mom_label, "detail": mom_detail},
                    "risk": {"score": risk_score, "label": risk_label, "detail": risk_detail},
                },
            }
        )

    holding_analyses.sort(key=lambda x: -x["composite_score"])
    diversification = _diversification_report(db, player, summary, allocation_data, lang)
    dimensions = {
        "valuation": _aggregate(holding_analyses, "valuation", lang),
        "momentum": _aggregate(holding_analyses, "momentum", lang),
        "risk": _aggregate(holding_analyses, "risk", lang),
        "diversification": {
            "score": diversification["score"],
            "label": diversification["label"],
            "detail": diversification["summary"],
        },
    }
    health = _clamp_score(
        dimensions["valuation"]["score"] * 0.2
        + dimensions["momentum"]["score"] * 0.25
        + dimensions["risk"]["score"] * 0.25
        + dimensions["diversification"]["score"] * 0.3
    )

    education = (
        [
            "估值是比较你为每一美元盈利支付的价格与行业通常支付的价格。",
            "动量衡量最近买卖双方谁在主导价格趋势。",
            "风险评分综合日波动率、市场敏感度以及自近期高点的回撤。",
            "分散化奖励跨行业配置，并惩罚过大的单一仓位。",
        ]
        if lang == "zh"
        else [
            "Valuation compares what you pay per dollar of earnings with what the industry typically pays.",
            "Momentum measures how recently buyers or sellers have controlled the price trend.",
            "Risk scores account for daily volatility, market sensitivity, and drawdown from recent highs.",
            "Diversification rewards spread across sectors and penalizes oversized single positions.",
        ]
    )

    return {
        "health_score": health,
        "summary": summary,
        "dimensions": dimensions,
        "holdings": holding_analyses,
        "allocation": allocation_data,
        "education": education,
    }


def _aggregate(holdings: list[dict], dimension: str, lang: str = "en") -> dict:
    if not holdings:
        if lang == "zh":
            return {
                "score": 50,
                "label": "暂无持仓",
                "detail": "建立仓位后才能获得评分。",
            }
        return {"score": 50, "label": "No holdings", "detail": "Build a position to receive a score."}
    scores = [item["dimensions"][dimension]["score"] for item in holdings]
    weighted = sum(
        item["weight"] / 100.0 * item["dimensions"][dimension]["score"] for item in holdings
    )
    score = _clamp_score(weighted if sum(item["weight"] for item in holdings) > 0 else sum(scores) / len(scores))
    sample = max(holdings, key=lambda item: item["dimensions"][dimension]["score"])
    return {
        "score": score,
        "label": sample["dimensions"][dimension]["label"],
        "detail": sample["dimensions"][dimension]["detail"],
        "best": {"name": sample["name"], "score": sample["dimensions"][dimension]["score"]},
    }


def _diversification_report(
    db: Session,
    player: models.Player,
    summary: dict,
    allocation_data: dict,
    lang: str = "en",
) -> dict:
    breakdown = allocation_data["breakdown"]
    sector_count = len(breakdown)
    weights = [row["weight"] / 100.0 for row in breakdown]
    hhi = sum(w * w for w in weights)
    cash_ratio = summary["cash"] / summary["value"] if summary["value"] else 1.0
    coverage_score = sector_count / 5.0 * 40.0
    concentration_score = max(0.0, (1.0 - hhi)) * 45.0
    cash_score = 15.0 if 0.05 <= cash_ratio <= 0.55 else (-20.0 if cash_ratio > 0.8 else 0.0)
    score = _clamp_score(coverage_score + concentration_score + cash_score + 10.0)

    if score >= 70:
        label = "分散良好" if lang == "zh" else "Well diversified"
    elif score >= 45:
        label = "分散适中" if lang == "zh" else "Moderately diversified"
    else:
        label = "较为集中" if lang == "zh" else "Concentrated"

    if sector_count == 0:
        summary_text = (
            "你目前 100% 持有现金，规避了市场风险，但也限制了长期增长。"
            if lang == "zh"
            else "You are 100% in cash, which removes market risk but also caps long-term growth."
        )
    else:
        top = breakdown[0]
        if lang == "zh":
            summary_text = (
                f"当前覆盖 {sector_count} 个行业，{industry_label(lang, top['industry'])}是最大敞口，"
                f"占投入资本的 {top['weight']:.0f}%。现金占总资产 {cash_ratio * 100:.0f}%。"
            )
        else:
            summary_text = (
                f"Across {sector_count} sectors, {top['industry'].title()} is your largest exposure at "
                f"{top['weight']:.0f}% of invested capital. Cash is {cash_ratio * 100:.0f}% of total value."
            )
    return {
        "score": score,
        "label": label,
        "summary": summary_text,
        "sector_count": sector_count,
        "hhi": round(hhi, 4),
        "cash_ratio": round(cash_ratio, 4),
    }


def chat(db: Session, player: models.Player, message: str, lang: str = "en") -> dict:
    report = portfolio_report(db, player, lang)
    summary = report["summary"]
    text = message.lower()
    answers = []

    if re.search(r"valu|pe |p/e|cheap|expensive|overpriced|估值|市盈|便宜|贵", text):
        best = report["holdings"][0] if report["holdings"] else None
        if best:
            dim = best["dimensions"]["valuation"]
            answers.append(
                f"估值方面，{best['name']} 得分 {dim['score']}/100：{dim['label']}。{dim['detail']}"
                if lang == "zh"
                else f"On valuation, {best['name']} scores {dim['score']}/100: {dim['label']}. {dim['detail']}"
            )
        else:
            answers.append(
                "估值分析需要有持仓才有意义。买入股票后，我可以将其市盈率与行业进行比较。"
                if lang == "zh"
                else "Valuation is only meaningful with a position. Buy a stock and I can compare its P/E with its industry."
            )

    if re.search(r"momentum|trend|moving|动能|趋势", text):
        if report["holdings"]:
            best = max(report["holdings"], key=lambda x: x["dimensions"]["momentum"]["score"])
            dim = best["dimensions"]["momentum"]
            answers.append(
                f"你的持仓中趋势最强的是 {best['name']}，动能得分 {dim['score']}/100：{dim['label']}。{dim['detail']}"
                if lang == "zh"
                else f"The strongest trend in your book is {best['name']} with a momentum score of {dim['score']}/100: {dim['label']}. {dim['detail']}"
            )
        else:
            answers.append(
                "动量衡量价格最近的方向。目前没有持仓，暂时无法评分。"
                if lang == "zh"
                else "Momentum measures the recent direction of price. With no holdings, I have nothing to score yet."
            )

    if re.search(r"risk|volatil|beta|safe|dangerous|风险|波动|安全|危险", text):
        riskiest = sorted(
            report["holdings"], key=lambda x: x["dimensions"]["risk"]["score"]
        )
        if riskiest:
            item = riskiest[0]
            dim = item["dimensions"]["risk"]
            answers.append(
                f"风险最高的持仓是 {item['name']}，得分 {dim['score']}/100：{dim['label']}。{dim['detail']}"
                if lang == "zh"
                else f"Highest risk: {item['name']} scores {dim['score']}/100. {dim['label']}. {dim['detail']}"
            )
        else:
            answers.append(
                "现金没有市场风险，但在本模拟中也不产生收益。"
                if lang == "zh"
                else "Cash has no market risk, but it also earns no return in this simulation."
            )

    if re.search(r"diversif|sector|concentrat|allocation|分散|行业|集中|配置", text):
        div = report["dimensions"]["diversification"]
        answers.append(
            f"分散化得分 {div['score']}/100：{div['label']}。{div['detail']}"
            if lang == "zh"
            else f"Diversification scores {div['score']}/100: {div['label']}. {div['detail']}"
        )

    if re.search(r"cash|idle|dry powder|现金|闲置", text):
        answers.append(
            f"你目前持有现金 ${summary['cash']:,.0f}，占总资产 {summary['cash'] / summary['value'] * 100:.0f}%。现金能抵御回撤，但也会拖累复利增长。"
            if lang == "zh"
            else f"You currently hold ${summary['cash']:,.0f} in cash, {summary['cash'] / summary['value'] * 100:.0f}% of total value. Cash protects against drawdowns but drags on compound growth."
        )

    if re.search(r"buy|should i|买入|买什么|应该", text):
        if report["holdings"]:
            top = report["holdings"][0]
            answers.append(
                f"我评分最高的持仓是 {top['name']}，综合得分 {top['composite_score']}/100。继续加仓前建议先看估值与风险卡片；均衡的组合通常好过追逐单一标的。"
                if lang == "zh"
                else f"My top-rated holding is {top['name']} at {top['composite_score']}/100. Before buying more, check the valuation and risk cards; a balanced book usually beats chasing one name."
            )
        else:
            answers.append(
                "手握 ¥100,000 现金，合理的起步是在至少三个行业各建少量仓位，并控制单只股票占比。"
                if lang == "zh"
                else "With ¥100,000 in cash, a sensible start is a handful of positions across at least three sectors, sizing each so no single stock dominates the book."
            )

    if re.search(r"sell|trim|reduce|卖出|减仓|止盈|止损", text):
        big = [h for h in report["holdings"] if h["weight"] > 30]
        if big:
            for item in big:
                answers.append(
                    f"{item['name']} 占组合 {item['weight']:.0f}%。即使趋势看起来很强，减仓过大赢家也能降低集中风险。"
                    if lang == "zh"
                    else f"{item['name']} is {item['weight']:.0f}% of your book. Trimming oversized winners reduces concentration risk, even when the trend looks strong."
                )
        else:
            answers.append(
                "目前没有单一持仓超过组合的 30%，集中度并未迫使你卖出。"
                if lang == "zh"
                else "No single holding exceeds 30% of your portfolio, so concentration is not forcing a sale right now."
            )

    if not answers:
        answers.append(
            f"你的组合市值 ¥{summary['value']:,.0f}，健康评分 {report['health_score']}/100。可以问我估值、动量、风险、分散化、现金，以及买什么或卖什么。"
            if lang == "zh"
            else f"Your portfolio is worth ¥{summary['value']:,.0f} with a health score of {report['health_score']}/100. Ask me about valuation, momentum, risk, diversification, cash, or what to buy or sell."
        )

    return {
        "reply": " ".join(answers),
        "health_score": report["health_score"],
        "ticker_mentions": [h["name"] for h in report["holdings"][:3]],
    }
