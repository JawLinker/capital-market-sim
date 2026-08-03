import {
  Archive,
  Badge,
  BookOpenText,
  CandlestickChart,
  FastForward,
  Globe,
  History,
  LayoutDashboard,
  ListChecks,
  LogOut,
  MessageCircleMore,
  Pause,
  Play,
  RotateCcw,
  Sparkles,
  Trophy,
  Volume2,
  VolumeX,
} from "lucide-react";
import { useEffect, useState } from "react";

import { useApp } from "../../store/AppContext.jsx";
import { eraForDate } from "../../utils/era.js";
import { CYCLE_META } from "../../utils/format.js";
import Avatar from "../Avatar.jsx";
import BlackSwanModal from "../story/BlackSwanModal.jsx";
import ChronicleModal from "../story/ChronicleModal.jsx";
import EraTransitionModal from "../story/EraTransitionModal.jsx";
import NewspaperModal from "../story/NewspaperModal.jsx";
import RetailStoryModal from "../story/RetailStoryModal.jsx";

const NAV_ITEMS = [
  { key: "dashboard", icon: LayoutDashboard },
  { key: "market", icon: CandlestickChart },
  { key: "portfolio", icon: BookOpenText },
  { key: "advisor", icon: Sparkles },
  { key: "achievements", icon: Trophy },
  { key: "archive", icon: Archive },
  { key: "quests", icon: ListChecks },
  { key: "replay", icon: History },
];

function Sidebar() {
  const { view, setView, t } = useApp();
  return (
    <aside className="flex w-16 shrink-0 flex-col border-r border-ink-600/70 bg-ink-950/80 lg:w-60">
      <div className="flex h-14 items-center gap-2.5 border-b border-ink-600/70 px-3 lg:px-4">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-[3px] border border-brass/50 bg-brass/15 text-brass">
          <CandlestickChart size={17} strokeWidth={2.2} />
        </div>
        <div className="hidden min-w-0 lg:block">
          <p className="truncate font-display text-sm font-bold text-parch-100">{t("app.brand")}</p>
          <p className="truncate text-[9px] font-semibold uppercase tracking-[0.18em] text-parch-600">
            {t("app.terminal")}
          </p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-2 lg:p-3">
        {NAV_ITEMS.map(({ key, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setView(key)}
            title={t(`nav.${key}`)}
            className={`flex w-full items-center gap-3 rounded-[3px] border px-2.5 py-2.5 text-sm font-medium transition-colors lg:px-3 ${
              view === key
                ? "border-risk/40 bg-risk/10 text-risk"
                : "border-transparent text-parch-500 hover:border-brass/30 hover:bg-ink-700/40 hover:text-parch-200"
            }`}
          >
            <Icon size={17} className="shrink-0" />
            <span className="hidden lg:inline">{t(`nav.${key}`)}</span>
          </button>
        ))}
      </nav>
      <div className="hidden border-t border-ink-600/70 p-4 lg:block">
        <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-parch-600">
          {t("app.wing")}
        </p>
        <p className="mt-1 text-[11px] leading-5 text-parch-500">{t("app.simulated")}</p>
      </div>
    </aside>
  );
}

