import { Flame, Target, X } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";

export default function ChronicleModal() {
  const { chronicle, closeChronicle, t } = useApp();
  if (!chronicle) return null;
  const current = chronicle.beats.find((beat) => beat.status === "current") || chronicle.beats[chronicle.beats.length - 1];
  const total = chronicle.beats.length;
  const objective = current?.objective;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-ink-950/70 p-4">
      <div className="panel w-full max-w-md overflow-hidden border-brass/30">
        <div className="flex items-center gap-2 border-b border-brass/25 bg-ink-850 px-4 py-3">
          <Flame size={16} className="text-brass" />
          <h2 className="text-sm font-semibold text-parch-100">{t("chronicle.title")}</h2>
          <button
            onClick={closeChronicle}
            className="ml-auto rounded p-1 text-parch-600 transition-colors hover:bg-ink-700 hover:text-parch-200"
            aria-label={t("story.dismiss")}
          >
            <X size={16} />
          </button>
        </div>
        <div className="space-y-3 bg-gradient-to-b from-brass/[0.07] to-transparent p-5">
          <div className="flex items-center justify-between gap-3">
            <span className="inline-flex items-center gap-1.5 rounded-[3px] border border-brass/40 bg-brass/10 px-2 py-0.5 text-[11px] font-semibold text-brass">
              <Flame size={11} />
              {chronicle.stamp}
            </span>
            <span className="font-mono text-[11px] tabular text-parch-600">
              {t("chronicle.chapter", { index: current?.index || total, total })}
            </span>
          </div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-parch-600">
            {chronicle.title}
          </p>
          <h3 className="font-display text-xl font-bold leading-7 text-parch-100">{current?.title}</h3>
          <p className="border-l-2 border-brass/40 pl-3 text-sm italic leading-6 text-parch-500">
            {current?.prose}
          </p>
          {objective ? (
            <div className="rounded-[3px] border border-ink-600/70 bg-ink-900/60 p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-parch-600">
                  <Target size={11} className="text-brass" />
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
          ) : null}
          <div className="flex justify-end pt-1">
            <button onClick={closeChronicle} className="btn btn-primary px-3">
              {t("story.close")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
