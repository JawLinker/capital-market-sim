import { useState } from "react";
import { Award, Soup, Target, Trophy, X } from "lucide-react";

import { api } from "../../api/client.js";
import { useApp } from "../../store/AppContext.jsx";
import { money, percent, toneClass } from "../../utils/format.js";
import Avatar from "../Avatar.jsx";
import LineChart from "../charts/LineChart.jsx";
import { Badge, ProgressBar, SectionTitle } from "../ui.jsx";

const CATEGORY_COLORS = {
  trading: "border-sky/40 bg-sky/10 text-sky",
  strategy: "border-mint/40 bg-mint/10 text-mint",
  risk: "border-gold/40 bg-gold/10 text-gold",
  milestone: "border-violet-400/40 bg-violet-400/10 text-violet-300",
};

export default function AchievementsView() {
  const { achievements, leaderboard, t } = useApp();
  const [botData, setBotData] = useState(null);
  const [loadingBot, setLoadingBot] = useState(false);
  const items = achievements?.achievements || [];
  const milestones = achievements?.milestones || [];
  const entries = leaderboard?.entries || [];

  const unlocked = items.filter((item) => item.unlocked);
  const locked = items.filter((item) => !item.unlocked);

  const openBot = async (entry) => {
    if (entry.kind !== "rival") return;
    setLoadingBot(true);
    try {
      const data = await api.getBot(entry.id);
      setBotData(data);
    } finally {
      setLoadingBot(false);
    }
  };

  const closeBot = () => setBotData(null);

  const equityData =
    botData?.equity?.map((point) => ({
      date: new Date(
        Date.UTC(2019, 0, 2) + point.day * 86400 * 1000
      )
        .toISOString()
        .slice(0, 10),
      value: point.value,
    })) || [];

  return (
    <div className="space-y-4 p-4 lg:p-5">
      <section className="panel p-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-center">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg border border-violet-400/30 bg-violet-400/10 text-violet-300">
              <Trophy size={22} />
            </div>
            <div>
              <p className="text-sm font-semibold text-parch-100">{t("achievements.title")}</p>
              <p className="mt-0.5 text-xs text-parch-600">
                {t("achievements.subtitle", {
                  unlocked: achievements?.unlocked_count,
                  total: achievements?.total_count,
                  value: money(achievements?.portfolio_value),
                })}
              </p>
            </div>
          </div>
          <div className="grid flex-1 grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
            {milestones.map((milestone, index) => {
              const next = milestones[index + 1];
              const span = next ? next.threshold - milestone.threshold : 50_000;
              const progress = next
                ? Math.max(
                    0,
                    Math.min(1, (achievements?.portfolio_value - milestone.threshold) / span)
                  )
                : milestone.reached
                  ? 1
                  : Math.max(0, Math.min(1, (achievements?.portfolio_value - milestone.threshold) / span));
              return (
                <div
                  key={milestone.label}
                  className={`rounded-md border px-3 py-2.5 ${
                    milestone.reached
                      ? "border-mint/40 bg-mint/10"
                      : "border-ink-600/70 bg-ink-750/60"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <Target size={14} className={milestone.reached ? "text-mint" : "text-parch-600"} />
                    <span className={`text-[11px] font-semibold tabular ${milestone.reached ? "text-mint" : "text-parch-500"}`}>
                      {milestone.label}
                    </span>
                  </div>
                  <ProgressBar
                    value={progress}
                    className="mt-2"
                    color={milestone.reached ? "#22c55e" : "#38bdf8"}
                  />
                  <p className="mt-1.5 text-[10px] text-parch-600">
                    {milestone.reached
                      ? t("achievements.reached")
                      : t("achievements.nextGoal", { pct: Math.round(progress * 100) })}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="panel overflow-hidden">
        <SectionTitle title={t("achievements.gridTitle")} detail={t("achievements.gridDetail")} />
        <div className="grid grid-cols-1 gap-3 p-4 sm:grid-cols-2 xl:grid-cols-3">
          {[...unlocked, ...locked].map((item) => (
            <div
              key={item.code}
              className={`rounded-md border p-3.5 ${
                item.unlocked
                  ? "border-mint/25 bg-mint/[0.04]"
                  : "border-ink-600/60 bg-ink-750/50 opacity-80"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className={`flex h-9 w-9 items-center justify-center rounded-md border ${CATEGORY_COLORS[item.category] || CATEGORY_COLORS.trading}`}>
                  <Award size={17} />
                </div>
                <Badge
                  className={
                    item.unlocked
                      ? "border-mint/40 bg-mint/10 text-mint"
                      : "border-ink-500/50 text-parch-600"
                  }
                >
                  {item.unlocked ? t("achievements.unlocked") : t("achievements.locked")}
                </Badge>
              </div>
              <p className="mt-2.5 text-sm font-semibold text-parch-100">{item.title}</p>
              <p className="mt-1 text-xs leading-5 text-parch-600">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="panel overflow-hidden">
        <SectionTitle
          title={t("achievements.leaderboard")}
          detail={t("achievements.leaderboardDetail")}
          right={
            <div className="flex items-center gap-2">
              <Badge className="border-gold/40 bg-gold/10 text-gold">
                {leaderboard?.season?.label}
              </Badge>
              <Badge className="border-ink-500/50 text-parch-300">
                {t("achievements.winRate", {
                  losses: leaderboard?.losses,
                  flat: leaderboard?.flat,
                  wins: leaderboard?.wins,
                })}
              </Badge>
              <Badge className="border-gold/40 bg-gold/10 text-gold">
                {t("achievements.bestStreak", { days: achievements?.best_streak || 0 })}
              </Badge>
              <Badge className="border-gold/40 bg-gold/10 text-gold">
                {t("achievements.seerStreak", {
                  days: achievements?.best_prediction_streak || 0,
                })}
              </Badge>
            </div>
          }
        />
        <div className="overflow-x-auto">
          <table className="w-full min-w-[680px] border-collapse">
            <thead>
              <tr>
                <th className="th">{t("achievements.colRank")}</th>
                <th className="th">{t("achievements.colManager")}</th>
                <th className="th">{t("achievements.colStyle")}</th>
                <th className="th">{t("achievements.colValue")}</th>
                <th className="th">{t("achievements.colReturn")}</th>
                <th className="th">{t("portfolio.colAction")}</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr
                  key={entry.name}
                  className={`hover:bg-ink-700/40 ${
                    entry.kind === "player" && entry.is_current ? "bg-sky/[0.05]" : ""
                  }`}
                >
                  <td className="td">
                    <span
                      className={`inline-flex h-6 w-6 items-center justify-center rounded font-semibold tabular ${
                        entry.rank === 1
                          ? "bg-gold/20 text-gold"
                          : entry.rank === 2
                            ? "bg-slate-400/20 text-parch-200"
                            : entry.rank === 3
                              ? "bg-amber-700/25 text-amber-400"
                              : "text-parch-600"
                      }`}
                    >
                      {entry.rank}
                    </span>
                  </td>
                  <td className="td">
                    <span className="flex items-center gap-2 font-semibold text-parch-100">
                      <Avatar seed={entry.name} size={22} />
                      {entry.name}
                      {entry.kind === "player" && entry.is_current ? (
                        <Badge className="border-sky/40 bg-sky/10 text-sky">{t("achievements.you")}</Badge>
                      ) : null}
                      {entry.kind === "player" && entry.is_current && entry.medal ? (
                        <Badge
                          className={
                            entry.medal === "gold"
                              ? "border-gold/40 bg-gold/10 text-gold"
                              : entry.medal === "silver"
                                ? "border-parch-400/40 bg-parch-400/10 text-parch-200"
                                : "border-brass/40 bg-brass/10 text-brass"
                          }
                        >
                          {t(
                            `season.medal${entry.medal.charAt(0).toUpperCase()}${entry.medal.slice(1)}`
                          )}
                        </Badge>
                      ) : null}
                      {entry.noodle ? (
                        <Badge
                          className="border-gold/40 bg-gold/10 text-gold"
                          title={t("season.noodle")}
                        >
                          <Soup size={11} />
                          {t("season.noodle")}
                        </Badge>
                      ) : entry.kind === "benchmark" ? (
                        <Badge className="border-ink-500/50 text-parch-500">{t("achievements.index")}</Badge>
                      ) : null}
                    </span>
                  </td>
                  <td className="td text-parch-500">{t(`strategy.${entry.strategy}`)}</td>
                  <td className="td font-semibold tabular text-parch-100">{money(entry.value)}</td>
                  <td className={`td font-semibold tabular ${toneClass(entry.return_pct)}`}>
                    {percent(entry.return_pct)}
                  </td>
                  <td className="td">
                    {entry.kind === "rival" ? (
                      <button
                        onClick={() => openBot(entry)}
                        className="btn btn-ghost px-2.5 py-1 text-xs"
                      >
                        {t("leaderboard.history")}
                      </button>
                    ) : (
                      <span className="text-parch-700">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {botData ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-3 sm:p-6"
          onClick={closeBot}
        >
          <div
            className="panel flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="panel-header">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="truncate text-base font-bold text-parch-100">{botData.name}</h3>
                  <Badge className="border-violet-400/30 bg-violet-400/10 text-violet-300">
                    {t(`strategy.${botData.strategy}`)}
                  </Badge>
                </div>
                <p className="mt-0.5 text-xs text-parch-600">{botData.positions} {t("portfolio.positions", { count: botData.positions })}</p>
              </div>
              <button
                onClick={closeBot}
                className="btn btn-ghost px-2.5"
                aria-label={t("history.close")}
              >
                <X size={16} />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3 border-b border-ink-600/60 bg-ink-750/40 p-4 sm:grid-cols-4">
              {[
                [t("dashboard.portfolioValue"), money(botData.value)],
                [t("portfolio.statCash"), money(botData.cash)],
                [t("portfolio.statInvested"), money(botData.invested)],
                [t("dashboard.totalReturn"), percent(botData.return_pct)],
              ].map(([label, value]) => (
                <div key={label}>
                  <p className="text-[10px] uppercase tracking-wide text-parch-600">{label}</p>
                  <p className={`mt-0.5 truncate text-sm font-semibold tabular ${label === t("dashboard.totalReturn") ? toneClass(botData.return_pct) : "text-parch-100"}`}>
                    {value}
                  </p>
                </div>
              ))}
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto">
              <div className="border-b border-ink-600/60 p-3">
                <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-parch-500">
                  {t("history.equity")}
                </h4>
                {equityData.length > 1 ? (
                  <LineChart data={equityData} height={200} color="#38bdf8" />
                ) : (
                  <p className="px-3 py-6 text-center text-xs text-parch-600">{t("history.noHistory")}</p>
                )}
              </div>
              <div className="p-4">
                <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-parch-500">
                  {t("history.trades")}
                </h4>
                {botData.trades.length > 0 ? (
                  <table className="w-full min-w-[560px] border-collapse">
                    <thead>
                      <tr>
                        <th className="th">{t("portfolio.colTxDay")}</th>
                        <th className="th">{t("history.colStock")}</th>
                        <th className="th">{t("portfolio.colTxAction")}</th>
                        <th className="th">{t("portfolio.colTxShares")}</th>
                        <th className="th">{t("portfolio.colTxPrice")}</th>
                        <th className="th">{t("portfolio.colTxGross")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {botData.trades.map((trade) => (
                        <tr key={trade.id} className="hover:bg-ink-700/40">
                          <td className="td text-parch-600">{trade.day}</td>
                          <td className="td font-semibold text-parch-100">{trade.name}</td>
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
                          <td className="td text-parch-300">{trade.shares.toLocaleString()}</td>
                          <td className="td text-parch-300">{money(trade.price)}</td>
                          <td className="td text-parch-300">{money(trade.notional)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p className="px-3 py-6 text-center text-xs text-parch-600">{t("history.noTrades")}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
