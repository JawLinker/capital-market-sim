import { useEffect, useState } from "react";
import {
  CheckCircle2,
  Lock,
  Target,
  Trophy,
} from "lucide-react";

import { api } from "../../api/client.js";
import { useApp } from "../../store/AppContext.jsx";
import { ArchiveCard, MuseumHeader } from "../museum.jsx";
import { Badge } from "../ui.jsx";

export default function QuestBookView() {
  const { chronicle, t } = useApp();
  const [book, setBook] = useState({ arcs: [] });

  useEffect(() => {
    api
      .getChronicleBook()
      .then((data) => setBook(data || { arcs: [] }))
      .catch(() => {});
  }, []);

  const activeArc =
    book.arcs.find((arc) => arc.key === chronicle?.arc_key) ||
    book.arcs.find((arc) => arc.beats.some((beat) => beat.status === "current")) ||
    book.arcs[0];
  const currentBeat = activeArc?.beats.find((beat) => beat.status === "current");

  return (
    <div className="space-y-4 p-4 lg:p-5">
      <MuseumHeader
        kicker={t("quest.kicker")}
        title={t("quest.title")}
        detail={t("quest.detail")}
      />

      {currentBeat ? (
        <ArchiveCard
          stamp={chronicle?.stamp}
          header={
            <div className="flex w-full flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="flex items-center gap-2 font-display text-[15px] font-semibold text-parch-100">
                  <Target size={15} className="text-brass" />
                  {t("quest.currentTask")}
                </h2>
                <p className="mt-0.5 text-xs text-parch-500">
                  {t("chronicle.chapter", {
                    index: currentBeat.index,
                    total: activeArc.beats.length,
                  })}
                  {" · "}
                  {activeArc.title}
                </p>
              </div>
              <Badge className="border-brass/40 bg-brass/10 text-brass">
                {activeArc.key}
              </Badge>
            </div>
          }
        >
          <h3 className="font-display text-lg font-bold leading-7 text-parch-100">
            {currentBeat.title}
          </h3>
          <p className="mt-2 border-l-2 border-brass/40 pl-3 text-sm italic leading-6 text-parch-500">
            {currentBeat.prose}
          </p>
          {currentBeat.objective ? (
            <div className="mt-4 rounded-[3px] border border-ink-600/70 bg-ink-900/60 p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-parch-600">
                  {t("chronicle.objective")}
                </p>
                <span
                  className={`rounded-[3px] border px-2 py-0.5 text-[10px] font-bold ${
                    currentBeat.objective.met
                      ? "border-mint/40 bg-mint/10 text-mint"
                      : "border-brass/40 bg-brass/10 text-brass"
                  }`}
                >
                  {currentBeat.objective.met ? t("chronicle.met") : t("chronicle.notMet")}
                </span>
              </div>
              <p className="mt-2 text-xs text-parch-300">{currentBeat.objective.label}</p>
              <p className="mt-1 text-xs tabular text-parch-500">
                {currentBeat.objective.current.toLocaleString()} /{" "}
                {currentBeat.objective.target.toLocaleString()}
              </p>
              {currentBeat.objective.target > 0 ? (
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-ink-600">
                  <div
                    className="h-full rounded-full bg-brass"
                    style={{
                      width: `${Math.min(
                        100,
                        (currentBeat.objective.current / currentBeat.objective.target) * 100
                      )}%`,
                    }}
                  />
                </div>
              ) : null}
            </div>
          ) : null}
          <div className="mt-4 flex items-center gap-2 rounded-[3px] border border-gold/40 bg-gold/10 px-3 py-2.5">
            <Trophy size={14} className="text-gold" />
            <p className="text-xs text-parch-300">
              {t("quest.reward")}:{" "}
              <span className="font-semibold text-gold">{currentBeat.reward?.label}</span>
            </p>
          </div>
        </ArchiveCard>
      ) : null}

      <section className="space-y-4">
        {book.arcs.map((arc) => {
          const completed = arc.beats.filter((beat) => beat.status === "passed").length;
          return (
            <article key={arc.key} className="panel overflow-hidden">
              <div className="flex items-center justify-between gap-3 border-b border-ink-600/70 px-4 py-3">
                <div>
                  <p className="font-mono text-[11px] tabular text-parch-600">{arc.key}</p>
                  <h3 className="mt-0.5 font-display text-base font-bold text-parch-100">
                    {arc.title}
                  </h3>
                  <p className="mt-0.5 text-xs text-parch-500">{arc.summary}</p>
                </div>
                <Badge className="border-brass/40 bg-brass/10 text-brass">
                  {completed}/{arc.beats.length}
                </Badge>
              </div>
              <ol className="divide-y divide-ink-600/50">
                {arc.beats.map((beat) => (
                  <li
                    key={beat.id}
                    className={`flex items-start gap-3 px-4 py-3 ${
                      beat.status === "current" ? "bg-risk/[0.06]" : ""
                    }`}
                  >
                    {beat.status === "passed" ? (
                      <CheckCircle2 size={15} className="mt-0.5 shrink-0 text-mint" />
                    ) : beat.status === "current" ? (
                      <Target size={15} className="mt-0.5 shrink-0 text-risk" />
                    ) : (
                      <Lock size={15} className="mt-0.5 shrink-0 text-ink-500" />
                    )}
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-xs font-semibold text-parch-200">
                          {beat.index}. {beat.title}
                        </p>
                        <span className="font-mono text-[10px] tabular text-parch-600">
                          {beat.date}
                        </span>
                      </div>
                      {beat.status !== "locked" ? (
                        <p className="mt-1 flex items-center gap-1.5 text-[11px] text-parch-500">
                          <Trophy size={11} className="text-gold" />
                          {t("quest.reward")}: {beat.reward?.label}
                        </p>
                      ) : (
                        <p className="mt-1 text-[11px] text-parch-600">{t("quest.locked")}</p>
                      )}
                    </div>
                  </li>
                ))}
              </ol>
            </article>
          );
        })}
      </section>
    </div>
  );
}
