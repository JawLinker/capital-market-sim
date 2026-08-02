import { ArrowDownCircle, ArrowUpCircle, Banknote, Briefcase, PieChart } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";
import { industryColor, money, percent, toneClass } from "../../utils/format.js";
import LineChart from "../charts/LineChart.jsx";
import DonutChart from "../charts/DonutChart.jsx";
import { Badge, Change, EmptyState, SectionTitle, StatCard } from "../ui.jsx";

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

  const unrealizedTotal = holdings.reduce((sum, item) => sum + item.unrealized_pnl, 0);

  return (
    <div className="space-y-4 p-4 lg:p-5">
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
              <LineChart data={performanceSeries} height={280} color="#38bdf8" baseline={100000} />
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
                      <span className="flex-1 text-slate-300">{t(`industry.${item.industry}`)}</span>
                      <span className="w-12 text-right font-semibold tabular text-slate-200">
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
        <SectionTitle
          title={t("portfolio.holdingsTitle")}
          detail={t("portfolio.holdingsDetail")}
        />
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
                    <span className="font-semibold text-slate-100">{holding.name}</span>
                  </td>
                  <td className="td text-slate-400">{t(`industry.${holding.industry}`)}</td>
                  <td className="td text-slate-300">{holding.shares.toFixed(4)}</td>
                  <td className="td text-slate-300">{money(holding.avg_cost)}</td>
                  <td className="td font-semibold text-slate-100">{money(holding.price)}</td>
                  <td className="td font-semibold text-slate-100">{money(holding.market_value)}</td>
                  <td className="td">
                    <span className={`${toneClass(holding.unrealized_pnl)}`}>
                      {money(holding.unrealized_pnl)}
                      <span className="ml-1 text-[11px]">({percent(holding.unrealized_pct)})</span>
                    </span>
                  </td>
                  <td className="td"><Change value={holding.day_change_pct} /></td>
                  <td className="td text-slate-300">{holding.weight.toFixed(1)}%</td>
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

      <section className="panel overflow-hidden">
        <SectionTitle title={t("portfolio.txTitle")} detail={t("portfolio.txDetail")} />
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] border-collapse">
            <thead>
              <tr>
                <th className="th">{t("portfolio.colTxDay")}</th>
                <th className="th">{t("portfolio.colTxSymbol")}</th>
                <th className="th">{t("portfolio.colTxAction")}</th>
                <th className="th">{t("portfolio.colTxShares")}</th>
                <th className="th">{t("portfolio.colTxPrice")}</th>
                <th className="th">{t("portfolio.colTxGross")}</th>
                <th className="th">{t("portfolio.colTxFee")}</th>
                <th className="th">{t("portfolio.colTxTax")}</th>
                <th className="th">{t("portfolio.colTxRealized")}</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((trade) => (
                <tr key={trade.id} className="hover:bg-ink-700/40">
                  <td className="td text-slate-500">{trade.day}</td>
                  <td className="td font-semibold text-slate-200">{trade.name || trade.ticker}</td>
                  <td className="td">
                    <Badge
                      className={
                        trade.action === "buy"
                          ? "border-mint/40 bg-mint/10 text-mint"
                          : "border-risk/40 bg-risk/10 text-risk"
                      }
                    >
                      {t(trade.action === "buy" ? "order.buy" : "order.sell")}
                    </Badge>
                  </td>
                  <td className="td text-slate-300">{trade.shares.toFixed(4)}</td>
                  <td className="td text-slate-300">{money(trade.price)}</td>
                  <td className="td text-slate-300">{money(trade.gross)}</td>
                  <td className="td text-slate-400">{money(trade.fee)}</td>
                  <td className="td text-slate-400">{money(trade.stamp_tax)}</td>
                  <td className={`td ${toneClass(trade.realized_pnl)}`}>
                    {trade.realized_pnl ? `${trade.realized_pnl > 0 ? "+" : ""}${money(trade.realized_pnl)}` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {transactions.length === 0 ? (
            <EmptyState title={t("portfolio.txEmpty")} detail={t("portfolio.txEmptyDetail")} />
          ) : null}
        </div>
      </section>
    </div>
  );
}
