import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  Banknote,
  Briefcase,
  FileText,
  Newspaper,
  ScrollText,
  TrendingUp,
  Wallet,
} from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";
import { eraForDate, playableEras } from "../../utils/era.js";
import { money, percent } from "../../utils/format.js";
import LineChart from "../charts/LineChart.jsx";
import Avatar from "../Avatar.jsx";
import { ArchiveCard, EraBadge, MuseumHeader, TimelineNavigator } from "../museum.jsx";
import { Badge, Change, EmptyState, SectionTitle, StatCard } from "../ui.jsx";

const CYCLE_ACTION = {
  recovery: "home.actionRecovery",
  bull: "home.actionBull",
  bear: "home.actionBear",
  recession: "home.actionRecession",
};

const BARRAGE_ZH = [
  "敢死队今天又上榜了",
  "下一棒是谁？",
  "算力订单还能再涨吗",
  "我已经全仓梭哈了",
  "关灯吃面的位置越来越多了",
  "别追高，会挨打的",
];

const BARRAGE_EN = [
  "The commandos are on the leaderboard again",
  "Who takes the baton next?",
  "Can compute orders keep rising?",
  "I am all in already",
  "More noodles eaten in the dark",
  "Chasing highs ends in pain",
];

export default function DashboardView() {
  const {
    gameState,
    portfolio,
    news,
    stocks,
    indexHistory,
    selectTicker,
    playerActivity,
    chronicle,
    t,
    lang,
  } = useApp();
  const summary = portfolio?.summary;
  const market = gameState?.market;
  const stockMap = useMemo(
    () => Object.fromEntries(stocks.map((stock) => [stock.ticker, stock])),
    [stocks]
  );
  const era = eraForDate(market?.date, lang);
  const eras = playableEras(lang);
  const cycleLabel = t(`cycle.${market?.market_cycle}`);
  const recentNews = (news || []).slice(-8).reverse();
  const [barrageIndex, setBarrageIndex] = useState(0);
  const barrage = lang === "zh" ? BARRAGE_ZH : BARRAGE_EN;
  useEffect(() => {
    if (chronicle?.arc_key !== "2026") return undefined;
    const timer = window.setInterval(() => setBarrageIndex((index) => index + 1), 2600);
    return () => window.clearInterval(timer);
  }, [chronicle?.arc_key]);
  const allocationBreakdown = portfolio?.allocation?.breakdown || [];
  const performanceSeries =
    portfolio?.performance?.series.map((point) => ({
      date: point.date,
      value: point.value,
    })) || [];

  return (
    <div className="space-y-4 p-4 lg:p-5">
      <MuseumHeader
        kicker={t("home.kicker")}
        title={`${era.label} · ${cycleLabel}`}
        detail={t("home.detail", { date: market?.date || "…", day: market?.day || 0 })}
        right={<EraBadge>{era.label}</EraBadge>}
      />

      <TimelineNavigator eras={eras} current={era.key} />

      <ArchiveCard
        stamp={chronicle?.stamp}
        header={
          <div className="flex w-full flex-wrap items-center justify-between gap-2">
            <div>
              <h2 className="flex items-center gap-2 font-display text-[15px] font-semibold text-parch-100">
                <ScrollText size={15} className="text-brass" />
                {t("chronicle.title")}
              </h2>
              <p className="mt-0.5 text-xs text-parch-500">{chronicle?.summary || ""}</p>
            </div>
            <Badge className="border-brass/40 bg-brass/10 text-brass">
              {chronicle?.title?.label}
            </Badge>
          </div>
        }
      >
        <ol className="flex flex-wrap items-center gap-1.5">
          {(chronicle?.beats || []).map((beat) => (
            <li
              key={beat.id}
              className={`rounded-[3px] border px-2 py-1 text-[11px] font-semibold ${
                beat.status === "current"
                  ? "border-risk/50 bg-risk/10 text-risk"
                  : beat.status === "passed"
                    ? "border-brass/35 bg-brass/5 text-brass"
                    : "border-ink-600/80 text-parch-600"
              }`}
              title={beat.title}
            >
              {beat.index}. {beat.title}
            </li>
          ))}
        </ol>
        {chronicle?.arc_key === "2026" ? (
          <div className="mt-3 overflow-hidden rounded-[3px] border border-brass/35 bg-ink-900/70 px-3 py-2">
            <p className="flex items-center gap-2 text-[11px] text-brass">
              <ScrollText size={12} className="shrink-0" />
              <span className="truncate">{barrage[barrageIndex % barrage.length]}</span>
            </p>
          </div>
        ) : null}
        {(() => {
          const current = (chronicle?.beats || []).find((beat) => beat.status === "current");
          const objective = current?.objective;
          if (!objective) return null;
          return (
            <div className="mt-3 rounded-[3px] border border-ink-600/70 bg-ink-900/60 p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-parch-600">
                  {t("chronicle.objective")}
                </p>
                <span
                  className={`rounded-[3px] border px-2 py-0.5 text-[10px] font-bold ${
                    objective.met
                      ? "border-mint/40 bg-mint/10 text-mint"
                      : "border-brass/40 bg-brass/10 text-brass"
                  }`}
                >
                  {objective.met ? t("chronicle.met") : t("chronicle.notMet")}
                </span>
              </div>
              <p className="mt-2 text-xs text-parch-300">{objective.label}</p>
              <p className="mt-1 text-xs tabular text-parch-500">
                {objective.current.toLocaleString()} / {objective.target.toLocaleString()}
              </p>
              {objective.target > 0 ? (
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-ink-600">
                  <div
                    className="h-full rounded-full bg-brass"
                    style={{ width: `${Math.min(100, (objective.current / objective.target) * 100)}%` }}
                  />
                </div>
              ) : null}
            </div>
          );
        })()}
      </ArchiveCard>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <ArchiveCard
          className="xl:col-span-2"
          stamp={t("home.stamp")}
          header={
            <div>
              <h2 className="flex items-center gap-2 font-display text-[15px] font-semibold text-parch-100">
                <Newspaper size={15} className="text-brass" />
                {t("home.events")}
              </h2>
              <p className="mt-0.5 text-xs text-parch-500">{t("home.eventsDetail")}</p>
            </div>
          }
        >
          {recentNews.length > 0 ? (
            <ul className="space-y-2">
              {recentNews.map((event) => (
                <li
                  key={event.id}
                  className="flex gap-3 rounded-[3px] border border-ink-600/60 bg-ink-900/50 px-3 py-2.5"
                >
                  <span
                    className={`mt-1 h-2 w-2 shrink-0 rounded-full ${
                      event.category === "positive"
                        ? "bg-mint"
                        : event.category === "negative"
                          ? "bg-risk"
                          : "bg-brass"
                    }`}
                  />
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="text-xs font-semibold text-parch-100">{event.headline}</p>
                      {event.company ? (
                        <Badge className="border-brass/40 bg-brass/10 text-brass">
                          {event.company}
                        </Badge>
                      ) : null}
                    </div>
                    {event.summary ? (
                      <p className="mt-1 text-[11px] leading-5 text-parch-500">{event.summary}</p>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              title={t("home.eventsEmpty")}
              detail={t("home.eventsEmptyDetail")}
            />
          )}
        </ArchiveCard>

        <div className="space-y-4">
          <ArchiveCard
            stamp={t("home.indicatorsStamp")}
            header={
              <h2 className="font-display text-[15px] font-semibold text-parch-100">
                {t("home.indicators")}
              </h2>
            }
          >
            <div className="grid grid-cols-2 gap-2">
              {[
                [t("topbar.rate"), `${market?.policy_rate?.toFixed(2) ?? "…"}%`],
                [t("topbar.sentiment"), market?.sentiment?.toFixed(2) ?? "…"],
                [t("home.inflation"), `${market?.inflation?.toFixed(2) ?? "…"}%`],
                [t("topbar.benchmark"), market ? money(market.benchmark_value, 0) : "…"],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-[3px] border border-ink-600/60 bg-ink-900/50 px-3 py-2.5"
                >
                  <p className="text-[10px] uppercase tracking-[0.12em] text-parch-500">{label}</p>
                  <p className="mt-1 font-display text-sm font-bold tabular text-parch-100">{value}</p>
                </div>
              ))}
            </div>
            <div className="mt-3">
              <div className="mb-1 flex justify-between text-[10px] text-parch-500">
                <span>{t("home.sentimentScale")}</span>
                <span className="tabular text-parch-300">
                  {market ? Math.round(((market.sentiment - 0.55) / 0.95) * 100) : 0}%
                </span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-ink-600">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-risk via-gold to-mint"
                  style={{
                    width: `${market ? Math.round(((market.sentiment - 0.55) / 0.95) * 100) : 0}%`,
                  }}
                />
              </div>
            </div>
          </ArchiveCard>

          <ArchiveCard
            header={
              <h2 className="flex items-center gap-2 font-display text-[15px] font-semibold text-parch-100">
                <FileText size={15} className="text-brass" />
                {t("home.actions")}
              </h2>
            }
          >
            <p className="text-sm leading-6 text-parch-400">{t(CYCLE_ACTION[market?.market_cycle] || CYCLE_ACTION.recovery)}</p>
            <div className="museum-rule my-3" />
            <p className="text-[11px] leading-5 text-parch-600">{t("home.actionsDetail")}</p>
          </ArchiveCard>
        </div>
      </div>

      <section className="panel overflow-hidden">
        <SectionTitle
          title={t("home.journey")}
          detail={t("home.journeyDetail")}
          right={
            <Badge className="border-brass/40 bg-brass/10 text-brass">
              {t("dashboard.vsStart")}
            </Badge>
          }
        />
        <div className="space-y-4 p-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label={t("dashboard.portfolioValue")}
              value={money(summary?.value)}
              sub={t("dashboard.invested", {
                value: summary?.invested !== undefined ? money(summary.invested) : "…",
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
              />
              <div className="p-3">
                {performanceSeries.length > 1 ? (
                  <LineChart
                    data={performanceSeries}
                    height={280}
                    color="#b08d57"
                    baseline={100000}
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
                title={t("dashboard.indexTitle")}
                detail={t("dashboard.indexDetail")}
                right={
                  <Badge className="border-brass/40 bg-brass/10 text-brass">
                    {market?.shanghai_index?.toFixed(2)}
                  </Badge>
                }
              />
              <div className="p-3">
                {indexHistory.length > 1 ? (
                  <LineChart
                    data={indexHistory.map((point) => ({ date: point.date, value: point.close }))}
                    height={240}
                    color="#c9a24b"
                  />
                ) : (
                  <EmptyState
                    title={t("dashboard.performanceEmpty")}
                    detail={t("dashboard.performanceEmptyDetail")}
                  />
                )}
              </div>
            </section>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <section className="panel lg:col-span-2">
          <SectionTitle title={t("dashboard.moversTitle")} detail={t("dashboard.moversDetail")} />
          <div className="grid grid-cols-1 sm:grid-cols-2">
            <div>
              <p className="flex items-center gap-1 border-b border-ink-600/60 px-3 py-2 text-[11px] font-semibold uppercase tracking-wide text-mint">
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
                        <span className="block truncate text-xs font-semibold text-parch-200">
                          {stock.name}
                        </span>
                        <span className="block text-[11px] text-parch-500">
                          {t(`industry.${stockMap[stock.ticker]?.industry}`)}
                        </span>
                      </span>
                      <span className="text-xs tabular text-parch-300">{money(stock.price)}</span>
                      <span className="w-14 text-right">
                        <Change value={stock.change_pct} />
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="flex items-center gap-1 border-b border-ink-600/60 px-3 py-2 text-[11px] font-semibold uppercase tracking-wide text-risk">
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
                        <span className="block truncate text-xs font-semibold text-parch-200">
                          {stock.name}
                        </span>
                        <span className="block text-[11px] text-parch-500">
                          {t(`industry.${stockMap[stock.ticker]?.industry}`)}
                        </span>
                      </span>
                      <span className="text-xs tabular text-parch-300">{money(stock.price)}</span>
                      <span className="w-14 text-right">
                        <Change value={stock.change_pct} />
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section className="panel">
          <SectionTitle
            title={t("dashboard.playerActivityTitle")}
            detail={t("dashboard.playerActivityDetail")}
          />
          {playerActivity.length > 0 ? (
            <ul className="grid grid-cols-1 gap-px bg-ink-600/60">
              {playerActivity.slice(0, 12).map((trade) => (
                <li key={trade.id} className="flex items-center justify-between gap-2 bg-ink-800 px-4 py-2.5">
                  <div className="min-w-0">
                    <p className="flex items-center gap-2 text-xs font-semibold text-parch-200">
                      <Avatar seed={trade.player} size={18} />
                      <span className="truncate">{trade.player}</span>
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
                    <p className="mt-0.5 truncate text-[11px] text-parch-500">
                      {trade.name} {trade.shares.toFixed(4)} @ {money(trade.price)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-semibold tabular text-parch-200">{money(trade.gross)}</p>
                    <p className="text-[11px] text-parch-500">
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
      </div>
    </div>
  );
}
