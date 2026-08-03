import { useState } from "react";
import {
  Newspaper as NewspaperIcon,
  TrendingDown,
  TrendingUp,
  X,
} from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";

export default function NewspaperModal() {
  const { newspaper, marketSummary, closeNewspaper, gameState, t } = useApp();
  const [page, setPage] = useState("front");
  if (!newspaper) return null;
  const positive = newspaper.kind === "earnings_beat";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-950/85 p-4">
      <div className="paper-panel relative w-full max-w-lg overflow-hidden">
        <button
          onClick={closeNewspaper}
          className="absolute right-3 top-3 rounded p-1 text-ink-900/50 transition-colors hover:bg-ink-900/10 hover:text-ink-900"
          aria-label={t("story.dismiss")}
        >
          <X size={16} />
        </button>
        <div className="border-b-2 border-ink-900/30 px-6 pb-3 pt-5 text-center">
          <p className="flex items-center justify-center gap-2 text-[10px] font-semibold uppercase tracking-[0.3em] text-ink-900/60">
            <NewspaperIcon size={12} />
            {t("newspaper.title")}
          </p>
          <p className="mt-1 font-display text-3xl font-bold tracking-[0.08em] text-ink-950">
            {t("newspaper.title")}
          </p>
          <p className="mt-1 text-[11px] text-ink-900/60">
            {gameState?.market?.date || ""}
          </p>
          <div className="mt-3 flex justify-center gap-2">
            <button
              onClick={() => setPage("front")}
              className={`rounded-[3px] border px-2.5 py-1 text-[11px] font-semibold transition-colors ${
                page === "front"
                  ? "border-ink-900 bg-ink-900 text-parch-100"
                  : "border-ink-900/30 text-ink-900/70 hover:bg-ink-900/10"
              }`}
            >
              {t("newspaper.frontPage")}
            </button>
            <button
              onClick={() => setPage("second")}
              className={`rounded-[3px] border px-2.5 py-1 text-[11px] font-semibold transition-colors ${
                page === "second"
                  ? "border-ink-900 bg-ink-900 text-parch-100"
                  : "border-ink-900/30 text-ink-900/70 hover:bg-ink-900/10"
              }`}
            >
              {t("newspaper.secondPage")}
            </button>
          </div>
        </div>
        <div className="space-y-3 px-6 py-5">
          {page === "front" ? (
            <>
              <div className="flex items-center gap-2">
                <span className="rounded-[3px] border border-ink-900/30 bg-ink-900/10 px-2 py-0.5 text-[11px] font-bold text-ink-900">
                  {newspaper.name}
                </span>
                <span
                  className={`flex items-center gap-1 text-[11px] font-semibold ${
                    positive ? "text-ink-900" : "text-risk"
                  }`}
                >
                  {positive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                  {newspaper.impact_pct > 0 ? "+" : ""}
                  {newspaper.impact_pct}%
                </span>
              </div>
              <h3 className="font-display text-xl font-bold leading-7 text-ink-950">
                {newspaper.headline}
              </h3>
              <p className="text-sm leading-6 text-ink-900/80">{newspaper.summary}</p>
            </>
          ) : (
            <div className="space-y-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-ink-900/60">
                {t("newspaper.secondTitle")}
              </p>
              <div className="flex items-center justify-between rounded-[3px] border border-ink-900/20 bg-ink-900/5 px-3 py-2">
                <span className="text-xs font-semibold text-ink-900">
                  {t("home.northbound")}
                </span>
                <span
                  className={`text-xs font-bold tabular ${
                    (marketSummary?.northbound_flow || 0) >= 0
                      ? "text-ink-900"
                      : "text-risk"
                  }`}
                >
                  {(marketSummary?.northbound_flow || 0) >= 0 ? "+" : ""}
                  {marketSummary?.northbound_flow}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-[3px] border border-ink-900/20 p-3">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-ink-900/60">
                    {t("dashboard.gainers")}
                  </p>
                  {(marketSummary?.gainers || []).map((stock) => (
                    <p key={stock.name} className="mt-1.5 flex justify-between text-xs">
                      <span className="text-ink-900">{stock.name}</span>
                      <span className="font-semibold text-ink-900">
                        +{stock.change_pct}%
                      </span>
                    </p>
                  ))}
                </div>
                <div className="rounded-[3px] border border-ink-900/20 p-3">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-ink-900/60">
                    {t("dashboard.losers")}
                  </p>
                  {(marketSummary?.losers || []).map((stock) => (
                    <p key={stock.name} className="mt-1.5 flex justify-between text-xs">
                      <span className="text-ink-900">{stock.name}</span>
                      <span className="font-semibold text-risk">
                        {stock.change_pct}%
                      </span>
                    </p>
                  ))}
                </div>
              </div>
            </div>
          )}
          <div className="flex items-center justify-between border-t border-ink-900/20 pt-3">
            <p className="text-[10px] uppercase tracking-[0.16em] text-ink-900/50">
              {t("newspaper.impact")}
            </p>
            <button onClick={closeNewspaper} className="btn btn-ghost px-4">
              {t("newspaper.read")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
