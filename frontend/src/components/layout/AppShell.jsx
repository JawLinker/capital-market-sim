import {
  Badge,
  Briefcase,
  CandlestickChart,
  FastForward,
  Globe,
  LayoutDashboard,
  LogOut,
  Play,
  RotateCcw,
  Sparkles,
  Trophy,
} from "lucide-react";
import { useState } from "react";

import { useApp } from "../../store/AppContext.jsx";
import { CYCLE_META, money, percent, toneClass } from "../../utils/format.js";

const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { key: "market", label: "Market", icon: CandlestickChart },
  { key: "portfolio", label: "Portfolio", icon: Briefcase },
  { key: "advisor", label: "Advisor", icon: Sparkles },
  { key: "achievements", label: "Achievements", icon: Trophy },
];

function Sidebar() {
  const { view, setView, t } = useApp();
  return (
    <aside className="flex w-16 shrink-0 flex-col border-r border-ink-600/70 bg-ink-900 lg:w-56">
      <div className="flex h-14 items-center gap-2.5 border-b border-ink-600/70 px-3 lg:px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-mint/80 to-sky/70 text-ink-950">
          <CandlestickChart size={18} strokeWidth={2.4} />
        </div>
        <div className="hidden min-w-0 lg:block">
          <p className="truncate text-sm font-bold text-slate-100">{t("app.brand")}</p>
          <p className="text-[10px] font-medium uppercase tracking-wide text-slate-500">
            {t("app.terminal")}
          </p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-2 lg:p-3">
        {NAV_ITEMS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setView(key)}
            title={t(`nav.${key}`)}
            className={`flex w-full items-center gap-3 rounded-md border px-2.5 py-2.5 text-sm font-medium transition-colors lg:px-3 ${
              view === key
                ? "border-mint/25 bg-mint/10 text-mint"
                : "border-transparent text-slate-400 hover:bg-ink-800 hover:text-slate-100"
            }`}
          >
            <Icon size={18} className="shrink-0" />
            <span className="hidden lg:inline">{t(`nav.${key}`)}</span>
          </button>
        ))}
      </nav>
      <div className="hidden border-t border-ink-600/70 p-4 lg:block">
        <p className="text-[11px] leading-5 text-slate-500">
          {t("app.simulated")}
        </p>
      </div>
    </aside>
  );
}

