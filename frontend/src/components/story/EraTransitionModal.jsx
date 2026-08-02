import { Flame, X } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";

const GRADE_STYLE = {
  gold: {
    border: "border-gold/60",
    text: "text-gold",
    bg: "from-gold/15",
  },
  silver: {
    border: "border-parch-400/50",
    text: "text-parch-200",
    bg: "from-parch-400/10",
  },
  bronze: {
    border: "border-brass/60",
    text: "text-brass",
    bg: "from-brass/15",
  },
  dark: {
    border: "border-ink-500/60",
    text: "text-parch-600",
    bg: "from-ink-500/20",
  },
};

export default function EraTransitionModal() {
  const { eraTransition, closeEraTransition, t } = useApp();
  if (!eraTransition) return null;
  const grade = eraTransition.grade || { key: "bronze", label: t("chronicle.gradeBronze") };
  const style = GRADE_STYLE[grade.key] || GRADE_STYLE.bronze;
  const flavorKey = `chronicle.grade${grade.key.charAt(0).toUpperCase()}${grade.key.slice(1)}Flavor`;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-ink-950/80 p-4">
      <div className={`panel relative w-full max-w-lg overflow-hidden border ${style.border}`}>
        <div className={`bg-gradient-to-b ${style.bg} to-transparent px-8 py-10 text-center`}>
          <button
            onClick={closeEraTransition}
            className="absolute right-3 top-3 rounded p-1 text-parch-600 transition-colors hover:bg-ink-700 hover:text-parch-200"
            aria-label={t("story.dismiss")}
          >
            <X size={16} />
          </button>
          <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-parch-600">
            {t("chronicle.newEra")}
          </p>
          <p className={`mt-3 font-display text-5xl font-bold tabular ${style.text}`}>
            {eraTransition.year}
          </p>
          <h2 className={`mt-2 font-display text-2xl font-bold ${style.text}`}>{grade.label}</h2>
          <div className="mx-auto mt-4 flex max-w-sm items-center gap-2">
            <span className="h-px flex-1 bg-current opacity-30" />
            <Flame size={14} className={style.text} />
            <span className="h-px flex-1 bg-current opacity-30" />
          </div>
          <p className="mt-4 text-sm leading-6 text-parch-400">{t(flavorKey)}</p>
          <button onClick={closeEraTransition} className="btn btn-primary mt-6 px-5">
            {t("story.close")}
          </button>
        </div>
      </div>
    </div>
  );
}
