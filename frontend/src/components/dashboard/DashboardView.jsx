import { useMemo } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  Banknote,
  Briefcase,
  Newspaper,
  TrendingUp,
  Wallet,
} from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";
import { industryColor, money, percent, toneClass } from "../../utils/format.js";
import LineChart from "../charts/LineChart.jsx";
import DonutChart from "../charts/DonutChart.jsx";
import { Badge, Change, EmptyState, SectionTitle, StatCard } from "../ui.jsx";

export default function DashboardView() {
  const {
    gameState,
    portfolio,
    news,
    stocks,
    indexHistory,
    selectTicker,
    playerActivity,
    t,
  } = useApp();
  const summary = portfolio?.summary;
  const market = gameState?.market;
  const stockMap = useMemo(
    () => Object.fromEntries(stocks.map((stock) => [stock.ticker, stock])),
    [stocks]
  );

  const performanceSeries =
    portfolio?.performance?.series.map((point) => ({
      date: point.date,
      value: point.value,
    })) || [];

  const allocationBreakdown = portfolio?.allocation?.breakdown || [];
  const transactions = portfolio?.transactions || [];
  const recentNews = (news || []).slice(-6).reverse();

  return (
    <div className="space-y-4 p-4 lg:p-5">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label={t("dashboard.portfolioValue")}
          value={money(summary?.value)}
          sub={t("dashboard.invested", {
            value: summary?.invested !== undefined ? money(summary.invested) : "—",
          })}
          icon={<Wallet size={17} />}
        />
        <StatCard
          label={t("dashboard.cashBalance")}
          value={money(summary?.cash)}
          sub={t("dashboard.ofTotal", {
            pct: percent((summary?.cash / summary?.value) * 100, 1, false),
          })}
          icon={<Banknote size={17} />}
        />
        <StatCard
          label={t("dashboard.dailyPnl")}
          value={money(summary?.daily_pnl)}
          sub={<Change value={summary?.day_change_pct} />}
          tone={summary?.daily_pnl >= 0 ? "positive" : "negative"}
          icon={<TrendingUp size={17} />}
        />
        <StatCard
          label={t("dashboard.totalReturn")}
          value={percent(summary?.total_return_pct)}
          sub={t("dashboard.sinceStart", { value: money(summary?.profit) })}
          tone={summary?.total_return_pct >= 0 ? "positive" : "negative"}
          icon={<Briefcase size={17} />}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <section className="panel xl:col-span-2">
          <SectionTitle
            title={t("dashboard.performanceTitle")}
            detail={t("dashboard.performanceDetail")}
            right={<Badge className="border-ink-500/60 text-slate-400">{t("dashboard.vsStart")}</Badge>}
          />
          <div className="p-3">
            {performanceSeries.length > 1 ? (
              <LineChart data={performanceSeries} height={290} color="#22c55e" baseline={100000} />
            ) : (
              <EmptyState
                title={t("dashboard.performanceEmpty")}
                detail={t("dashboard.performanceEmptyDetail")}
              />
            )}
          </div>
        </section>

        <section className="panel">
          <SectionTitle title={t("dashboard.allocationTitle")} detail={t("dashboard.allocationDetail")} />
          <div className="flex flex-col items-center gap-4 p-4">
            {allocationBreakdown.length > 0 ? (
              <>
                <DonutChart
                  data={allocationBreakdown}
                  centerTitle={t("dashboard.investedLabel")}
                  centerValue={money(portfolio?.allocation?.total_invested, 0)}
                />
                <ul className="w-full space-y-1.5">
                  {allocationBreakdown.map((item) => (
                    <li key={item.industry} className="flex items-center gap-2 text-xs">
                      <span
                        className="h-2 w-2 shrink-0 rounded-full"
                        style={{ backgroundColor: industryColor(item.industry) }}
                      />
                      <span className="flex-1 text-slate-300">{t(`industry.${item.industry}`)}</span>
                      <span className="tabular text-slate-400">{money(item.value, 0)}</span>
                      <span className="w-10 text-right font-semibold tabular text-slate-200">
                        {item.weight.toFixed(1)}%
                      </span>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <EmptyState
                title={t("dashboard.allocationEmpty")}
                detail={t("dashboard.allocationEmptyDetail")}
              />
            )}
          </div>
        </section>
      </div>

      <section className="panel">
        <SectionTitle
          title={t("dashboard.indexTitle")}
          detail={t("dashboard.indexDetail")}
          right={
            <Badge className="border-gold/40 bg-gold/10 text-gold">
              {market?.shanghai_index?.toFixed(2)}
            </Badge>
          }
        />
        <div className="p-3">
          {indexHistory.length > 1 ? (
            <LineChart
              data={indexHistory.map((point) => ({ date: point.date, value: point.close }))}
              height={210}
              color="#f59e0b"
            />
          ) : (
            <EmptyState
              title={t("dashboard.performanceEmpty")}
              detail={t("dashboard.performanceEmptyDetail")}
            />
          )}
        </div>
      </section>

      <section className="panel">
        <SectionTitle
          title={t("dashboard.playerActivityTitle")}
          detail={t("dashboard.playerActivityDetail")}
        />
        {playerActivity.length > 0 ? (
          <ul className="grid grid-cols-1 gap-px bg-ink-600/60 sm:grid-cols-2 xl:grid-cols-3">
            {playerActivity.slice(0, 12).map((trade) => (
              <li key={trade.id} className="flex items-center justify-between gap-2 bg-ink-800 px-4 py-2.5">
                <div className="min-w-0">
                  <p className="flex items-center gap-2 text-xs font-semibold text-slate-200">
                    <span className="truncate">{trade.player}</span>
                    {trade.is_current ? (
                      <Badge className="border-sky/40 bg-sky/10 text-sky">
                        {t("achievements.you")}
                      </Badge>
                    ) : null}
                    <Badge
                      className={
                        trade.action === "buy"
                          ? "border-mint/40 bg-mint/10 text-mint"
                          : "border-risk/40 bg-risk/10 text-risk"
                      }
                    >
                      {t(trade.action === "buy" ? "order.buy" : "order.sell")}
                    </Badge>
                  </p>
                  <p className="mt-0.5 truncate text-[11px] text-slate-500">
                    {trade.name} {trade.shares.toFixed(4)} @ {money(trade.price)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-semibold tabular text-slate-200">{money(trade.gross)}</p>
                  <p className="text-[11px] text-slate-500">
                    {t("dashboard.day", { day: trade.day })}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="p-4">
            <EmptyState
              title={t("dashboard.playerActivityEmpty")}
              detail={t("dashboard.playerActivityEmptyDetail")}
            />
          </div>
        )}
      </section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <section className="panel">
          <SectionTitle title={t("dashboard.moversTitle")} detail={t("dashboard.moversDetail")} />
          <div className="grid grid-cols-2">
            <div>
              <p className="flex items-center gap-1 border-b border-ink-600/60 px-3 py-2 text-[11px] font-semibold uppercase text-mint">
                <ArrowUpRight size={13} /> {t("dashboard.gainers")}
              </p>
              <ul>
                {market?.gainers?.map((stock) => (
                  <li key={stock.ticker}>
                    <button
                      onClick={() => selectTicker(stock.ticker)}
                      className="row-hover flex w-full items-center justify-between gap-2 px-3 py-2 text-left"
                    >
                      <span className="min-w-0">
                        <span className="block truncate text-xs font-semibold text-slate-200">
                          {stock.name}
                        </span>
                        <span className="block text-[11px] text-slate-500">
                          {t(`industry.${stockMap[stock.ticker]?.industry}`)}
                        </span>
                      </span>
                      <span className="text-xs tabular text-slate-300">{money(stock.price)}</span>
                      <span className="w-14 text-right"><Change value={stock.change_pct} /></span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="flex items-center gap-1 border-b border-ink-600/60 px-3 py-2 text-[11px] font-semibold uppercase text-risk">
                <ArrowDownRight size={13} /> {t("dashboard.losers")}
              </p>
              <ul>
                {market?.losers?.map((stock) => (
                  <li key={stock.ticker}>
                    <button
                      onClick={() => selectTicker(stock.ticker)}
                      className="row-hover flex w-full items-center justify-between gap-2 px-3 py-2 text-left"
                    >
                      <span className="min-w-0">
                        <span className="block truncate text-xs font-semibold text-slate-200">
                          {stock.name}
                        </span>
                        <span className="block text-[11px] text-slate-500">
                          {t(`industry.${stockMap[stock.ticker]?.industry}`)}
                        </span>
                      </span>
                      <span className="text-xs tabular text-slate-300">{money(stock.price)}</span>
                      <span className="w-14 text-right"><Change value={stock.change_pct} /></span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section className="panel">
          <SectionTitle title={t("dashboard.recentTrades")} />
          {transactions.length > 0 ? (
            <ul className="max-h-64 divide-y divide-ink-600/50 overflow-y-auto">
              {transactions.slice(0, 8).map((trade) => (
                <li key={trade.id} className="flex items-center justify-between gap-2 px-4 py-2.5">
                  <div className="min-w-0">
                    <p className="flex items-center gap-2 text-xs font-semibold text-slate-200">
                      {trade.name || trade.ticker}
                      <Badge
                        className={
                          trade.action === "buy"
                            ? "border-mint/40 bg-mint/10 text-mint"
                            : "border-risk/40 bg-risk/10 text-risk"
                        }
                      >
                        {t(trade.action === "buy" ? "order.buy" : "order.sell")}
                      </Badge>
                    </p>
                    <p className="mt-0.5 truncate text-[11px] text-slate-500">
                      {trade.shares.toFixed(4)} @ {money(trade.price)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`text-xs font-semibold tabular ${toneClass(trade.realized_pnl)}`}>
                      {trade.realized_pnl !== 0 ? `${trade.realized_pnl > 0 ? "+" : ""}${money(trade.realized_pnl)}` : "—"}
                    </p>
                    <p className="text-[11px] text-slate-500">{t("dashboard.day", { day: trade.day })}</p>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState title={t("dashboard.noTrades")} detail={t("dashboard.noTradesDetail")} />
          )}
        </section>

        <section className="panel">
          <SectionTitle title={t("dashboard.newsTitle")} detail={t("dashboard.newsDetail")} right={<Newspaper size={15} className="text-slate-500" />} />
          {recentNews.length > 0 ? (
            <ul className="max-h-64 divide-y divide-ink-600/50 overflow-y-auto">
              {recentNews.map((event) => (
                <li key={event.id} className="px-4 py-2.5">
                  <div className="flex items-start gap-2">
                    <Badge
                      className={
                        event.category === "positive"
                          ? "border-mint/40 bg-mint/10 text-mint"
                          : event.category === "negative"
                            ? "border-risk/40 bg-risk/10 text-risk"
                            : "border-slate-500/40 bg-slate-500/10 text-slate-300"
                      }
                    >
                      {t(`news.${event.category}`)}
                    </Badge>
                    <p className="text-xs font-medium leading-4 text-slate-200">{event.headline}</p>
                  </div>
                  <p className="mt-1 text-[11px] leading-4 text-slate-500">{event.summary}</p>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              title={t("dashboard.quietTape")}
              detail={t("dashboard.newsEmptyDetail")}
            />
          )}
        </section>
      </div>
    </div>
  );
}
