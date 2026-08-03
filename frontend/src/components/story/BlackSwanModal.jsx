import { CloudLightning, X } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";

export default function BlackSwanModal() {
  const { blackSwan, closeBlackSwan, resolveBlackSwanOption, t } = useApp();
  if (!blackSwan) return null;
  const delta = blackSwan.sentiment_delta || 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-950/85 p-4">
      <div className="panel relative w-full max-w-lg overflow-hidden border-risk/50">
        <div className="flex items-center gap-2 border-b border-risk/30 bg-ink-850 px-4 py-3">
          <CloudLightning size={17} className="text-risk" />
          <h2 className="text-sm font-semibold text-parch-100">{t("blackswan.title")}</h2>
          <button
            onClick={closeBlackSwan}
            className="ml-auto rounded p-1 text-parch-600 transition-colors hover:bg-ink-700 hover:text-parch-200"
            aria-label={t("story.dismiss")}
          >
            <X size={16} />
          </button>
        </div>
        <div className="space-y-4 bg-gradient-to-b from-risk/[0.08] to-transparent p-6">
          <p className="font-mono text-[11px] tabular text-parch-600">
            {blackSwan.date || "…"}
          </p>
          <h3 className="font-display text-2xl font-bold leading-8 text-parch-100">
            {blackSwan.title}
          </h3>
          <p className="border-l-2 border-risk/50 pl-3 text-sm italic leading-6 text-parch-400">
            {blackSwan.prose}
          </p>
          {(blackSwan.options || []).length > 0 ? (
            <div className="space-y-2">
              <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-parch-600">
                {t("decision.title")}
              </p>
              {blackSwan.options.map((option) => (
                <button
                  key={option.key}
                  onClick={() => resolveBlackSwanOption(option)}
                  className="flex w-full items-center justify-between gap-3 rounded-[3px] border border-ink-600/70 bg-ink-900/60 px-3 py-2.5 text-left transition-colors hover:border-risk/50 hover:bg-risk/10"
                >
                  <span className="text-xs font-semibold text-parch-100">{option.label}</span>
                  <span className="text-[10px] text-parch-500">{option.detail}</span>
                </button>
              ))}
            </div>
          ) : null}
          <div className="rounded-[3px] border border-ink-600/70 bg-ink-900/60 p-3">
            <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-parch-600">
              {t("blackswan.effect")}
            </p>
            <p className={`mt-1.5 text-sm font-bold tabular ${delta >= 0 ? "text-mint" : "text-risk"}`}>
              {delta >= 0 ? "+" : ""}
              {Math.round(delta * 100)}%
            </p>
          </div>
          <div className="flex justify-end pt-1">
            <button onClick={closeBlackSwan} className="btn btn-danger px-4">
              {t("blackswan.ack")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
