import { useMemo, useState, useEffect } from "react";
import {
  Archive,
  CalendarDays,
  ChevronDown,
  ChevronUp,
  Flame,
  Hash,
  Landmark,
  User,
} from "lucide-react";

import { api } from "../../api/client.js";
import { useApp } from "../../store/AppContext.jsx";
import { Badge } from "../ui.jsx";

export default function StoriesArchiveView() {
  const { t } = useApp();
  const [tab, setTab] = useState("stories");
  const [stories, setStories] = useState([]);
  const [legends, setLegends] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [eraFilter, setEraFilter] = useState("all");
  const [openId, setOpenId] = useState(null);

  useEffect(() => {
    Promise.all([api.getStories(), api.getLegends(), api.getTimeline()])
      .then(([storyData, legendData, timelineData]) => {
        setStories(storyData.stories || []);
        setLegends(legendData.legends || []);
        setTimeline(timelineData.events || []);
      })
      .catch(() => {});
  }, []);

  const eras = useMemo(() => [...new Set(stories.map((story) => story.era))], [stories]);
  const visible = useMemo(
    () => (eraFilter === "all" ? stories : stories.filter((story) => story.era === eraFilter)),
    [stories, eraFilter]
  );

  const tabs = [
    { key: "stories", label: t("archive.tabStories") },
    { key: "legends", label: t("archive.tabLegends") },
    { key: "timeline", label: t("archive.tabTimeline") },
  ];

  return (
    <div className="space-y-4 p-4 lg:p-5">
      <section className="panel">
        <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[3px] border border-risk/40 bg-risk/10 text-risk">
              <Flame size={18} />
            </div>
            <div className="min-w-0">
              <h2 className="font-display text-sm font-semibold text-parch-100">{t("archive.title")}</h2>
              <p className="mt-0.5 text-xs text-parch-500">{t("archive.detail")}</p>
            </div>
          </div>
          <div className="flex items-center gap-1 rounded-[3px] border border-ink-600/70 bg-ink-900/70 p-1 sm:ml-auto">
            {tabs.map((item) => (
              <button
                key={item.key}
                onClick={() => setTab(item.key)}
                className={`rounded-[3px] px-3 py-1.5 text-xs font-semibold transition-colors ${
                  tab === item.key
                    ? "border border-brass/40 bg-brass/15 text-brass"
                    : "border border-transparent text-parch-500 hover:text-parch-200"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {tab === "stories" ? (
        <>
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs text-parch-500">{t("archive.tabStoriesDetail")}</p>
            <select
              value={eraFilter}
              onChange={(event) => setEraFilter(event.target.value)}
              className="input w-56"
            >
              <option value="all">{t("archive.all")}</option>
              {eras.map((era) => (
                <option key={era} value={era}>
                  {era}
                </option>
              ))}
            </select>
          </div>
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
                    <span className="absolute right-4 top-4 rotate-6 rounded-[3px] border-2 border-risk/40 bg-ink-900/70 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-risk/80">
                      {story.stamp}
                    </span>
                    <div className="flex items-center justify-between gap-3 border-b border-ink-600/70 px-4 py-3">
                      <span className="inline-flex items-center gap-1.5 rounded-[3px] border border-risk/40 bg-risk/10 px-2 py-0.5 text-[11px] font-semibold text-risk">
                        <Flame size={11} />
                        {story.era}
                      </span>
                      <span className="font-mono text-[11px] tabular text-parch-600">{story.file_no}</span>
                    </div>
                    <div className="space-y-3 p-4">
                      <div className="grid grid-cols-3 gap-2 rounded-[3px] border border-ink-600/70 bg-ink-900/60 p-2 text-[10px]">
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
                      <h3 className="font-display text-base font-bold leading-6 text-parch-100">{story.title}</h3>
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
        </>
      ) : null}

      {tab === "legends" ? (
        <>
          <p className="text-xs text-parch-500">{t("archive.tabLegendsDetail")}</p>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {legends.map((legend) => (
              <article key={legend.id} className="panel relative overflow-hidden">
                <span className="absolute right-4 top-4 rotate-6 rounded-[3px] border-2 border-brass/45 bg-ink-900/70 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-brass/90">
                  {legend.stamp}
                </span>
                <div className="flex items-center justify-between gap-3 border-b border-ink-600/70 px-4 py-3">
                  <span className="inline-flex items-center gap-1.5 rounded-[3px] border border-brass/40 bg-brass/10 px-2 py-0.5 text-[11px] font-semibold text-brass">
                    <Flame size={11} />
                    {legend.era}
                  </span>
                  <span className="font-mono text-[11px] tabular text-parch-600">{legend.file_no}</span>
                </div>
                <div className="space-y-3 p-4">
                  <div className="flex items-center justify-between gap-2">
                    <Badge className="border-ink-500/50 text-parch-500">{legend.tag}</Badge>
                    <p className="flex items-center gap-1 text-[10px] text-parch-600">
                      <User size={10} />
                      {legend.source}
                    </p>
                  </div>
                  <h3 className="font-display text-lg font-bold leading-7 text-parch-100">{legend.title}</h3>
                  <p className="text-sm leading-6 text-parch-300">{legend.story}</p>
                  <div className="rounded-[3px] border border-brass/35 bg-brass/10 px-3 py-2.5">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-brass">
                      {t("legend.footnote")}
                    </p>
                    <p className="mt-1 text-[11px] leading-5 text-parch-500">{legend.footnote}</p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </>
      ) : null}

      {tab === "timeline" ? (
        <>
          <p className="text-xs text-parch-500">{t("timeline.detail")}</p>
          <section className="panel p-5">
            <ol className="relative space-y-6 border-l border-brass/40 pl-6">
              {timeline.map((event) => (
                <li key={event.year} className="relative">
                  <span className="absolute -left-[31px] top-1 flex h-3 w-3 items-center justify-center">
                    <span className="h-2.5 w-2.5 rotate-45 rounded-[2px] border border-brass/60 bg-ink-800" />
                  </span>
                  <div className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:gap-4">
                    <p className="w-16 shrink-0 font-display text-lg font-bold tabular text-brass">
                      {event.year}
                    </p>
                    <div className="min-w-0">
                      <h3 className="flex items-center gap-2 text-sm font-semibold text-parch-100">
                        <Landmark size={14} className="shrink-0 text-brass" />
                        {event.title}
                      </h3>
                      <p className="mt-1 text-xs leading-5 text-parch-500">{event.fact}</p>
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </section>
        </>
      ) : null}
    </div>
  );
}
