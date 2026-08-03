import { useEffect, useState } from "react";
import {
  CalendarDays,
  CheckCircle2,
  Dices,
  Lock,
  MessagesSquare,
  Scale,
  Target,
  Trophy,
} from "lucide-react";

import { api } from "../../api/client.js";
import { useApp } from "../../store/AppContext.jsx";
import { money } from "../../utils/format.js";
import Avatar from "../Avatar.jsx";
import { ArchiveCard, MuseumHeader } from "../museum.jsx";
import { Badge } from "../ui.jsx";

function ObjectiveBlock({ objective, t }) {
  if (!objective) return null;
  return (
    <div className="rounded-[3px] border border-ink-600/70 bg-ink-900/60 p-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-parch-600">
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
            style={{
              width: `${Math.min(100, (objective.current / objective.target) * 100)}%`,
            }}
          />
        </div>
      ) : null}
    </div>
  );
}

export default function QuestBookView() {
  const { chronicle, t } = useApp();
  const [book, setBook] = useState({ arcs: [] });
  const [daily, setDaily] = useState(null);
  const [commission, setCommission] = useState(null);
  const [storylines, setStorylines] = useState([]);
  const [rivals, setRivals] = useState([]);
  const [duels, setDuels] = useState([]);
  const [rivalId, setRivalId] = useState("");
  const [stake, setStake] = useState("100");
  const [days, setDays] = useState(10);
  const [duelNotice, setDuelNotice] = useState("");

  useEffect(() => {
    Promise.all([
      api.getChronicleBook(),
      api.getDailyQuest(),
      api.getCommission(),
      api.getStorylines(),
      api.getBots(),
      api.getDuels(),
    ])
      .then(([bookData, dailyData, commissionData, storylineData, botData, duelData]) => {
        setBook(bookData || { arcs: [] });
        setDaily(dailyData);
        setCommission(commissionData);
        setStorylines(storylineData?.storylines || []);
        setRivals(botData?.bots || []);
        setDuels(duelData?.duels || []);
        if (botData?.bots?.length) setRivalId(String(botData.bots[0].id));
      })
      .catch(() => {});
  }, []);

  const placeDuel = () => {
    setDuelNotice("");
    api
      .createDuel(Number(rivalId), Number.parseFloat(stake), days)
      .then(() => {
        setDuelNotice(t("duel.placed"));
        return api.getDuels();
      })
      .then((data) => setDuels(data.duels || []))
      .catch((error) => setDuelNotice(error.message));
  };

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
          <div className="mt-4">
            <ObjectiveBlock objective={currentBeat.objective} t={t} />
          </div>
          <div className="mt-4 flex items-center gap-2 rounded-[3px] border border-gold/40 bg-gold/10 px-3 py-2.5">
            <Trophy size={14} className="text-gold" />
            <p className="text-xs text-parch-300">
              {t("quest.reward")}:{" "}
              <span className="font-semibold text-gold">{currentBeat.reward?.label}</span>
            </p>
          </div>
        </ArchiveCard>
      ) : null}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <ArchiveCard
          header={
            <div>
              <h2 className="flex items-center gap-2 font-display text-[15px] font-semibold text-parch-100">
                <CalendarDays size={15} className="text-brass" />
                {t("quest.daily")}
              </h2>
              <p className="mt-0.5 text-xs text-parch-500">{t("quest.dailyDetail")}</p>
            </div>
          }
        >
          {daily ? (
            <>
              <p className="font-mono text-[11px] tabular text-parch-600">{daily.date}</p>
              <p className="mt-2 text-sm leading-6 text-parch-400">{daily.description}</p>
              <div className="mt-3">
                <ObjectiveBlock objective={daily.objective} t={t} />
              </div>
              <div className="mt-3 flex items-center gap-2 rounded-[3px] border border-gold/40 bg-gold/10 px-3 py-2.5">
                <Trophy size={14} className="text-gold" />
                <p className="text-xs text-parch-300">
                  {t("quest.reward")}:{" "}
                  <span className="font-semibold text-gold">{daily.reward?.label}</span>
                </p>
              </div>
            </>
          ) : (
            <p className="text-xs text-parch-600">…</p>
          )}
        </ArchiveCard>

        <ArchiveCard
          header={
            <div>
              <h2 className="flex items-center gap-2 font-display text-[15px] font-semibold text-parch-100">
                <MessagesSquare size={15} className="text-brass" />
                {t("quest.commission")}
              </h2>
              <p className="mt-0.5 text-xs text-parch-500">{t("quest.commissionDetail")}</p>
            </div>
          }
        >
          {commission ? (
            <>
              <div className="flex items-center gap-3">
                <Avatar seed={commission.npc?.name} iconKey={commission.npc?.icon} size={34} />
                <div>
                  <p className="text-[10px] uppercase tracking-[0.12em] text-parch-600">
                    {t("quest.from")}
                  </p>
                  <p className="font-display text-sm font-bold text-parch-100">
                    {commission.npc?.name}
                  </p>
                </div>
              </div>
              <p className="mt-3 text-sm leading-6 text-parch-400">{commission.description}</p>
              <div className="mt-3">
                <ObjectiveBlock objective={commission.objective} t={t} />
              </div>
              <div className="mt-3 flex items-center gap-2 rounded-[3px] border border-gold/40 bg-gold/10 px-3 py-2.5">
                <Trophy size={14} className="text-gold" />
                <p className="text-xs text-parch-300">
                  {t("quest.reward")}:{" "}
                  <span className="font-semibold text-gold">{commission.reward?.label}</span>
                </p>
              </div>
            </>
          ) : (
            <p className="text-xs text-parch-600">…</p>
          )}
        </ArchiveCard>
      </div>

      <section>
        <div className="mb-3 flex items-center gap-2">
          <MessagesSquare size={16} className="text-brass" />
          <h2 className="font-display text-lg font-bold text-parch-100">
            {t("quest.storylines")}
          </h2>
          <p className="text-xs text-parch-500">{t("quest.storylinesDetail")}</p>
        </div>
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
          {storylines.map((line) => {
            const current = line.chapters.find((chapter) => chapter.status === "current");
            return (
              <article key={line.key} className="panel overflow-hidden">
                <div className="flex items-center gap-3 border-b border-ink-600/70 px-4 py-3">
                  <Avatar seed={line.name} iconKey={line.icon} size={34} />
                  <div className="min-w-0">
                    <h3 className="font-display text-sm font-bold text-parch-100">{line.name}</h3>
                    <p className="text-[11px] text-parch-500">
                      {line.completed
                        ? t("chronicle.met")
                        : `${line.current_chapter}/${line.chapters.length}`}
                    </p>
                  </div>
                  {line.completed ? (
                    <Badge className="ml-auto border-mint/40 bg-mint/10 text-mint">
                      {t("quest.completed")}
                    </Badge>
                  ) : null}
                </div>
                <div className="space-y-3 p-4">
                  <ol className="flex flex-wrap items-center gap-1.5">
                    {line.chapters.map((chapter) => (
                      <li
                        key={chapter.id}
                        title={chapter.title}
                        className={`rounded-[3px] border px-2 py-1 text-[10px] font-semibold ${
                          chapter.status === "current"
                            ? "border-risk/50 bg-risk/10 text-risk"
                            : chapter.status === "passed"
                              ? "border-brass/35 bg-brass/5 text-brass"
                              : "border-ink-600/80 text-parch-600"
                        }`}
                      >
                        {chapter.index}
                      </li>
                    ))}
                  </ol>
                  {current ? (
                    <>
                      <h4 className="text-sm font-semibold text-parch-100">{current.title}</h4>
                      <p className="text-xs italic leading-5 text-parch-500">{current.prose}</p>
                      <ObjectiveBlock objective={current.objective} t={t} />
                      <p className="flex items-center gap-1.5 text-[11px] text-parch-500">
                        <Trophy size={11} className="text-gold" />
                        {t("quest.reward")}: {current.reward}
                      </p>
                    </>
                  ) : (
                    <p className="text-xs text-parch-600">{t("quest.locked")}</p>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section>
        <div className="mb-3 flex items-center gap-2">
          <Dices size={16} className="text-brass" />
          <h2 className="font-display text-lg font-bold text-parch-100">{t("duel.title")}</h2>
          <p className="text-xs text-parch-500">{t("duel.detail")}</p>
        </div>
        <div className="panel p-4">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <select
              value={rivalId}
              onChange={(event) => setRivalId(event.target.value)}
              className="input"
            >
              {rivals.map((rival) => (
                <option key={rival.id} value={rival.id}>
                  {rival.name} ({rival.return_pct}%)
                </option>
              ))}
            </select>
            <input
              type="number"
              min="1"
              value={stake}
              onChange={(event) => setStake(event.target.value)}
              className="input tabular"
              aria-label={t("duel.stake")}
            />
            <select
              value={days}
              onChange={(event) => setDays(Number(event.target.value))}
              className="input"
              aria-label={t("duel.days")}
            >
              {[5, 10, 20, 30].map((option) => (
                <option key={option} value={option}>
                  {option} {t("duel.daysUnit")}
                </option>
              ))}
            </select>
            <button onClick={placeDuel} className="btn btn-primary">
              <Scale size={15} />
              {t("duel.place")}
            </button>
          </div>
          {duelNotice ? (
            <p className="mt-3 text-xs text-brass">{duelNotice}</p>
          ) : null}
          {duels.length > 0 ? (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[560px] border-collapse">
                <thead>
                  <tr>
                    <th className="th">{t("duel.rival")}</th>
                    <th className="th">{t("duel.stake")}</th>
                    <th className="th">{t("duel.period")}</th>
                    <th className="th">{t("duel.status")}</th>
                    <th className="th">{t("duel.returns")}</th>
                  </tr>
                </thead>
                <tbody>
                  {duels.map((duel) => (
                    <tr key={duel.id} className="hover:bg-ink-700/40">
                      <td className="td font-semibold text-parch-100">{duel.rival}</td>
                      <td className="td">{money(duel.stake)}</td>
                      <td className="td text-parch-500">
                        {duel.start_day} - {duel.end_day}
                      </td>
                      <td className="td">
                        <span
                          className={`rounded-[3px] border px-1.5 py-0.5 text-[10px] font-bold ${
                            duel.status === "won"
                              ? "border-mint/40 bg-mint/10 text-mint"
                              : duel.status === "lost"
                                ? "border-risk/40 bg-risk/10 text-risk"
                                : "border-brass/40 bg-brass/10 text-brass"
                          }`}
                        >
                          {t(`duel.${duel.status}`)}
                        </span>
                      </td>
                      <td className="td text-parch-500">
                        {duel.player_return != null
                          ? `${duel.player_return}% vs ${duel.rival_return}%`
                          : "…"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      </section>

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
