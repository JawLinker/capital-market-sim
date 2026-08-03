import { useEffect, useState } from "react";
import { Activity, Percent, Scale, TrendingDown } from "lucide-react";

import { api } from "../../api/client.js";
import { useApp } from "../../store/AppContext.jsx";
import { eraForDate } from "../../utils/era.js";
import { money } from "../../utils/format.js";
import { EraBadge, MuseumHeader } from "../museum.jsx";
import { Badge, EmptyState, SectionTitle, StatCard } from "../ui.jsx";

export default function ReplayView() {
  const { t, lang } = useApp();
  const [data, setData] = useState({ stats: {}, trades: [] });

  useEffect(() => {
    api
      .getReplay()
      .then(setData)
      .catch(() => {});
  }, []);

  const stats = data.stats || {};
  const trades = [...(data.trades || [])].reverse();

  return (
    <div className="space-y-4 p-4 lg:p-5">
      <MuseumHeader
        kicker={t("replay.kicker")}
        title={t("replay.title")}
        detail={t("replay.detail")}
      />

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label={t("replay.trades")}
          value={stats.total_trades ?? 0}
          icon={<Activity size={17} />}
        />
        <StatCard
          label={t("replay.winRate")}
          value={`${stats.win_rate ?? 0}%`}
          icon={<Percent size={17} />}
        />
        <StatCard
          label={t("replay.realized")}
          value={money(stats.total_realized)}
          tone={(stats.total_realized || 0) >= 0 ? "positive" : "negative"}
          icon={<Scale size={17} />}
        />
        <StatCard
          label={t("replay.drawdown")}
          value={`-${stats.max_drawdown ?? 0}%`}
          tone="negative"
          icon={<TrendingDown size={17} />}
        />
      </div>

      <section className="panel overflow-hidden">
        <SectionTitle title={t("replay.journal")} detail={t("replay.journalDetail")} />
        {trades.length > 0 ? (
          <div className="space-y-2 p-4">
            {trades.map((trade) => {
              const era = eraForDate(trade.date, lang);
              return (
                <article
                  key={trade.id}
                  className="flex flex-wrap items-center gap-3 rounded-[3px] border border-ink-600/60 bg-ink-900/50 px-3 py-2.5"
                >
                  <EraBadge tone="brass">{era.label}</EraBadge>
                  <Badge
                    className={
                      trade.action === "buy"
                        ? "border-mint/40 bg-mint/10 text-mint"
                        : "border-risk/40 bg-risk/10 text-risk"
                    }
                  >
                    {t(trade.action === "buy" ? "order.buy" : "order.sell")}
                  </Badge>
                  <p className="text-xs font-semibold text-parch-100">{trade.name}</p>
                  <p className="text-[11px] tabular text-parch-500">
                    {trade.date || `${t("replay.day")} ${trade.day}`} · {trade.shares.toFixed(4)} @{" "}
                    {money(trade.price)}
                  </p>
                  <span
                    className={`ml-auto text-xs font-semibold tabular ${
                      trade.realized_pnl > 0
                        ? "text-mint"
                        : trade.realized_pnl < 0
                          ? "text-risk"
                          : "text-parch-500"
                    }`}
                  >
                    {trade.realized_pnl
                      ? `${trade.realized_pnl > 0 ? "+" : ""}${money(trade.realized_pnl)}`
                      : "…"}
                  </span>
                </article>
              );
            })}
          </div>
        ) : (
          <EmptyState title={t("replay.empty")} detail={t("replay.emptyDetail")} />
        )}
      </section>
    </div>
  );
}
