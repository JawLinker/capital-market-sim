import { compactNumber, money, percent, toneClass } from "../utils/format.js";

export function StatCard({ label, value, sub, tone = "default", icon }) {
  const valueClass =
    tone === "positive"
      ? "text-mint"
      : tone === "negative"
        ? "text-risk"
        : "text-parch-100";
  return (
    <div className="panel relative flex min-w-0 items-center justify-between gap-3 overflow-hidden px-4 py-3.5">
      <span className="absolute left-0 top-0 h-full w-0.5 bg-gradient-to-b from-brass/70 to-transparent" />
      <div className="min-w-0">
        <p className="truncate text-[11px] font-semibold uppercase tracking-[0.12em] text-parch-500">
          {label}
        </p>
        <p
          key={String(value)}
          className={`tick-flash mt-1 truncate text-xl font-semibold tabular ${valueClass}`}
        >
          {value}
        </p>
        {sub ? <p className="mt-0.5 truncate text-xs text-parch-500">{sub}</p> : null}
      </div>
      {icon ? (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[3px] border border-brass/40 bg-ink-700/60 text-brass">
          {icon}
        </div>
      ) : null}
    </div>
  );
}

export function Badge({ children, className = "" }) {
  return (
    <span
      className={`inline-flex items-center rounded-[3px] border px-1.5 py-0.5 text-[11px] font-medium ${className}`}
    >
      {children}
    </span>
  );
}

export function Change({ value, suffix = "%", className = "" }) {
  if (value === null || value === undefined || Number.isNaN(value)) return <span>—</span>;
  return (
    <span className={`tabular ${toneClass(value)} ${className}`}>
      {value > 0 ? "+" : ""}
      {value.toFixed(2)}
      {suffix}
    </span>
  );
}

export function ScoreRing({ score, size = 92, label }) {
  const radius = (size - 10) / 2;
  const circumference = 2 * Math.PI * radius;
  const color = score >= 70 ? "#7ba05b" : score >= 45 ? "#c9a24b" : "#c05a45";
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(176, 141, 87, 0.25)"
          strokeWidth={8}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeLinecap="round"
          strokeDasharray={`${(score / 100) * circumference} ${circumference}`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-xl font-bold tabular text-parch-100">{score}</span>
        {label ? <span className="text-[10px] uppercase tracking-wide text-parch-500">{label}</span> : null}
      </div>
    </div>
  );
}

export function ProgressBar({ value, color = "#38bdf8", className = "" }) {
  return (
    <div className={`h-1.5 w-full overflow-hidden rounded-full bg-ink-600/70 ${className}`}>
      <div
        className="h-full rounded-full transition-all"
        style={{ width: `${Math.max(0, Math.min(100, value * 100))}%`, backgroundColor: color }}
      />
    </div>
  );
}

export function MarketCapCell({ value }) {
  return (
    <span className="tabular text-parch-300">
      ${compactNumber(value)}
    </span>
  );
}

export function VolumeCell({ value }) {
  return <span className="tabular text-parch-500">{compactNumber(value)}</span>;
}

export function EmptyState({ title, detail }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-10 text-center">
      <p className="font-display text-sm font-semibold text-parch-200">{title}</p>
      <p className="mt-1 max-w-sm text-xs leading-5 text-parch-500">{detail}</p>
    </div>
  );
}

export function SectionTitle({ title, detail, right }) {
  return (
    <div className="panel-header">
      <div>
        <h2 className="font-display text-[15px] font-semibold tracking-wide text-parch-100">{title}</h2>
        {detail ? <p className="mt-0.5 text-xs text-parch-500">{detail}</p> : null}
      </div>
      {right}
    </div>
  );
}

export function formatMoney(value) {
  return money(value);
}

export function formatPercent(value) {
  return percent(value);
}
