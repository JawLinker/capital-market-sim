import { useMemo, useState, useEffect } from "react";
import {
  Archive,
  CalendarDays,
  ChevronDown,
  ChevronUp,
  Flame,
  Hash,
  User,
} from "lucide-react";

import { api } from "../../api/client.js";
import { useApp } from "../../store/AppContext.jsx";

export default function StoriesArchiveView() {
  const { t } = useApp();
  const [stories, setStories] = useState([]);
  const [eraFilter, setEraFilter] = useState("all");
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    api
      .getStories()
      .then((data) => setStories(data.stories || []))
      .catch(() => setStories([]));
  }, []);

  const eras = useMemo(() => [...new Set(stories.map((story) => story.era))], [stories]);
  const visible = useMemo(
    () => (eraFilter === "all" ? stories : stories.filter((story) => story.era === eraFilter)),
    [stories, eraFilter]
  );

  return (
    <div className="space-y-4 p-4 lg:p-5">
      <section className="panel">
        <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-risk/40 bg-risk/10 text-risk">
              <Flame size={18} />
            </div>
            <div className="min-w-0">
              <h2 className="text-sm font-semibold text-parch-100">{t("archive.title")}</h2>
              <p className="mt-0.5 text-xs text-parch-600">{t("archive.detail")}</p>
            </div>
          </div>
          <select
            value={eraFilter}
            onChange={(event) => setEraFilter(event.target.value)}
            className="input w-full sm:ml-auto sm:w-64"
          >
            <option value="all">{t("archive.all")}</option>
            {eras.map((era) => (
              <option key={era} value={era}>
                {era}
              </option>
            ))}
          </select>
        </div>
      </section>

      {visible.length === 0 ? (
        <section className="panel flex flex-col items-center gap-2 p-10 text-center">
          <Archive size={22} className="text-parch-600" />
          <p className="text-sm text-parch-500">{t("archive.empty")}</p>
        </section>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {visible.map((story) => {
            const open = openId === story.id;
            return (
              <article key={story.id} className="panel relative overflow-hidden">
                <span className="absolute right-4 top-4 rotate-6 rounded border-2 border-risk/40 bg-ink-900/70 px-2 py-1 text-[10px] font-bold uppercase tracking-widest text-risk/80">
                  {story.stamp}
                </span>
                <div className="flex items-center justify-between gap-3 border-b border-ink-600/70 px-4 py-3">
                  <span className="inline-flex items-center gap-1.5 rounded border border-risk/40 bg-risk/10 px-2 py-0.5 text-[11px] font-semibold text-risk">
                    <Flame size={11} />
                    {story.era}
                  </span>
                  <span className="font-mono text-[11px] tabular text-parch-600">{story.file_no}</span>
                </div>
                <div className="space-y-3 p-4">
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
                  <h3 className="text-base font-bold leading-6 text-parch-100">{story.title}</h3>
                  <p className="border-l-2 border-risk/40 pl-3 text-sm italic leading-6 text-parch-500">
                    {story.prologue}
                  </p>
                  {open ? (
                    <p className="text-sm leading-6 text-parch-300">{story.story}</p>
                  ) : null}
                  <button
                    onClick={() => setOpenId(open ? null : story.id)}
                    className="btn btn-ghost w-full"
                  >
                    {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    {open ? t("archive.collapse") : t("archive.read")}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
