const BASE = import.meta.env.VITE_API_BASE || "";
let language = localStorage.getItem("cms-lang") || "zh";
const REQUEST_TIMEOUT_MS = 20000;

function authHeaders() {
  const key = localStorage.getItem("cms_api_key");
  return key ? { "X-API-Key": key } : {};
}

export function setApiLanguage(lang) {
  language = lang;
}

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        "Accept-Language": language,
        ...authHeaders(),
        ...(options.headers || {}),
      },
      signal: controller.signal,
      ...options,
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error(
        language === "zh" ? "请求超时，请重试。" : "Request timed out. Please try again."
      );
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = body.detail || `Request failed (${response.status})`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  return body;
}

export const api = {
  getState: () => request("/api/state"),
  getStocks: (params = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, value]) => value !== undefined && value !== "")
    ).toString();
    return request(`/api/stocks${query ? `?${query}` : ""}`);
  },
  getStock: (ticker) => request(`/api/stocks/${encodeURIComponent(ticker)}`),
  getHistory: (ticker, limit = 252) =>
    request(`/api/stocks/${encodeURIComponent(ticker)}/history?limit=${limit}`),
  getIndexHistory: (limit = 510) => request(`/api/index/history?limit=${limit}`),
  getNews: (limit = 20) => request(`/api/news?limit=${limit}`),
  getTodayStory: () => request("/api/stories/today"),
  getRandomStory: () => request("/api/stories/random"),
  getStories: () => request("/api/stories"),
  getLegends: () => request("/api/legends"),
  getTimeline: () => request("/api/timeline"),
  getChronicle: () => request("/api/chronicle"),
  getChronicleBook: () => request("/api/chronicle/book"),
  getDailyQuest: () => request("/api/quests/daily"),
  getCommission: () => request("/api/quests/commission"),
  resolveCommission: (decisionId, optionKey) =>
    request(`/api/quests/commission/${decisionId}/resolve`, {
      method: "POST",
      body: JSON.stringify({ option_key: optionKey }),
    }),
  getStorylines: () => request("/api/storylines"),
  getReplay: () => request("/api/replay"),
  getBots: () => request("/api/bots"),
  createOrder: (ticker, kind, price, shares) =>
    request("/api/orders", {
      method: "POST",
      body: JSON.stringify({ ticker, kind, price, shares }),
    }),
  getOrders: () => request("/api/orders"),
  cancelOrder: (orderId) =>
    request(`/api/orders/${orderId}/cancel`, { method: "POST" }),
  createDuel: (rivalId, stake, days) =>
    request("/api/duels", {
      method: "POST",
      body: JSON.stringify({ rival_id: rivalId, stake, days }),
    }),
  getDuels: () => request("/api/duels"),
  resolveDecision: (decisionId, optionKey) =>
    request(`/api/decisions/${decisionId}/resolve`, {
      method: "POST",
      body: JSON.stringify({ option_key: optionKey }),
    }),
  eraBonus: (gradeKey, optionKey) =>
    request("/api/decisions/era-bonus", {
      method: "POST",
      body: JSON.stringify({ grade_key: gradeKey, option_key: optionKey }),
    }),
  createJudgment: (ticker, thesis) =>
    request("/api/judgments", {
      method: "POST",
      body: JSON.stringify({ ticker, thesis }),
    }),
  getJudgments: () => request("/api/judgments"),
  getPortfolio: () => request("/api/portfolio"),
  getAdvisorReport: () => request("/api/advisor/portfolio"),
  advisorChat: (message) =>
    request("/api/advisor/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  getAchievements: () => request("/api/achievements"),
  getLeaderboard: () => request("/api/leaderboard"),
  getPlayerActivity: (limit = 30) => request(`/api/players/activity?limit=${limit}`),
  getBot: (id, limit = 120) => request(`/api/bots/${id}?limit=${limit}`),
  getTransactions: (limit = 100) => request(`/api/transactions?limit=${limit}`),
  trade: (action, ticker, shares) =>
    request("/api/trades", {
      method: "POST",
      body: JSON.stringify({ action, ticker, shares }),
    }),
  advanceDay: (days = 1) =>
    request("/api/game/advance", {
      method: "POST",
      body: JSON.stringify({ days }),
    }),
  resetGame: () =>
    request("/api/game/reset", {
      method: "POST",
    }),
  register: (username, password) =>
    request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  login: (username, password) =>
    request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  me: () => request("/api/auth/me"),
};
