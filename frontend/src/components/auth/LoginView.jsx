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
          <div className="flex h-10 w-10 items-center justify-center rounded-[3px] border border-brass/50 bg-brass/15 text-brass">
            <CandlestickChart size={20} strokeWidth={2.4} />
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-brass">
              {t("auth.kicker")}
            </p>
            <h1 className="font-display text-base font-bold text-parch-100">{t("app.brand")}</h1>
            <p className="text-xs text-parch-500">{t("auth.subtitle")}</p>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-1 rounded-md border border-ink-600/70 bg-ink-900/60 p-1">
          <button
            onClick={() => setMode("login")}
            className={`flex items-center justify-center gap-1.5 rounded px-3 py-2 text-sm font-semibold transition-colors ${
              mode === "login"
                ? "bg-sky/15 text-sky"
                : "text-parch-500 hover:text-parch-200"
            }`}
          >
            <LogIn size={15} /> {t("auth.login")}
          </button>
          <button
            onClick={() => setMode("register")}
            className={`flex items-center justify-center gap-1.5 rounded px-3 py-2 text-sm font-semibold transition-colors ${
              mode === "register"
                ? "bg-mint/15 text-mint"
                : "text-parch-500 hover:text-parch-200"
            }`}
          >
            <UserPlus size={15} /> {t("auth.register")}
          </button>
        </div>

        <div className="mt-4 space-y-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-parch-500">
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
            <label className="mb-1 block text-xs font-medium text-parch-500">
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
          <p className="text-center text-[11px] leading-4 text-parch-600">
            {lang === "zh" ? t("auth.hostHintZh") : t("auth.hostHint")}
            <span className="mt-1 block">{t("auth.lanHint")}</span>
          </p>
        </div>
      </div>
    </div>
  );
}
