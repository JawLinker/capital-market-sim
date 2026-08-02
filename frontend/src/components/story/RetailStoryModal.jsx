import { CalendarDays, Flame, Hash, Quote, User, X } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";

export default function RetailStoryModal() {
  const { story, nextStory, closeStory, t } = useApp();
  if (!story) return null;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-ink-950/70 p-4">
      <div className="panel w-full max-w-md overflow-hidden border-risk/30">
        <div className="flex items-center gap-2 border-b border-risk/25 bg-ink-850 px-4 py-3">
          <Flame size={16} className="text-risk" />
          <h2 className="text-sm font-semibold text-parch-100">{t("story.archiveTitle")}</h2>
          <button
            onClick={closeStory}
            className="ml-auto rounded p-1 text-parch-600 transition-colors hover:bg-ink-700 hover:text-parch-200"
            aria-label={t("story.dismiss")}
          >
            <X size={16} />
          </button>
        </div>
        <div className="space-y-3 bg-gradient-to-b from-risk/[0.06] to-transparent p-5">
          <div className="flex items-center justify-between gap-3">
            <span className="inline-flex items-center gap-1.5 rounded border border-risk/40 bg-risk/10 px-2 py-0.5 text-[11px] font-semibold tracking-wide text-risk">
              <Flame size={11} />
              {story.tag}
            </span>
            <span className="font-mono text-[11px] tabular text-parch-600">{story.file_no}</span>
          </div>
          <div className="grid grid-cols-3 gap-2 rounded-md border border-ink-600/70 bg-ink-900/60 p-2 text-[10px]">
            <div className="min-w-0">
              <p className="flex items-center gap-1 text-parch-600">
                <Hash size={10} />
                {t("archive.fileNo")}
              </p>
              <p className="mt-0.5 truncate font-mono text-parch-300">{story.file_no}</p>
            </div>
            <div className="min-w-0">
              <p className="flex items-center gap-1 text-parch-600">
                <CalendarDays size={10} />
                {t("archive.recordDate")}
              </p>
              <p className="mt-0.5 truncate text-parch-300">{story.date}</p>
            </div>
            <div className="min-w-0">
              <p className="flex items-center gap-1 text-parch-600">
                <User size={10} />
                {t("archive.source")}
              </p>
              <p className="mt-0.5 truncate text-parch-300">{story.source}</p>
            </div>
          </div>
          <div>
            <h3 className="mt-1 text-xl font-bold leading-7 text-parch-100">{story.title}</h3>
          </div>
          <p className="border-l-2 border-risk/40 pl-3 text-sm italic leading-6 text-parch-500">
            {story.prologue}
          </p>
          <div className="flex items-center gap-2 py-1">
            <span className="h-px flex-1 bg-ink-600/70" />
            <Flame size={12} className="text-risk/70" />
            <span className="h-px flex-1 bg-ink-600/70" />
          </div>
          <div className="relative">
            <span className="absolute -top-1 right-0 rotate-6 rounded border-2 border-risk/40 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-risk/80">
              {story.stamp}
            </span>
            <p className="pr-24 text-sm leading-6 text-parch-300">{story.story}</p>
          </div>
          <p className="text-[11px] text-parch-600">{t("story.fiction")}</p>
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
