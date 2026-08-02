import { ArrowDownCircle, ArrowUpCircle, Banknote, Briefcase, PieChart, ScrollText } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";
import { industryColor, money, percent, toneClass } from "../../utils/format.js";
import LineChart from "../charts/LineChart.jsx";
import DonutChart from "../charts/DonutChart.jsx";
import { MuseumHeader } from "../museum.jsx";
import { Badge, Change, EmptyState, SectionTitle, StatCard } from "../ui.jsx";

function lessonFor(trade, t) {
  if (trade.action === "buy") return t("journal.lessonBuy");
  if (trade.realized_pnl > 0) return t("journal.lessonProfit");
  if (trade.realized_pnl < 0) return t("journal.lessonLoss");
  return t("journal.lessonFlat");
}

export default function PortfolioView() {
  const { portfolio, selectTicker, t } = useApp();
  const summary = portfolio?.summary;
  const holdings = portfolio?.holdings || [];
  const allocation = portfolio?.allocation?.breakdown || [];
  const transactions = portfolio?.transactions || [];
  const performanceSeries =
    portfolio?.performance?.series.map((point) => ({
      date: point.date,
      value: point.value,
    })) || [];
  const journalEntries = [...transactions].reverse();
  const unrealizedTotal = holdings.reduce((sum, item) => sum + item.unrealized_pnl, 0);

  return (
    <div className="space-y-4 p-4 lg:p-5">
      <MuseumHeader
        kicker={t("journal.kicker")}
        title={t("journal.title")}
        detail={t("journal.detail")}
      />

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label={t("portfolio.statValue")} value={money(summary?.value)} icon={<Briefcase size={17} />} />
        <StatCard label={t("portfolio.statCash")} value={money(summary?.cash)} icon={<Banknote size={17} />} />
        <StatCard
          label={t("portfolio.statInvested")}
          value={money(summary?.invested)}
          sub={t("portfolio.positions", { count: holdings.length })}
          icon={<PieChart size={17} />}
        />
        <StatCard
          label={t("portfolio.statUnrealized")}
          value={money(unrealizedTotal)}
          sub={t("dashboard.totalReturn")}
          tone={unrealizedTotal >= 0 ? "positive" : "negative"}
          icon={<ArrowUpCircle size={17} />}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <section className="panel xl:col-span-2">
          <SectionTitle title={t("portfolio.equityTitle")} detail={t("portfolio.equityDetail")} />
          <div className="p-3">
            {performanceSeries.length > 1 ? (
              <LineChart data={performanceSeries} height={280} color="#b08d57" baseline={100000} />
            ) : (
              <EmptyState
                title={t("portfolio.equityEmpty")}
                detail={t("portfolio.equityEmptyDetail")}
              />
            )}
          </div>
        </section>

        <section className="panel">
          <SectionTitle title={t("portfolio.mixTitle")} detail={t("portfolio.mixDetail")} />
          <div className="flex flex-col items-center gap-4 p-4">
            {allocation.length > 0 ? (
              <>
                <DonutChart
                  data={allocation}
                  centerTitle={t("dashboard.investedLabel")}
                  centerValue={money(portfolio?.allocation?.total_invested, 0)}
                />
                <ul className="w-full space-y-1.5">
                  {allocation.map((item) => (
                    <li key={item.industry} className="flex items-center gap-2 text-xs">
                      <span
                        className="h-2 w-2 shrink-0 rounded-full"
                        style={{ backgroundColor: industryColor(item.industry) }}
                      />
                      <span className="flex-1 text-parch-300">{t(`industry.${item.industry}`)}</span>
                      <span className="w-12 text-right font-semibold tabular text-parch-200">
                        {item.weight.toFixed(1)}%
                      </span>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <EmptyState title={t("portfolio.mixEmpty")} detail={t("portfolio.mixEmptyDetail")} />
            )}
          </div>
        </section>
      </div>

      <section className="panel overflow-hidden">
        <SectionTitle title={t("portfolio.holdingsTitle")} detail={t("portfolio.holdingsDetail")} />
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse">
            <thead>
              <tr>
                <th className="th">{t("portfolio.colSymbol")}</th>
                <th className="th">{t("portfolio.colIndustry")}</th>
                <th className="th">{t("portfolio.colShares")}</th>
                <th className="th">{t("portfolio.colAvgCost")}</th>
                <th className="th">{t("portfolio.colPrice")}</th>
                <th className="th">{t("portfolio.colValue")}</th>
                <th className="th">{t("portfolio.colUnrealized")}</th>
                <th className="th">{t("portfolio.colDay")}</th>
                <th className="th">{t("portfolio.colWeight")}</th>
                <th className="th">{t("portfolio.colAction")}</th>
              </tr>
            </thead>
            <tbody>
              {holdings.map((holding) => (
                <tr key={holding.ticker} className="row-hover" onClick={() => selectTicker(holding.ticker)}>
                  <td className="td">
                    <span className="font-semibold text-parch-100">{holding.name}</span>
                  </td>
                  <td className="td text-parch-500">{t(`industry.${holding.industry}`)}</td>
                  <td className="td text-parch-300">{holding.shares.toFixed(4)}</td>
                  <td className="td text-parch-300">{money(holding.avg_cost)}</td>
                  <td className="td font-semibold text-parch-100">{money(holding.price)}</td>
                  <td className="td font-semibold text-parch-100">{money(holding.market_value)}</td>
                  <td className="td">
                    <span className={`${toneClass(holding.unrealized_pnl)}`}>
                      {money(holding.unrealized_pnl)}
                      <span className="ml-1 text-[11px]">({percent(holding.unrealized_pct)})</span>
                    </span>
                  </td>
                  <td className="td">
                    <Change value={holding.day_change_pct} />
                  </td>
                  <td className="td text-parch-300">{holding.weight.toFixed(1)}%</td>
                  <td className="td">
                    <div className="flex gap-1" onClick={(event) => event.stopPropagation()}>
                      <button
                        onClick={() => selectTicker(holding.ticker)}
                        className="btn btn-ghost px-2 py-1 text-xs"
                        title={t("portfolio.openTrade")}
                      >
                        <ArrowUpCircle size={13} /> {t("portfolio.trade")}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {holdings.length === 0 ? (
            <EmptyState
              title={t("portfolio.holdingsEmpty")}
              detail={t("portfolio.holdingsEmptyDetail")}
            />
          ) : null}
        </div>
      </section>

      <section>
        <div className="mb-3 flex items-center gap-2">
          <ScrollText size={16} className="text-brass" />
          <h2 className="font-display text-lg font-bold text-parch-100">{t("journal.entries")}</h2>
        </div>
        {journalEntries.length > 0 ? (
          <div className="space-y-3">
            {journalEntries.map((trade) => (
              <article key={trade.id} className="paper-panel px-4 py-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Badge
                      className={
                        trade.action === "buy"
                          ? "border-ink-900/30 bg-ink-900/10 text-ink-900"
                          : "border-risk/40 bg-risk/10 text-risk"
                      }
                    >
                      {t(trade.action === "buy" ? "order.buy" : "order.sell")}
                    </Badge>
                    <h3 className="font-display text-sm font-bold text-ink-950">
                      {trade.name || trade.ticker}
                    </h3>
                  </div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.1em] text-ink-900/60">
                    {t("journal.tradingDay", { day: trade.day })}
                  </p>
                </div>
                <p className="mt-1.5 text-xs leading-5 text-ink-900/75">
                  {trade.shares.toFixed(4)} @ {money(trade.price)} · {t("portfolio.colTxGross")}{" "}
                  {money(trade.gross)}
                  {trade.realized_pnl ? (
                    <>
                      {" "}· {t("portfolio.colTxRealized")}{" "}
                      <span className={trade.realized_pnl >= 0 ? "font-semibold text-ink-900" : "font-semibold text-risk"}>
                        {trade.realized_pnl > 0 ? "+" : ""}
                        {money(trade.realized_pnl)}
                      </span>
                    </>
                  ) : null}
                </p>
                <p className="mt-2 border-t border-ink-900/15 pt-2 text-xs italic leading-5 text-ink-900/80">
                  {lessonFor(trade, t)}
                </p>
              </article>
            ))}
          </div>
        ) : (
          <section className="panel">
            <EmptyState title={t("journal.empty")} detail={t("journal.emptyDetail")} />
          </section>
        )}
      </section>
    </div>
  );
}
