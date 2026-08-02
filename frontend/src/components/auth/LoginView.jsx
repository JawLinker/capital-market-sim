import { useState } from "react";
import { CandlestickChart, LogIn, UserPlus } from "lucide-react";

import { useApp } from "../../store/AppContext.jsx";

export default function LoginView() {
  const { t, login, register, lang } = useApp();
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!username.trim() || password.length < 4) {
      setError(t("auth.errorLength"));
      return;
    }
    setBusy(true);
    setError("");
    try {
      if (mode === "login") {
        await login(username.trim(), password);
      } else {
        await register(username.trim(), password);
      }
    } catch (err) {
      setError(err.message || t("auth.errorGeneric"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex h-full items-center justify-center p-4">
      <div className="panel w-full max-w-sm p-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-gradient-to-br from-mint/80 to-sky/70 text-ink-950">
            <CandlestickChart size={20} strokeWidth={2.4} />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-100">{t("app.name")}</h1>
            <p className="text-xs text-slate-500">{t("auth.subtitle")}</p>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-1 rounded-md border border-ink-600/70 bg-ink-900/60 p-1">
          <button
            onClick={() => setMode("login")}
            className={`flex items-center justify-center gap-1.5 rounded px-3 py-2 text-sm font-semibold transition-colors ${
              mode === "login"
                ? "bg-sky/15 text-sky"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <LogIn size={15} /> {t("auth.login")}
          </button>
          <button
            onClick={() => setMode("register")}
            className={`flex items-center justify-center gap-1.5 rounded px-3 py-2 text-sm font-semibold transition-colors ${
              mode === "register"
                ? "bg-mint/15 text-mint"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <UserPlus size={15} /> {t("auth.register")}
          </button>
        </div>

        <div className="mt-4 space-y-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              {t("auth.username")}
            </label>
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="input"
              autoComplete="username"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              {t("auth.password")}
            </label>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && submit()}
              className="input"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
            />
          </div>
          {error ? <p className="text-xs font-medium text-risk">{error}</p> : null}
          <button
            onClick={submit}
            disabled={busy}
            className="btn btn-primary w-full"
          >
            {busy
              ? t("topbar.running")
              : t(mode === "login" ? "auth.login" : "auth.register")}
          </button>
          <p className="text-center text-[11px] leading-4 text-slate-500">
            {lang === "zh" ? t("auth.hostHintZh") : t("auth.hostHint")}
            <span className="mt-1 block">{t("auth.lanHint")}</span>
          </p>
        </div>
      </div>
    </div>
  );
}
