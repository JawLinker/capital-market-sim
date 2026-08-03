import { useEffect, useMemo, useState } from "react";
import { Newspaper, Search } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";
import {
  compactMoney,
  compactNumber,
  industryColor,
  money,
  percent,
  toneClass,
} from "../../utils/format.js";
import PriceChart from "../charts/PriceChart.jsx";
import OrderPanel from "../OrderPanel.jsx";
import { Badge, Change, MarketCapCell, VolumeCell } from "../ui.jsx";

const SORT_KEYS = {
  ticker: (a, b) => a.ticker.localeCompare(b.ticker),
  price: (a, b) => b.price - a.price,
  change: (a, b) => b.change_pct - a.change_pct,
  market_cap: (a, b) => b.market_cap - a.market_cap,
  volume: (a, b) => b.volume - a.volume,
};

export default function MarketView() {
  const {
    stocks,
    quote,
    history,
    news,
    selectedTicker,
    selectTicker,
    transactions,
    gameState,
    t,
    autoPlay,
  } = useApp();
  const [search, setSearch] = useState("");
  const [intradayPrice, setIntradayPrice] = useState(0);
  const [industry, setIndustry] = useState("all");
  const [sortKey, setSortKey] = useState("ticker");

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    const rows = stocks.filter(
      (stock) =>
        (industry === "all" || stock.industry === industry) &&
        (!term || stock.ticker.toLowerCase().includes(term) || stock.name.toLowerCase().includes(term))
    );
    return [...rows].sort(SORT_KEYS[sortKey] || SORT_KEYS.ticker);
  }, [stocks, search, industry, sortKey]);

  const industries = useMemo(
    () => ["all", ...new Set(stocks.map((stock) => stock.industry))],
    [stocks]
  );

  const tradeMarkers = useMemo(() => {
    if (!quote || !history || !transactions || !gameState?.market) return [];
    const currentDay = gameState.market.day;
    const dateByDay = new Map();
    history.forEach((point, index) => {
      dateByDay.set(currentDay - (history.length - 1 - index), point.date);
    });
    const seen = new Set();
    const markers = [];
    for (const tx of transactions) {
      if (tx.ticker !== quote.ticker) continue;
      const date = dateByDay.get(tx.day);
      if (!date) continue;
      const key = `${date}:${tx.action}`;
      if (seen.has(key)) continue;
      seen.add(key);
      const isBuy = tx.action === "buy";
      markers.push({
        time: date,
        position: isBuy ? "belowBar" : "aboveBar",
        color: isBuy ? "#22c55e" : "#ef4444",
        shape: isBuy ? "arrowUp" : "arrowDown",
        text: isBuy ? "B" : "S",
      });
    }
    markers.sort((a, b) => (a.time < b.time ? -1 : 1));
    return markers;
  }, [quote, history, transactions, gameState]);

  useEffect(() => {
    setIntradayPrice(quote?.price || 0);
  }, [quote?.price]);

  useEffect(() => {
    if (!autoPlay) return undefined;
    const timer = window.setInterval(() => {
      setIntradayPrice((current) => {
        const base = quote?.price || current;
        const band = base * 0.02;
        const next = current + (Math.random() - 0.5) * base * 0.004;
        return Math.max(base - band, Math.min(base + band, next));
      });
    }, 1500);
    return () => window.clearInterval(timer);
  }, [autoPlay, quote?.price]);

  return (
    <div className="grid h-full grid-cols-1 gap-4 p-4 lg:grid-cols-[minmax(0,1fr)_400px] lg:p-5">
      <section className="panel flex min-h-0 flex-col overflow-hidden">
        <div className="panel-header gap-3">
          <div>
            <h2 className="text-sm font-semibold text-parch-100">{t("market.universeTitle")}</h2>
            <p className="mt-0.5 text-xs text-parch-600">{t("market.universeDetail")}</p>
          </div>
          <div className="ml-auto flex w-full max-w-md items-center gap-2">
            <div className="relative flex-1">
              <Search size={14} className="absolute left-2.5 top-2.5 text-parch-600" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder={t("market.search")}
                className="input pl-8"
              />
            </div>
            <select
              value={industry}
              onChange={(event) => setIndustry(event.target.value)}
              className="input w-36 capitalize"
            >
              {industries.map((item) => (
                <option key={item} value={item}>
                  {item === "all" ? t("market.allIndustries") : t(`industry.${item}`)}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="min-h-0 flex-1 overflow-auto">
          <table className="w-full min-w-[760px] border-collapse">
            <thead className="sticky top-0 z-10 bg-ink-800">
              <tr>
                <th className="th">{t("market.colSymbol")}</th>
                <th className="th">{t("market.colCompany")}</th>
                <th className="th cursor-pointer" onClick={() => setSortKey("price")}>
                  {t("market.colPrice")} {sortKey === "price" ? "↓" : ""}
                </th>
                <th className="th cursor-pointer" onClick={() => setSortKey("change")}>
                  {t("market.colChg")} {sortKey === "change" ? "↓" : ""}
                </th>
                <th className="th cursor-pointer" onClick={() => setSortKey("volume")}>
                  {t("market.colVolume")} {sortKey === "volume" ? "↓" : ""}
                </th>
                <th className="th">{t("market.colPe")}</th>
                <th className="th cursor-pointer" onClick={() => setSortKey("market_cap")}>
                  {t("market.colCap")} {sortKey === "market_cap" ? "↓" : ""}
                </th>
                <th className="th">{t("market.colMom")}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((stock) => (
                <tr
                  key={stock.ticker}
                  onClick={() => selectTicker(stock.ticker)}
                  className={`row-hover ${selectedTicker === stock.ticker ? "bg-ink-700/60" : ""}`}
                >
                  <td className="td">
                    <div className="flex items-center gap-2">
                      <span
                        className="h-1.5 w-1.5 shrink-0 rounded-full"
                        style={{ backgroundColor: industryColor(stock.industry) }}
                      />
                      <span className="max-w-[170px] truncate font-semibold text-parch-100">
                        {stock.name}
                      </span>
                    </div>
                  </td>
                  <td className="td">
                    <span className="text-parch-300">{t(`industry.${stock.industry}`)}</span>
                  </td>
                  <td className="td font-semibold text-parch-100">{money(stock.price)}</td>
                  <td className="td">
                    <Change value={stock.change_pct} />
                  </td>
                  <td className="td"><VolumeCell value={stock.volume} /></td>
                  <td className="td text-parch-300">{stock.pe_ratio.toFixed(1)}</td>
                  <td className="td"><MarketCapCell value={stock.market_cap} /></td>
                  <td className="td">
                    <span className={`tabular ${toneClass(stock.momentum_20d * 100)}`}>
                      {percent(stock.momentum_20d * 100)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="flex min-h-0 flex-col gap-4 overflow-y-auto lg:h-full">
        {quote ? (
          <>
            <div className="panel">
              <div className="panel-header">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h2 className="truncate text-base font-bold text-parch-100">{quote.name}</h2>
                    <Badge
                      className="border-ink-500/50 capitalize text-parch-500"
                    >
                      {t(`industry.${quote.industry}`)}
                    </Badge>
                    {quote.limit_up ? (
                      <Badge className="border-mint/50 bg-mint/15 text-mint">
                        {t("market.limitUp")}
                      </Badge>
                    ) : null}
                    {quote.limit_down ? (
                      <Badge className="border-risk/50 bg-risk/15 text-risk">
                        {t("market.limitDown")}
                      </Badge>
                    ) : null}
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    <p className="text-xl font-bold tabular text-parch-100">{money(quote.price)}</p>
                    {autoPlay ? (
                      <span className="rounded-[3px] border border-brass/40 bg-brass/10 px-1.5 py-0.5 text-[10px] font-semibold tabular text-brass">
                        {t("market.intraday")} {money(intradayPrice)}
                      </span>
                    ) : null}
                    {Math.abs(quote.player_impact || 0) > 0.0001 ? (
                      <span
                        className={`rounded-[3px] border px-1.5 py-0.5 text-[10px] font-semibold tabular ${
                          quote.player_impact > 0
                            ? "border-mint/40 bg-mint/10 text-mint"
                            : "border-risk/40 bg-risk/10 text-risk"
                        }`}
                        title={t("market.playerImpact")}
                      >
                        {t("market.playerImpact")}{" "}
                        {quote.player_impact > 0 ? "+" : ""}
                        {(quote.player_impact * 100).toFixed(2)}%
                      </span>
                    ) : null}
                  </div>
                  <p className={`text-xs font-semibold tabular ${toneClass(quote.change_pct)}`}>
                    {quote.change_pct > 0 ? "+" : ""}{quote.change_pct.toFixed(2)}% {t("market.today")}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-px border-b border-ink-600/60 bg-ink-600/60 text-center sm:grid-cols-6">
                {[
                  [t("market.quoteOpen"), money(quote.open)],
                  [t("market.quoteHigh"), money(quote.high)],
                  [t("market.quoteLow"), money(quote.low)],
                  [t("market.quoteVolume"), quote.volume.toLocaleString()],
                  [t("market.quotePe"), quote.pe_ratio.toFixed(1)],
                  [t("market.quoteBeta"), quote.beta.toFixed(2)],
                  [t("market.quoteBid"), money(quote.bid)],
                  [t("market.quoteAsk"), money(quote.ask)],
                  [t("market.quoteDepth"), compactNumber(quote.bid_depth)],
                ].map(([label, value]) => (
                  <div key={label} className="bg-ink-800 px-2 py-2">
                    <p className="text-[10px] uppercase tracking-wide text-parch-600">{label}</p>
                    <p className="mt-0.5 truncate text-xs font-semibold tabular text-parch-200">{value}</p>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-2 gap-px bg-ink-600/60 text-center sm:grid-cols-4">
                {[
                  [t("market.quoteCap"), compactMoney(quote.market_cap)],
                  [t("market.quoteHigh52"), money(quote.fifty_two_week_high)],
                  [t("market.quoteLow52"), money(quote.fifty_two_week_low)],
                  [t("market.quoteMom"), percent(quote.momentum_20d * 100)],
                ].map(([label, value]) => (
                  <div key={label} className="bg-ink-800 px-2 py-2">
                    <p className="text-[10px] uppercase tracking-wide text-parch-600">{label}</p>
                    <p className="mt-0.5 truncate text-xs font-semibold tabular text-parch-200">{value}</p>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-2 gap-px bg-ink-600/60 text-center sm:grid-cols-4">
                {[
                  [t("market.quoteEps"), quote.eps_estimate?.toFixed(2) ?? "—"],
                  [
                    t("market.quoteNext"),
                    quote.next_earnings_day != null
                      ? t("dashboard.day", { day: quote.next_earnings_day })
                      : "—",
                  ],
                  [
                    t("market.quoteSurprise"),
                    <span key="surprise" className={toneClass(quote.last_surprise_pct)}>
                      {percent(quote.last_surprise_pct)}
                    </span>,
                  ],
                  [
                    t("market.quoteBotFlow"),
                    <span key="flow" className={toneClass(quote.bot_net_flow)}>
                      {money(quote.bot_net_flow)}
                    </span>,
                  ],
                ].map(([label, value]) => (
                  <div key={label} className="bg-ink-800 px-2 py-2">
                    <p className="text-[10px] uppercase tracking-wide text-parch-600">{label}</p>
                    <p className="mt-0.5 truncate text-xs font-semibold tabular text-parch-200">{value}</p>
                  </div>
                ))}
              </div>
              <div className="p-2">
                <div className="mb-1 flex items-center justify-end gap-3 px-1 text-[10px] font-medium text-parch-600">
                  <span>
                    <span className="mr-1 font-bold text-mint">B</span>
                    {t("market.markerBuy")}
                  </span>
                  <span>
                    <span className="mr-1 font-bold text-risk">S</span>
                    {t("market.markerSell")}
                  </span>
                </div>
                <PriceChart data={history} height={300} markers={tradeMarkers} />
              </div>
            </div>

            <OrderPanel stock={quote} />

            <div className="panel">
              <div className="panel-header">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-parch-100">
                  <Newspaper size={15} className="text-parch-600" /> {t("market.newsFeed")}
                </h3>
              </div>
              <ul className="max-h-72 divide-y divide-ink-600/50 overflow-y-auto">
                {(news || []).slice(-10).reverse().map((event) => (
                  <li key={event.id} className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <Badge
                        className={
                          event.category === "positive"
                            ? "border-mint/40 bg-mint/10 text-mint"
                            : event.category === "negative"
                              ? "border-risk/40 bg-risk/10 text-risk"
                              : "border-slate-500/40 bg-slate-500/10 text-parch-300"
                        }
                      >
                        {t(`news.${event.category}`)}
                      </Badge>
                      <span className="text-[10px] uppercase text-parch-600">{t(`news.scope.${event.scope}`)}</span>
                      {event.ticker ? (
                        <span className="text-[10px] font-semibold text-sky">
                          {event.company || event.ticker}
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-1 text-xs font-medium leading-4 text-parch-200">{event.headline}</p>
                    <p className="mt-1 text-[11px] leading-4 text-parch-600">{event.summary}</p>
                  </li>
                ))}
                {(news || []).length === 0 ? (
                  <li className="px-4 py-6 text-center text-xs text-parch-600">
                    {t("market.advanceForNews")}
                  </li>
                ) : null}
              </ul>
            </div>
          </>
        ) : (
          <div className="panel flex flex-1 items-center justify-center p-8 text-sm text-parch-600">
            {t("market.selectStock")}
          </div>
        )}
      </section>
    </div>
  );
}
