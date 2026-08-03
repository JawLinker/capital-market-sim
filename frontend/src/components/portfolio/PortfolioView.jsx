import {
  ArrowDownCircle,
  ArrowUpCircle,
  Banknote,
  Briefcase,
  PieChart,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { useState } from "react";

import { api } from "../../api/client.js";
import { useApp } from "../../store/AppContext.jsx";
import { industryColor, money, percent, toneClass } from "../../utils/format.js";
import LineChart from "../charts/LineChart.jsx";
import DonutChart from "../charts/DonutChart.jsx";
import { MuseumHeader } from "../museum.jsx";
import { Badge, Change, EmptyState, SectionTitle, StatCard } from "../ui.jsx";

export default function PortfolioView() {
  const { portfolio, selectTicker, t } = useApp();
  const [guardNotice, setGuardNotice] = useState("");
  const summary = portfolio?.summary;
  const holdings = portfolio?.holdings || [];
  const allocation = portfolio?.allocation?.breakdown || [];
  const performanceSeries =
    portfolio?.performance?.series.map((point) => ({
      date: point.date,
      value: point.value,
    })) || [];
  const unrealizedTotal = holdings.reduce((sum, item) => sum + item.unrealized_pnl, 0);

  const placeGuard = (kind, holding) => {
    const multiplier = kind === "stop_loss" ? 0.95 : 1.1;
    api
      .createOrder(
        holding.ticker,
        kind,
        Math.round(holding.price * multiplier * 100) / 100,
        holding.shares
      )
      .then(() => setGuardNotice(t("portfolio.guardPlaced")))
      .catch((error) => setGuardNotice(error.message));
  };

  return (
    <div className="space-y-4 p-4 lg:p-5">
      <MuseumHeader
        kicker={t("portfolio.kicker")}
        title={t("portfolio.pageTitle")}
        detail={t("portfolio.pageDetail")}
      />

      {summary?.margin_debt > 0 ? (
        <div className="flex flex-wrap items-center gap-3 rounded-[3px] border border-risk/40 bg-risk/10 px-4 py-2.5 text-xs">
          <span className="font-semibold text-risk">{t("portfolio.marginDebt")}</span>
          <span className="tabular text-risk">{money(summary.margin_debt)}</span>
          <span className="text-parch-600">·</span>
          <span className="font-semibold text-parch-300">{t("portfolio.marginRatio")}</span>
          <span className="tabular text-parch-300">
            {summary.margin_ratio != null ? summary.margin_ratio.toFixed(2) : "…"}
          </span>
          {summary.margin_ratio != null && summary.margin_ratio < 1.5 ? (
            <span className="font-semibold text-risk">{t("portfolio.marginDanger")}</span>
          ) : null}
        </div>
      ) : null}

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
        {guardNotice ? (
          <p className="border-b border-ink-600/60 bg-brass/10 px-4 py-2 text-xs text-brass">
            {guardNotice}
          </p>
        ) : null}
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
                        onClick={() => placeGuard("stop_loss", holding)}
                        className="btn btn-ghost px-2 py-1 text-xs"
                        title={t("portfolio.stopLoss")}
                      >
                        <ShieldAlert size={12} />
                        {t("portfolio.stopLossShort")}
                      </button>
                      <button
                        onClick={() => placeGuard("take_profit", holding)}
                        className="btn btn-ghost px-2 py-1 text-xs"
                        title={t("portfolio.takeProfit")}
                      >
                        <ShieldCheck size={12} />
                        {t("portfolio.takeProfitShort")}
                      </button>
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
    </div>
  );
}