function TopBar() {
  const { gameState, advanceDay, resetGame, busy, t, lang, setLang, authPlayer, logout } = useApp();
  const [fastDays, setFastDays] = useState(30);
  const market = gameState?.market;
  const cycle = CYCLE_META[market?.market_cycle] || CYCLE_META.recovery;
  const sentimentPct = market ? Math.round(((market.sentiment - 0.55) / 0.95) * 100) : 0;
  const benchmarkChange = market?.benchmark_change_pct || 0;
  const isHost = Boolean(authPlayer?.is_host);

  const confirmReset = () => {
    if (window.confirm(t("topbar.resetConfirm"))) {
      resetGame();
    }
  };

  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-3 border-b border-ink-600/70 bg-ink-850 px-4">
      <div className="flex min-w-0 items-center gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-slate-100">
            {market?.date || "—"}
          </p>
          <p className="text-[11px] text-slate-500">{t("topbar.tradingDay", { day: market?.day || 0 })}</p>
        </div>
        <span className={`hidden rounded-md border px-2 py-1 text-[11px] font-semibold sm:inline-flex ${cycle.className}`}>
          {t(`cycle.${market?.market_cycle}`)}
        </span>
        <div className="hidden items-center gap-2 md:flex">
          <div className="w-24">
            <div className="mb-1 flex justify-between text-[10px] text-slate-500">
              <span>{t("topbar.sentiment")}</span>
              <span className="tabular text-slate-300">{market?.sentiment?.toFixed(2)}</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-ink-600">
              <div
                className="h-full rounded-full bg-gradient-to-r from-risk via-gold to-mint"
                style={{ width: `${sentimentPct}%` }}
              />
            </div>
          </div>
          <div className="hidden border-l border-ink-600 pl-3 lg:block">
            <p className="text-[10px] uppercase tracking-wide text-slate-500">{t("topbar.benchmark")}</p>
            <p className="text-sm font-semibold tabular text-slate-100">
              {market ? money(market.benchmark_value, 2) : "—"}
              <span className={`ml-1.5 text-xs ${toneClass(benchmarkChange)}`}>
                {percent(benchmarkChange)}
              </span>
            </p>
          </div>
          <div className="hidden border-l border-ink-600 pl-3 xl:block">
            <p className="text-[10px] uppercase tracking-wide text-slate-500">{t("topbar.rate")}</p>
            <p className="text-sm font-semibold tabular text-slate-100">
              {market?.policy_rate?.toFixed(2)}%
            </p>
          </div>
          <div className="hidden border-l border-ink-600 pl-3 xl:block">
            <p className="text-[10px] uppercase tracking-wide text-slate-500">{t("topbar.index")}</p>
            <p className="text-sm font-semibold tabular text-slate-100">
              {market?.shanghai_index?.toFixed(2)}
              <span className={`ml-1.5 text-xs ${toneClass(market?.shanghai_change_pct || 0)}`}>
                {percent(market?.shanghai_change_pct || 0)}
              </span>
            </p>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {isHost ? (
          <>
            <div className="hidden items-center gap-1 rounded-md border border-ink-600/70 bg-ink-800 p-1 md:flex">
          <select
            value={fastDays}
            onChange={(event) => setFastDays(Number(event.target.value))}
            className="bg-transparent px-1 py-0.5 text-xs font-semibold tabular text-slate-200 outline-none"
            aria-label={t("topbar.fastForward")}
          >
            {[5, 10, 30, 90, 250].map((days) => (
              <option key={days} value={days} className="bg-ink-800">
                {days}
              </option>
            ))}
          </select>
          <button
            onClick={() => advanceDay(fastDays)}
            disabled={busy}
            className="rounded px-2 py-1 text-xs font-semibold text-sky transition-colors hover:bg-sky/10"
            title={t("topbar.fastForward")}
          >
            <FastForward size={13} />
            <span className="hidden lg:inline">{t("topbar.fastForward")}</span>
          </button>
            </div>
          </>
        ) : null}
        <button
          onClick={() => setLang(lang === "en" ? "zh" : "en")}
          className="btn btn-ghost px-2.5"
          title={lang === "en" ? "切换到中文" : "Switch to English"}
        >
          <Globe size={16} />
          <span className="hidden sm:inline">{lang === "en" ? "中文" : "EN"}</span>
        </button>
        {authPlayer ? (
          <div className="hidden items-center gap-2 rounded-md border border-ink-600/70 bg-ink-800/70 px-2.5 py-1.5 sm:flex">
            <span className="max-w-28 truncate text-xs font-semibold text-slate-200">
              {authPlayer.username}
            </span>
            {isHost ? (
              <Badge className="rounded bg-mint/15 px-1.5 py-0.5 text-[10px] font-bold text-mint">
                {t("topbar.host")}
              </Badge>
            ) : null}
            <button
              onClick={logout}
              className="rounded p-0.5 text-slate-500 transition-colors hover:bg-ink-700 hover:text-slate-200"
              title={t("topbar.logout")}
            >
              <LogOut size={14} />
            </button>
          </div>
        ) : null}
        {isHost ? (
          <button onClick={confirmReset} disabled={busy} className="btn btn-ghost px-2.5" title={t("topbar.reset")}>
            <RotateCcw size={16} />
            <span className="hidden sm:inline">{t("topbar.reset")}</span>
          </button>
        ) : null}
        {isHost ? (
          <button
            onClick={() => advanceDay()}
            disabled={busy}
            className="btn btn-primary px-3"
            title={t("topbar.advanceTitle")}
          >
            <Play size={16} fill="currentColor" />
            {busy ? t("topbar.running") : t("topbar.advance")}
          </button>
        ) : null}
      </div>
    </header>
  );
}

export default function AppShell({ children }) {
  const { loading, t } = useApp();
  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-9 w-9 animate-pulse rounded-md bg-gradient-to-br from-mint/70 to-sky/60" />
          <p className="text-sm text-slate-400">{t("loading.init")}</p>
        </div>
      </div>
    );
  }
  return (
    <div className="flex h-full min-h-0">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar />
        <main className="min-h-0 flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
