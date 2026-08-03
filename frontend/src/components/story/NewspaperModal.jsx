import { Newspaper as NewspaperIcon, TrendingDown, TrendingUp, X } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";

export default function NewspaperModal() {
  const { newspaper, closeNewspaper, gameState, t } = useApp();
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
        </div>
        <div className="space-y-3 px-6 py-5">
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
