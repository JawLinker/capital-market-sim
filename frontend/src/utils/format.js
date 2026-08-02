export function money(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency: "CNY",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

export function compactMoney(value) {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency: "CNY",
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

export function compactNumber(value) {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

export function percent(value, digits = 2, signed = true) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const sign = signed && value > 0 ? "+" : "";
  return `${sign}${value.toFixed(digits)}%`;
}

export function toneClass(value) {
  if (value > 0) return "text-mint";
  if (value < 0) return "text-risk";
  return "text-slate-400";
}

export const CYCLE_META = {
  bull: { label: "Bull Market", className: "bg-mint/15 text-mint border-mint/30", icon: "trending-up" },
  recovery: { label: "Recovery", className: "bg-sky/15 text-sky border-sky/30", icon: "sprout" },
  bear: { label: "Bear Market", className: "bg-risk/15 text-risk border-risk/30", icon: "trending-down" },
  recession: { label: "Recession", className: "bg-amber-500/15 text-amber-400 border-amber-500/30", icon: "cloud" },
};

export const INDUSTRY_META = {
  technology: { label: "Technology", color: "#38bdf8" },
  healthcare: { label: "Healthcare", color: "#34d399" },
  energy: { label: "Energy", color: "#fbbf24" },
  finance: { label: "Finance", color: "#a78bfa" },
  consumer: { label: "Consumer", color: "#fb7185" },
};

export function industryColor(industry) {
  return INDUSTRY_META[industry]?.color || "#94a3b8";
}
