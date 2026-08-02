import { useMemo, useState } from "react";
import { ArrowDownCircle, ArrowUpCircle } from "lucide-react";

import { useApp } from "../store/AppContext.jsx";
import { money } from "../utils/format.js";

const FEE_RATE = 0.0015;
const MIN_FEE = 1;

export default function OrderPanel({ stock, defaultAction = "buy" }) {
  const { portfolio, executeTrade, busy, t } = useApp();
  const [action, setAction] = useState(defaultAction);
  const [shares, setShares] = useState("");

  const holding = portfolio?.holdings?.find((item) => item.ticker === stock?.ticker);
  const price = stock?.price || 0;
  const fillPrice =
    action === "buy" ? stock?.ask || price : stock?.bid || price;
  const shareCount = Number.parseFloat(shares) || 0;
  const gross = shareCount * fillPrice;
  const fee = Math.max(MIN_FEE, gross * FEE_RATE);
  const stamp = action === "sell" ? gross * 0.0005 : 0;
  const cash = portfolio?.summary?.cash || 0;
  const maxBuy = fillPrice > 0 ? Math.floor((cash - Math.max(MIN_FEE, 1)) / (fillPrice * (1 + FEE_RATE)) * 100) / 100 : 0;
  const maxSell = holding?.shares || 0;
  const maxShares = action === "buy" ? maxBuy : maxSell;
  const blocked = action === "buy" ? stock?.limit_up : stock?.limit_down;
  const tPlusOne = action === "sell" && (holding?.locked_shares || 0) > 0;

  const canSubmit = useMemo(
    () =>
      shareCount > 0 &&
      gross >= 10 &&
      !blocked &&
      !tPlusOne &&
      (action === "buy" ? gross + fee <= cash + 1e-6 : shareCount <= maxSell - (holding?.locked_shares || 0) + 1e-6),
    [shareCount, gross, fee, cash, action, maxSell, blocked, tPlusOne, holding]
  );

  const setQuick = (fraction) => {
    const base = action === "buy" ? maxBuy : maxSell;
    setShares(base > 0 ? String(Math.floor(base * fraction * 100) / 100) : "");
  };

  const submit = () => {
    if (!canSubmit) return;
    executeTrade(action, stock.ticker, shareCount, stock.name);
    setShares("");
  };

  if (!stock) return null;

  return (
    <div className="panel">
      <div className="panel-header">
        <h3 className="truncate text-sm font-semibold text-parch-100">{t("order.title", { ticker: stock.name })}</h3>
        <span className="text-xs tabular text-parch-500">{money(stock.price)}</span>
      </div>
      <div className="grid grid-cols-2 gap-1 border-b border-ink-600/70 p-2">
        <button
          onClick={() => setAction("buy")}
          className={`flex items-center justify-center gap-1.5 rounded-md border px-3 py-2 text-sm font-semibold transition-colors ${
            action === "buy"
              ? "border-mint/50 bg-mint/15 text-mint"
              : "border-ink-500/50 text-parch-500 hover:bg-ink-700/50"
          }`}
        >
          <ArrowUpCircle size={16} />
          {t("order.buy")}
        </button>
        <button
          onClick={() => setAction("sell")}
          className={`flex items-center justify-center gap-1.5 rounded-md border px-3 py-2 text-sm font-semibold transition-colors ${
            action === "sell"
              ? "border-risk/50 bg-risk/15 text-risk"
              : "border-ink-500/50 text-parch-500 hover:bg-ink-700/50"
          }`}
        >
          <ArrowDownCircle size={16} />
          {t("order.sell")}
        </button>
      </div>
      <div className="space-y-3 p-4">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-parch-500">{t("order.shares")}</label>
          <div className="flex gap-2">
            <input
              type="number"
              min="0"
              step="0.01"
              value={shares}
              onChange={(event) => setShares(event.target.value)}
              placeholder="0.00"
              className="input tabular"
            />
            <button
              onClick={() => setQuick(0.25)}
              className="btn btn-ghost shrink-0 px-2.5 text-xs"
            >
              {t("order.quarter")}
            </button>
            <button
              onClick={() => setQuick(0.5)}
              className="btn btn-ghost shrink-0 px-2.5 text-xs"
            >
              {t("order.half")}
            </button>
            <button
              onClick={() => setQuick(1)}
              className="btn btn-ghost shrink-0 px-2.5 text-xs"
            >
              {t("order.max")}
            </button>
          </div>
        </div>
        <dl className="space-y-1.5 text-xs">
          <div className="flex justify-between">
            <dt className="text-parch-600">{t("order.gross")}</dt>
            <dd className="tabular text-parch-300">{money(gross)}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-parch-600">{t("order.commission")}</dt>
            <dd className="tabular text-parch-300">{money(shareCount > 0 ? fee : 0)}</dd>
          </div>
          {action === "sell" ? (
            <div className="flex justify-between">
              <dt className="text-parch-600">{t("order.stampTax")}</dt>
              <dd className="tabular text-parch-300">{money(shareCount > 0 ? stamp : 0)}</dd>
            </div>
          ) : null}
          <div className="flex justify-between border-t border-ink-600/70 pt-1.5">
            <dt className="font-medium text-parch-500">
              {t(action === "buy" ? "order.totalCost" : "order.netProceeds")}
            </dt>
            <dd className="tabular font-semibold text-parch-100">
              {action === "buy" ? money(gross + fee) : money(gross - fee - stamp)}
            </dd>
          </div>
        </dl>
        {blocked ? (
          <p className="text-[11px] font-medium text-risk">
            {action === "buy" ? t("market.limitUp") : t("market.limitDown")}
            ：{t(action === "buy" ? "order.noSellers" : "order.noBuyers")}
          </p>
        ) : null}
        {tPlusOne ? (
          <p className="text-[11px] font-medium text-gold">{t("order.tPlusOne")}</p>
        ) : null}
        <button
          onClick={submit}
          disabled={!canSubmit || busy}
          className={`btn w-full ${action === "buy" ? "btn-primary" : "btn-danger"}`}
        >
          {t(action === "buy" ? "order.buyShares" : "order.sellShares")}
        </button>
        <p className="text-[11px] leading-4 text-parch-600">
          {t("order.minimum", { min: 10, cash: money(cash) })}{" "}
          {action === "sell"
            ? t("order.youHold", { shares: (holding?.shares || 0).toFixed(4) })
            : t("order.maxBuy", { shares: maxBuy.toFixed(2) })}
        </p>
      </div>
    </div>
  );
}
