import { useState } from "react";
import { Bot, Send, Sparkles } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";
import { money, percent } from "../../utils/format.js";
import { Badge, EmptyState, ProgressBar, ScoreRing, SectionTitle } from "../ui.jsx";

const DIMENSION_LABELS = {
  valuation: "advisor.dimValuation",
  momentum: "advisor.dimMomentum",
  risk: "advisor.dimRisk",
  diversification: "advisor.dimDiversification",
};

const SUGGESTIONS = [
  "advisor.suggest1",
  "advisor.suggest2",
  "advisor.suggest3",
  "advisor.suggest4",
];

function DimensionCard({ name, data }) {
  const { t } = useApp();
  const score = data?.score || 0;
  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-parch-600">{name}</p>
          <p className="mt-1 text-sm font-semibold text-parch-100">{data?.label || "—"}</p>
        </div>
        <span className="text-xl font-bold tabular text-parch-100">{score}</span>
      </div>
      <ProgressBar value={score / 100} className="mt-3" color={score >= 70 ? "#22c55e" : score >= 45 ? "#f59e0b" : "#ef4444"} />
      <p className="mt-3 text-xs leading-5 text-parch-500">{data?.detail || t("advisor.dimEmpty")}</p>
    </div>
  );
}

export default function AdvisorView() {
  const { advisor, sendChat, chatMessages, busy, t } = useApp();
  const [message, setMessage] = useState("");
  const summary = advisor?.summary;

  const submit = (text = message) => {
    if (!text.trim()) return;
    sendChat(text);
    setMessage("");
  };

  return (
    <div className="grid grid-cols-1 gap-4 p-4 xl:grid-cols-3 lg:p-5">
      <div className="space-y-4 xl:col-span-2">
        <section className="panel flex flex-col gap-5 p-5 sm:flex-row sm:items-center">
          <div className="flex items-center gap-4">
            <ScoreRing score={advisor?.health_score || 0} label="Health" size={104} />
            <div>
              <p className="flex items-center gap-2 text-sm font-semibold text-parch-100">
                <Sparkles size={15} className="text-violet-400" />
                {t("advisor.healthReport")}
              </p>
              <p className="mt-1 max-w-md text-xs leading-5 text-parch-500">
                {t("advisor.healthDetail")}
              </p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3 sm:ml-auto">
            {[
              [t("advisor.value"), money(summary?.value)],
              [t("advisor.cash"), money(summary?.cash)],
              [t("advisor.return"), percent(summary?.total_return_pct)],
            ].map(([label, value]) => (
              <div key={label} className="rounded-md border border-ink-600/70 bg-ink-750 px-3 py-2 text-center">
                <p className="text-[10px] uppercase tracking-wide text-parch-600">{label}</p>
                <p className="mt-0.5 text-sm font-semibold tabular text-parch-100">{value}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {Object.entries(DIMENSION_LABELS).map(([key, label]) => (
            <DimensionCard key={key} name={t(label)} data={advisor?.dimensions?.[key]} />
          ))}
        </section>

        <section className="panel overflow-hidden">
          <SectionTitle
            title={t("advisor.analysisTitle")}
            detail={t("advisor.analysisDetail")}
          />
          {advisor?.holdings?.length ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] border-collapse">
                <thead>
                  <tr>
                    <th className="th">{t("advisor.colPosition")}</th>
                    <th className="th">{t("advisor.colWeight")}</th>
                    <th className="th">{t("advisor.colValuation")}</th>
                    <th className="th">{t("advisor.colMomentum")}</th>
                    <th className="th">{t("advisor.colRisk")}</th>
                    <th className="th">{t("advisor.colComposite")}</th>
                  </tr>
                </thead>
                <tbody>
                  {advisor.holdings.map((item) => (
                    <tr key={item.ticker} className="hover:bg-ink-700/40">
                      <td className="td">
                        <span className="block font-semibold text-parch-100">{item.name}</span>
                        <span className="block text-[11px] text-parch-600">
                          {t(`industry.${item.industry}`)}
                        </span>
                      </td>
                      <td className="td text-parch-300">{item.weight.toFixed(1)}%</td>
                      {["valuation", "momentum", "risk"].map((key) => (
                        <td key={key} className="td">
                          <div className="flex items-center gap-2">
                            <span className="w-6 font-semibold tabular text-parch-200">
                              {item.dimensions[key].score}
                            </span>
                            <ProgressBar
                              value={item.dimensions[key].score / 100}
                              className="w-16"
                              color={
                                item.dimensions[key].score >= 70
                                  ? "#22c55e"
                                  : item.dimensions[key].score >= 45
                                    ? "#f59e0b"
                                    : "#ef4444"
                              }
                            />
                          </div>
                        </td>
                      ))}
                      <td className="td">
                        <Badge
                          className={
                            item.composite_score >= 70
                              ? "border-mint/40 bg-mint/10 text-mint"
                              : item.composite_score >= 45
                                ? "border-gold/40 bg-gold/10 text-gold"
                                : "border-risk/40 bg-risk/10 text-risk"
                          }
                        >
                          {item.composite_score}/100
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState
              title={t("advisor.analysisEmpty")}
              detail={t("advisor.analysisEmptyDetail")}
            />
          )}
        </section>

        <section className="panel p-5">
          <h3 className="text-sm font-semibold text-parch-100">{t("advisor.howToRead")}</h3>
          <ul className="mt-3 grid grid-cols-1 gap-3 text-xs leading-5 text-parch-500 md:grid-cols-2">
            {(advisor?.education || []).map((item, index) => (
              <li key={index} className="rounded-md border border-ink-600/60 bg-ink-750/60 px-3 py-2.5">
                {item}
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="panel flex h-[560px] min-h-0 flex-col xl:sticky xl:top-5 xl:h-[calc(100vh-104px)]">
        <div className="panel-header">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-parch-100">
            <Bot size={16} className="text-violet-400" /> {t("advisor.aiTitle")}
          </h3>
          <Badge className="border-violet-400/30 bg-violet-400/10 text-violet-300">{t("advisor.localEngine")}</Badge>
        </div>
        <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
          <div className="rounded-md border border-ink-600/60 bg-ink-750/70 px-3 py-2.5 text-xs leading-5 text-parch-300">
            {t("advisor.intro")}
          </div>
          {chatMessages.map((chat, index) => (
            <div
              key={index}
              className={`max-w-[92%] rounded-md border px-3 py-2.5 text-xs leading-5 ${
                chat.role === "user"
                  ? "ml-auto border-sky/30 bg-sky/10 text-sky-100"
                  : "border-ink-600/60 bg-ink-750 text-parch-300"
              }`}
            >
              {chat.content}
            </div>
          ))}
        </div>
        <div className="border-t border-ink-600/70 p-3">
          <div className="mb-2 flex flex-wrap gap-1.5">
            {SUGGESTIONS.map((suggestionKey) => (
              <button
                key={suggestionKey}
                onClick={() => submit(t(suggestionKey))}
                className="rounded-full border border-ink-500/50 px-2.5 py-1 text-[11px] text-parch-500 transition-colors hover:border-sky/40 hover:text-sky"
              >
                {t(suggestionKey)}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && submit()}
              placeholder={t("advisor.placeholder")}
              className="input"
            />
            <button
              onClick={() => submit()}
              disabled={busy || !message.trim()}
              className="btn btn-primary px-3"
              aria-label={t("advisor.placeholder")}
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