function TopBar() {
  const {
    gameState,
    advanceDay,
    resetGame,
    busy,
    t,
    lang,
    setLang,
    authPlayer,
    logout,
    openStory,
    chronicle,
    muted,
    toggleMute,
    autoPlay,
    autoSpeed,
    toggleAutoPlay,
    setAutoSpeed,
  } = useApp();
  const [fastDays, setFastDays] = useState(30);
  const market = gameState?.market;
  const cycle = CYCLE_META[market?.market_cycle] || CYCLE_META.recovery;
  const era = eraForDate(market?.date, lang);
  const isHost = Boolean(authPlayer?.is_host);

  const confirmReset = () => {
    if (window.confirm(t("topbar.resetConfirm"))) {
      resetGame();
    }
  };

  return (
    <header className="flex h-14 shrink-0 items-center gap-3 overflow-x-auto border-b border-ink-600/70 bg-ink-900/90 px-4">
      <div className="flex shrink-0 items-center gap-3">
        <div className="min-w-0">
          <p className="truncate font-display text-sm font-bold text-parch-100">
            {market?.date ? `${era.label} · ${market.date}` : era.label}
          </p>
          <p className="whitespace-nowrap text-[10px] uppercase tracking-[0.14em] text-parch-600">
            {t("topbar.tradingDay", { day: market?.day || 0 })}
          </p>
        </div>
        <span
          className={`hidden rounded-[3px] border px-2 py-1 text-[11px] font-semibold sm:inline-flex ${cycle.className}`}
        >
          {t(`cycle.${market?.market_cycle}`)}
        </span>
      </div>
      <div className="flex items-center gap-2">
        {isHost ? (
          <>
            <div className="hidden items-center gap-1 rounded-[3px] border border-ink-600/70 bg-ink-800 p-1 md:flex">
              <select
                value={fastDays}
                onChange={(event) => setFastDays(Number(event.target.value))}
                className="bg-transparent px-1 py-0.5 text-xs font-semibold tabular text-parch-300 outline-none"
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
                className="rounded px-2 py-1 text-xs font-semibold text-brass transition-colors hover:bg-brass/10"
                title={t("topbar.fastForward")}
              >
                <FastForward size={13} />
                <span className="hidden xl:inline">{t("topbar.fastForward")}</span>
              </button>
              <span className="mx-0.5 h-4 w-px bg-ink-600" />
              {[1, 2, 4].map((speed) => (
                <button
                  key={speed}
                  onClick={() => setAutoSpeed(speed)}
                  className={`rounded px-1.5 py-0.5 text-[11px] font-semibold tabular transition-colors ${
                    autoSpeed === speed
                      ? "bg-brass/20 text-brass"
                      : "text-parch-600 hover:text-parch-300"
                  }`}
                  title={t("topbar.autoSpeed")}
                >
                  {speed}x
                </button>
              ))}
              <button
                onClick={toggleAutoPlay}
                className={`rounded px-2 py-1 transition-colors ${
                  autoPlay
                    ? "bg-risk/15 text-risk"
                    : "text-brass hover:bg-brass/10"
                }`}
                title={autoPlay ? t("topbar.autoStop") : t("topbar.auto")}
              >
                {autoPlay ? <Pause size={13} /> : <Play size={13} />}
              </button>
            </div>
          </>
        ) : null}
        <button
          onClick={openStory}
          className="btn btn-ghost px-2.5"
          title={t("story.button")}
        >
          <MessageCircleMore size={16} />
          <span className="hidden xl:inline">{t("story.button")}</span>
        </button>
        <button
          onClick={() => setLang(lang === "en" ? "zh" : "en")}
          className="btn btn-ghost px-2.5"
          title={lang === "en" ? "切换中文" : "Switch to English"}
        >
          <Globe size={16} />
          <span className="hidden xl:inline">{lang === "en" ? "中文" : "EN"}</span>
        </button>
        <button
          onClick={toggleMute}
          className="btn btn-ghost px-2.5"
          title={muted ? t("topbar.soundOff") : t("topbar.soundOn")}
        >
          {muted ? <VolumeX size={16} /> : <Volume2 size={16} />}
        </button>
        {authPlayer ? (
          <div className="hidden items-center gap-2 rounded-[3px] border border-ink-600/70 bg-ink-800/70 px-2.5 py-1.5 sm:flex">
            <Avatar seed={authPlayer.username || authPlayer.name} size={22} />
            <span className="max-w-28 truncate text-xs font-semibold text-parch-200">
              {authPlayer.username}
            </span>
            {chronicle?.title ? (
              <Badge
                className="hidden rounded bg-gold/15 px-1.5 py-0.5 text-[10px] font-bold text-gold lg:inline-flex"
                title={chronicle.title.label}
              >
                {chronicle.title.label}
              </Badge>
            ) : null}
            {isHost ? (
              <Badge className="rounded bg-brass/15 px-1.5 py-0.5 text-[10px] font-bold text-brass">
                {t("topbar.host")}
              </Badge>
            ) : null}
            <button
              onClick={logout}
              className="rounded p-0.5 text-parch-500 transition-colors hover:bg-ink-700 hover:text-parch-200"
              title={t("topbar.logout")}
            >
              <LogOut size={14} />
            </button>
          </div>
        ) : null}
        {isHost ? (
          <button
            onClick={confirmReset}
            disabled={busy}
            className="btn btn-ghost px-2.5"
            title={t("topbar.reset")}
          >
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
  const {
    loading,
    t,
    storyOpen,
    chronicleOpen,
    eraTransition,
    blackSwan,
    newspaper,
    authPlayer,
    setView,
    advanceDay,
    toggleMute,
    closeStory,
    closeChronicle,
    closeEraTransition,
    closeBlackSwan,
  } = useApp();
  const isHost = Boolean(authPlayer?.is_host);

  useEffect(() => {
    const onKeyDown = (event) => {
      const target = event.target;
      if (
        target &&
        ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)
      ) {
        return;
      }
      if (event.code === "Space") {
        event.preventDefault();
        if (isHost) advanceDay();
      } else if (event.key === "Escape") {
        closeStory();
        closeChronicle();
        closeEraTransition();
        closeBlackSwan();
      } else {
        const key = event.key.toLowerCase();
        if (key === "m") toggleMute();
        else if (key === "b") setView("market");
        else if (key === "p") setView("portfolio");
        else if (key === "q") setView("quests");
        else if (key === "r") setView("replay");
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [
    isHost,
    advanceDay,
    toggleMute,
    setView,
    closeStory,
    closeChronicle,
    closeEraTransition,
    closeBlackSwan,
  ]);
  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-9 w-9 animate-pulse rounded-[3px] border border-brass/40 bg-brass/15" />
          <p className="text-sm text-parch-400">{t("loading.init")}</p>
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
      {storyOpen ? <RetailStoryModal /> : null}
      {chronicleOpen ? <ChronicleModal /> : null}
      {eraTransition ? <EraTransitionModal /> : null}
      {blackSwan ? <BlackSwanModal /> : null}
      {newspaper ? <NewspaperModal /> : null}
    </div>
  );
}
