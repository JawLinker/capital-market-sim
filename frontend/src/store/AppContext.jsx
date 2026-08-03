import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { api } from "../api/client.js";
import { setApiLanguage } from "../api/client.js";
import { translations } from "../i18n/translations.js";

const AppContext = createContext(null);

function Toast({ id, kind, title, detail, onClose }) {
  const styles =
    kind === "success"
      ? "border-mint/40 text-mint"
      : kind === "error"
        ? "border-risk/40 text-risk"
        : "border-sky/40 text-sky";
  return (
    <div className={`panel border-l-4 ${styles} flex w-80 items-start gap-3 px-4 py-3`}>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold">{title}</p>
        {detail ? <p className="mt-0.5 text-xs text-parch-500">{detail}</p> : null}
      </div>
      <button
        onClick={onClose}
        className="rounded px-1 text-parch-600 hover:text-parch-200"
        aria-label="Dismiss"
      >
        ×
      </button>
    </div>
  );
}

export function AppProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem("cms-lang") || "zh");
  const [authPlayer, setAuthPlayer] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [view, setView] = useState("dashboard");
  const [gameState, setGameState] = useState(null);
  const [stocks, setStocks] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("BCSC");
  const [quote, setQuote] = useState(null);
  const [history, setHistory] = useState([]);
  const [indexHistory, setIndexHistory] = useState([]);
  const [news, setNews] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [playerActivity, setPlayerActivity] = useState([]);
  const [advisor, setAdvisor] = useState(null);
  const [achievements, setAchievements] = useState(null);
  const [leaderboard, setLeaderboard] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [story, setStory] = useState(null);
  const [storyOpen, setStoryOpen] = useState(false);
  const [chronicle, setChronicle] = useState(null);
  const [chronicleOpen, setChronicleOpen] = useState(false);
  const [eraTransition, setEraTransition] = useState(null);
  const [blackSwan, setBlackSwan] = useState(null);
  const toastId = useRef(0);
  const achievementsRef = useRef(null);
  const didInit = useRef(false);
  const chronicleBeatRef = useRef(null);
  const prevYearRef = useRef(null);

  useEffect(() => {
    setApiLanguage(lang);
  }, [lang]);

  useEffect(() => {
    achievementsRef.current = achievements;
  }, [achievements]);

  useEffect(() => {
    const token = localStorage.getItem("cms_api_key");
    if (!token) {
      setAuthChecked(true);
      return;
    }
    api
      .me()
      .then((player) => setAuthPlayer(player))
      .catch(() => localStorage.removeItem("cms_api_key"))
      .finally(() => setAuthChecked(true));
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("cms_api_key");
    setAuthPlayer(null);
    setChatMessages([]);
  }, []);

  useEffect(() => {
    if (!authPlayer) return;
    const timer = window.setInterval(async () => {
      try {
        const data = await api.getPlayerActivity(30);
        setPlayerActivity(data.trades);
      } catch {
        // Keep the last known activity; a failed refresh is non-critical.
      }
    }, 15000);
    return () => window.clearInterval(timer);
  }, [authPlayer]);

  const t = useCallback(
    (key, params) => {
      let text = translations[lang]?.[key] ?? translations.en[key] ?? key;
      if (params) {
        Object.entries(params).forEach(([name, value]) => {
          text = text.split(`{${name}}`).join(String(value));
        });
      }
      return text;
    },
    [lang]
  );

  const addToast = useCallback((kind, title, detail) => {
    const id = ++toastId.current;
    setToasts((current) => [...current, { id, kind, title, detail }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    }, 5200);
  }, []);

  const dismissToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const loadStory = useCallback(async (random = false) => {
    try {
      const next = random ? await api.getRandomStory() : await api.getTodayStory();
      setStory(next);
      return next;
    } catch {
      return null;
    }
  }, []);

  const openStory = useCallback(async () => {
    const current = story || (await loadStory(false));
    if (current) setStoryOpen(true);
  }, [story, loadStory]);

  const nextStory = useCallback(async () => {
    const next = await loadStory(true);
    if (next) setStoryOpen(true);
  }, [loadStory]);

  const closeStory = useCallback(() => setStoryOpen(false), []);

  const announceUnlocks = useCallback(
    (unlocked) => {
      if (!unlocked || unlocked.length === 0) return;
      const titles = {};
      (achievementsRef.current?.achievements || []).forEach((item) => {
        titles[item.code] = item.title;
      });
      const labels = unlocked.map((code) => titles[code] || code);
      addToast(
        "achievement",
        t("toast.achievementTitle", { codes: labels.join(", ") }),
        t("toast.achievementDetail")
      );
    },
    [addToast, t]
  );

  const loadMarket = useCallback(async (ticker = selectedTicker) => {
    const [stockList, stockQuote, stockHistory, newsFeed] = await Promise.all([
      api.getStocks(),
      api.getStock(ticker),
      api.getHistory(ticker, 252),
      api.getNews(20),
    ]);
    setStocks(stockList.stocks);
    setQuote(stockQuote);
    setHistory(stockHistory.series);
    setNews(newsFeed.news);
  }, [selectedTicker]);

  const refreshAll = useCallback(async () => {
    try {
      const [state, portfolioData, leaderboardData, achievementsData, advisorData, transactionData, activityData, chronicleData] =
        await Promise.all([
          api.getState(),
          api.getPortfolio(),
          api.getLeaderboard(),
          api.getAchievements(),
          api.getAdvisorReport(),
          api.getTransactions(500),
          api.getPlayerActivity(30),
          api.getChronicle(),
        ]);
      setGameState(state);
      const currentYear = String(state?.market?.date || "").slice(0, 4);
      if (prevYearRef.current && currentYear && currentYear !== prevYearRef.current) {
        setEraTransition({
          year: currentYear,
          grade: chronicleData?.grade || null,
        });
      }
      prevYearRef.current = currentYear;
      setPortfolio(portfolioData);
      setLeaderboard(leaderboardData);
      setAchievements(achievementsData);
      setAdvisor(advisorData);
      setTransactions(transactionData.transactions);
      setPlayerActivity(activityData.trades);
      setChronicle(chronicleData);
      const prevBeat = chronicleBeatRef.current;
      const nextBeat = chronicleData?.current_beat || null;
      if (prevBeat && nextBeat && prevBeat !== nextBeat) {
        setChronicleOpen(true);
      }
      chronicleBeatRef.current = nextBeat;
    } catch (error) {
      addToast("error", t("toast.failedLoad"), error.message);
    }
  }, [addToast, t]);

  const closeChronicle = useCallback(() => setChronicleOpen(false), []);
  const closeEraTransition = useCallback(() => setEraTransition(null), []);
  const closeBlackSwan = useCallback(() => setBlackSwan(null), []);

  const login = useCallback(
    async (username, password) => {
      const player = await api.login(username, password);
      localStorage.setItem("cms_api_key", player.api_key);
      setAuthPlayer(player);
      await Promise.all([refreshAll(), loadMarket()]);
      return player;
    },
    [refreshAll, loadMarket]
  );

  const register = useCallback(
    async (username, password) => {
      const player = await api.register(username, password);
      localStorage.setItem("cms_api_key", player.api_key);
      setAuthPlayer(player);
      await Promise.all([refreshAll(), loadMarket()]);
      return player;
    },
    [refreshAll, loadMarket]
  );

  const initialLoad = useCallback(async () => {
    setLoading(true);
    try {
      const [indexData] = await Promise.all([
        api.getIndexHistory(510),
        refreshAll(),
        loadMarket(),
      ]);
      setIndexHistory(indexData.series);
    } catch (error) {
      addToast("error", t("toast.connectionFailed"), error.message);
    } finally {
      setLoading(false);
    }
  }, [refreshAll, loadMarket, addToast, t]);

  useEffect(() => {
    if (didInit.current) return;
    didInit.current = true;
    initialLoad();
  }, [initialLoad]);

  const selectTicker = useCallback(async (ticker) => {
    setSelectedTicker(ticker);
    setView("market");
    try {
      const [stockQuote, stockHistory] = await Promise.all([
        api.getStock(ticker),
        api.getHistory(ticker, 252),
      ]);
      setQuote(stockQuote);
      setHistory(stockHistory.series);
    } catch (error) {
      addToast("error", t("toast.couldNotLoadStock"), error.message);
    }
  }, [addToast, t]);

  const changeLanguage = useCallback(
    (nextLang) => {
      setLang(nextLang);
      localStorage.setItem("cms-lang", nextLang);
      setApiLanguage(nextLang);
      refreshAll();
      loadMarket();
    },
    [refreshAll, loadMarket]
  );

  const advanceDay = useCallback(async (days = 1) => {
    if (busy) return;
    const count = Number.isFinite(days) ? Math.max(1, Math.min(250, Math.round(days))) : 1;
    setBusy(true);
    try {
      const result = await api.advanceDay(count);
      if (result.black_swan) {
        setBlackSwan(result.black_swan);
      }
      addToast("success", t("toast.advanced", { days: result.days_advanced }));
      announceUnlocks(result.unlocked_achievements);
      await Promise.all([refreshAll(), loadMarket()]);
      const todayStory = await loadStory(false);
      if (todayStory && result.days_advanced === 1) {
        setStoryOpen(true);
      }
    } catch (error) {
      addToast("error", t("toast.couldNotAdvance"), error.message);
    } finally {
      setBusy(false);
    }
  }, [busy, refreshAll, loadMarket, announceUnlocks, loadStory, addToast, t]);

  const executeTrade = useCallback(
    async (action, ticker, shares, displayName) => {
      setBusy(true);
      try {
        const result = await api.trade(action, ticker, shares);
        const verb = t(action === "buy" ? "toast.bought" : "toast.sold");
        addToast(
          "success",
          verb
            .replace("{shares}", String(shares))
            .replace("{ticker}", displayName || ticker),
          t("toast.feeCash", {
            fee: result.trade.fee.toFixed(2),
            cash: result.portfolio.cash.toFixed(2),
          })
        );
        announceUnlocks(result.unlocked_achievements);
        await Promise.all([
          refreshAll(),
          api.getStock(ticker).then(setQuote),
          api.getTransactions(100).then(() => {}),
        ]);
      } catch (error) {
        addToast("error", t("toast.orderRejected"), error.message);
      } finally {
        setBusy(false);
      }
    },
    [refreshAll, addToast, announceUnlocks, t]
  );

  const resetGame = useCallback(async () => {
    setBusy(true);
    try {
      await api.resetGame();
      setChatMessages([]);
      addToast("success", t("toast.resetTitle"), t("toast.resetDetail"));
      await Promise.all([refreshAll(), loadMarket()]);
    } catch (error) {
      addToast("error", t("toast.resetFailed"), error.message);
    } finally {
      setBusy(false);
    }
  }, [refreshAll, loadMarket, addToast, t]);

  const sendChat = useCallback(
    async (message) => {
      const trimmed = message.trim();
      if (!trimmed || busy) return;
      setChatMessages((current) => [...current, { role: "user", content: trimmed }]);
      setBusy(true);
      try {
        const response = await api.advisorChat(trimmed);
        setChatMessages((current) => [
          ...current,
          { role: "advisor", content: response.reply },
        ]);
      } catch (error) {
        addToast("error", t("toast.advisorUnavailable"), error.message);
      } finally {
        setBusy(false);
      }
    },
    [busy, addToast, t]
  );

  const value = useMemo(
    () => ({
      view,
      setView,
      gameState,
      stocks,
      quote,
      history,
      indexHistory,
      news,
      portfolio,
      transactions,
      playerActivity,
      advisor,
      achievements,
      leaderboard,
      chatMessages,
      loading,
      busy,
      lang,
      story,
      storyOpen,
      chronicle,
      chronicleOpen,
      closeChronicle,
      eraTransition,
      closeEraTransition,
      blackSwan,
      closeBlackSwan,
      openStory,
      nextStory,
      closeStory,
      authPlayer,
      authChecked,
      login,
      register,
      logout,
      setLang: changeLanguage,
      t,
      selectedTicker,
      selectTicker,
      advanceDay,
      executeTrade,
      resetGame,
      sendChat,
      refreshAll,
    }),
    [
      view,
      gameState,
      stocks,
      quote,
      history,
      indexHistory,
      news,
      portfolio,
      transactions,
      playerActivity,
      advisor,
      achievements,
      leaderboard,
      chatMessages,
      loading,
      busy,
      lang,
      story,
      storyOpen,
      chronicle,
      chronicleOpen,
      closeChronicle,
      eraTransition,
      closeEraTransition,
      blackSwan,
      closeBlackSwan,
      openStory,
      nextStory,
      closeStory,
      authPlayer,
      authChecked,
      login,
      register,
      logout,
      t,
      selectedTicker,
      changeLanguage,
      selectTicker,
      advanceDay,
      executeTrade,
      resetGame,
      sendChat,
      refreshAll,
    ]
  );

  return (
    <AppContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-80 flex-col gap-2">
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <Toast {...toast} onClose={() => dismissToast(toast.id)} />
          </div>
        ))}
      </div>
    </AppContext.Provider>
  );
}

export function useApp() {
  return useContext(AppContext);
}
