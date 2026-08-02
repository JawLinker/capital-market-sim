import { MessageCircleMore, Quote, X } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";

export default function RetailStoryModal() {
  const { story, nextStory, closeStory, t } = useApp();
  if (!story) return null;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-ink-950/70 p-4">
      <div className="panel w-full max-w-md overflow-hidden">
        <div className="flex items-center gap-2 border-b border-ink-600/70 bg-ink-800/70 px-4 py-3">
          <MessageCircleMore size={16} className="text-gold" />
          <h2 className="text-sm font-semibold text-slate-100">{t("story.title")}</h2>
          <button
            onClick={closeStory}
            className="ml-auto rounded p-1 text-slate-500 transition-colors hover:bg-ink-700 hover:text-slate-200"
            aria-label={t("story.dismiss")}
          >
            <X size={16} />
          </button>
        </div>
        <div className="space-y-3 p-5">
          <span className="inline-flex rounded border border-gold/40 bg-gold/10 px-2 py-0.5 text-[11px] font-semibold text-gold">
            {story.tag}
          </span>
          <h3 className="text-lg font-bold leading-6 text-slate-50">{story.title}</h3>
          <p className="text-sm leading-6 text-slate-300">{story.story}</p>
          <p className="text-[11px] text-slate-500">{t("story.fiction")}</p>
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={nextStory} className="btn btn-ghost px-3">
              <Quote size={14} />
              {t("story.another")}
            </button>
            <button onClick={closeStory} className="btn btn-primary px-3">
              {t("story.close")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
