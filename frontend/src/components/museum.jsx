import { Flame } from "lucide-react";

export function EraBadge({ children, tone = "crimson", className = "" }) {
  const tones = {
    crimson: "border-risk/50 bg-risk/10 text-risk",
    brass: "border-brass/50 bg-brass/10 text-brass",
  };
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-[3px] border px-2 py-0.5 text-[11px] font-semibold tracking-[0.08em] ${tones[tone]} ${className}`}
    >
      {children}
    </span>
  );
}

export function MuseumHeader({ kicker, title, detail, right }) {
  return (
    <header className="relative overflow-hidden rounded-[3px] border border-ink-600/80 bg-ink-850/80 px-5 py-5 shadow-panel">
      <div className="pointer-events-none absolute -right-10 -top-12 h-36 w-36 rounded-full bg-brass/10 blur-3xl" />
      <div className="relative flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.22em] text-brass">
            <span className="h-px w-6 bg-brass/60" />
            {kicker}
          </p>
          <h1 className="mt-2 font-display text-2xl font-bold leading-9 text-parch-100 sm:text-3xl">
            {title}
          </h1>
          {detail ? <p className="mt-1.5 max-w-2xl text-sm leading-6 text-parch-400">{detail}</p> : null}
        </div>
        {right ? <div className="shrink-0">{right}</div> : null}
      </div>
    </header>
  );
}

export function ArchiveCard({ header, meta, stamp, children, className = "" }) {
  return (
    <article className={`panel relative overflow-hidden ${className}`}>
      {stamp ? (
        <span className="absolute right-4 top-4 rotate-6 rounded-[3px] border-2 border-risk/45 bg-ink-900/70 px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.18em] text-risk/85">
          {stamp}
        </span>
      ) : null}
      {header ? (
        <div className="flex items-center justify-between gap-3 border-b border-ink-600/70 px-4 py-3">
          {header}
        </div>
      ) : null}
      {meta ? (
        <div className="border-b border-ink-600/50 bg-ink-900/50 px-4 py-2.5">{meta}</div>
      ) : null}
      <div className="p-4">{children}</div>
    </article>
  );
}

export function TimelineNavigator({ eras, current, onSelect }) {
  return (
    <nav className="panel overflow-x-auto px-4 py-3">
      <div className="flex min-w-max items-center gap-1">
        {eras.map((era, index) => {
          const active = era.key === current;
          const passed = index < eras.findIndex((item) => item.key === current);
          return (
            <div key={era.key} className="flex items-center">
              {index > 0 ? (
                <span
                  className={`mx-1 h-px w-8 sm:w-12 ${passed || active ? "bg-brass/60" : "bg-ink-600/80"}`}
                />
              ) : null}
              <button
                onClick={() => onSelect?.(era.key)}
                className={`flex items-center gap-2 rounded-[3px] border px-2.5 py-1.5 text-xs transition-colors ${
                  active
                    ? "border-risk/50 bg-risk/10 font-semibold text-risk"
                    : passed
                      ? "border-brass/35 bg-brass/5 text-brass"
                      : "border-ink-600/80 text-parch-500 hover:border-brass/40 hover:text-parch-300"
                }`}
              >
                <span className="font-display text-[11px] font-bold tabular">{era.key}</span>
                <span className="hidden sm:inline">{era.label}</span>
              </button>
            </div>
          );
        })}
      </div>
    </nav>
  );
}

export function DocumentStamp({ children }) {
  return (
    <span className="inline-flex rotate-3 items-center gap-1 rounded-[3px] border-2 border-risk/50 px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-risk/90">
      <Flame size={10} />
      {children}
    </span>
  );
}
