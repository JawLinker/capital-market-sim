import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownCircle,
  ArrowUpCircle,
  Clock,
  ListOrdered,
  X,
  Zap,
} from "lucide-react";

import { api } from "../api/client.js";
import { useApp } from "../store/AppContext.jsx";
import { money } from "../utils/format.js";

const FEE_RATE = 0.0015;
const MIN_FEE = 1;

export default function OrderPanel({ stock, defaultAction = "buy" }) {
  const { portfolio, executeTrade, busy, t } = useApp();
  const [action, setAction] = useState(defaultAction);
  const [shares, setShares] = useState("");
  const [mode, setMode] = useState("market");
  const [channel, setChannel] = useState("exchange");
  const [leverage, setLeverage] = useState(1);
  const [limitPrice, setLimitPrice] = useState("");
  const [orders, setOrders] = useState([]);
  const [notice, setNotice] = useState("");

  const refreshOrders = () => {
    api
      .getOrders()
      .then((data) => setOrders(data.orders || []))
      .catch(() => {});
  };

  useEffect(() => {
    refreshOrders();
  }, [stock?.ticker]);

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
  const limitValid =
    mode === "limit" &&
    Number.parseFloat(limitPrice) > 0 &&
    shareCount > 0 &&
    shareCount * Number.parseFloat(limitPrice) >= 10;

  const canSubmit = useMemo(
    () =>
      mode === "limit"
        ? limitValid
        : shareCount > 0 &&
          gross >= 10 &&
          !blocked &&
          !tPlusOne &&
          (action === "buy" ? gross + fee <= cash + 1e-6 : shareCount <= maxSell - (holding?.locked_shares || 0) + 1e-6),
    [shareCount, gross, fee, cash, action, maxSell, blocked, tPlusOne, holding, mode, limitValid]
  );

  const setQuick = (fraction) => {
    const base = action === "buy" ? maxBuy : maxSell;
    setShares(base > 0 ? String(Math.floor(base * fraction * 100) / 100) : "");
  };

  const submit = () => {
    if (!canSubmit) return;
    setNotice("");
    if (mode === "limit") {
      api
        .createOrder(
          stock.ticker,
          action === "buy" ? "buy_limit" : "sell_limit",
          Number.parseFloat(limitPrice),
          shareCount
        )
        .then(() => {
          setNotice(t("order.limitPlaced"));
          setShares("");
          setLimitPrice("");
          refreshOrders();
        })
        .catch((error) => setNotice(error.message));
      return;
    }
    executeTrade(
      action,
      stock.ticker,
      shareCount,
      stock.name,
      channel === "dark",
      leverage
    );
    setShares("");
  };

  const cancelOrder = (orderId) => {
    api
      .cancelOrder(orderId)
      .then(refreshOrders)
      .catch(() => {});
  };

  if (!stock) return null;

  const stockOrders = orders.filter((order) => order.ticker === stock.ticker);

  return (
    <div className="panel">
      <div className="panel-header">
        <h3 className="truncate text-sm font-semibold text-parch-100">{t("order.title", { ticker: stock.name })}</h3>
        <span className="text-xs tabular text-parch-500">{money(stock.price)}</span>
      </div>
      <div className="grid grid-cols-2 gap-1 border-b border-ink-600/70 p-2">
        <button
          onClick={() => setAction("buy")}
          className={`flex items-center justify-center gap-1.5 rounded-[3px] border px-3 py-2 text-sm font-semibold transition-colors ${
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
          className={`flex items-center justify-center gap-1.5 rounded-[3px] border px-3 py-2 text-sm font-semibold transition-colors ${
            action === "sell"
              ? "border-risk/50 bg-risk/15 text-risk"
              : "border-ink-500/50 text-parch-500 hover:bg-ink-700/50"
          }`}
        >
          <ArrowDownCircle size={16} />
          {t("order.sell")}
        </button>
      </div>
      <div className="grid grid-cols-2 gap-1 border-b border-ink-600/70 p-2">
        <button
          onClick={() => setMode("market")}
          className={`flex items-center justify-center gap-1.5 rounded-[3px] border px-3 py-1.5 text-xs font-semibold transition-colors ${
            mode === "market"
              ? "border-brass/50 bg-brass/15 text-brass"
              : "border-ink-500/50 text-parch-500 hover:bg-ink-700/50"
          }`}
        >
          <Zap size={13} />
          {t("order.market")}
        </button>
        <button
          onClick={() => setMode("limit")}
          className={`flex items-center justify-center gap-1.5 rounded-[3px] border px-3 py-1.5 text-xs font-semibold transition-colors ${
            mode === "limit"
              ? "border-brass/50 bg-brass/15 text-brass"
              : "border-ink-500/50 text-parch-500 hover:bg-ink-700/50"
          }`}
        >
          <Clock size={13} />
          {t("order.limit")}
        </button>
      </div>
      {mode === "market" ? (
        <div className="grid grid-cols-2 gap-1 border-b border-ink-600/70 p-2">
          <button
            onClick={() => setChannel("exchange")}
            className={`flex items-center justify-center gap-1.5 rounded-[3px] border px-3 py-1.5 text-xs font-semibold transition-colors ${
              channel === "exchange"
                ? "border-brass/50 bg-brass/15 text-brass"
                : "border-ink-500/50 text-parch-500 hover:bg-ink-700/50"
            }`}
          >
            <Zap size={13} />
            {t("order.channelExchange")}
          </button>
          <button
            onClick={() => setChannel("dark")}
            className={`flex items-center justify-center gap-1.5 rounded-[3px] border px-3 py-1.5 text-xs font-semibold transition-colors ${
              channel === "dark"
                ? "border-ink-400/50 bg-ink-500/15 text-parch-200"
                : "border-ink-500/50 text-parch-500 hover:bg-ink-700/50"
            }`}
            title={t("order.darkHint")}
          >
            <ListOrdered size={13} />
            {t("order.channelDark")}
          </button>
        </div>
      ) : null}
      <div className="space-y-3 p-4">
        {channel === "dark" && mode === "market" ? (
          <p className="rounded-[3px] border border-ink-500/40 bg-ink-900/60 px-3 py-2 text-[11px] leading-5 text-parch-500">
            {t("order.darkHint")}
          </p>
        ) : null}
        {action === "buy" && mode === "market" ? (
          <div className="flex items-center justify-between gap-2 rounded-[3px] border border-ink-600/70 bg-ink-900/60 px-3 py-2">
            <p className="text-[11px] font-medium text-parch-500">{t("order.leverage")}</p>
            <div className="flex gap-1">
              {[1, 1.5, 2].map((level) => (
                <button
                  key={level}
                  onClick={() => setLeverage(level)}
                  className={`rounded px-2 py-0.5 text-[11px] font-semibold tabular transition-colors ${
                    leverage === level
                      ? "bg-risk/15 text-risk"
                      : "text-parch-600 hover:text-parch-300"
                  }`}
                  title={t("order.marginHint")}
                >
                  {level}x
                </button>
              ))}
            </div>
          </div>
        ) : null}
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
              onClick={() => setShares("100")}
              className="btn btn-ghost shrink-0 px-2.5 text-xs"
              title={t("order.lotTitle")}
            >
              {t("order.lot")}
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
        {mode === "limit" ? (
          <div>
            <label className="mb-1.5 block text-xs font-medium text-parch-500">
              {t("order.limitPrice")}
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={limitPrice}
              onChange={(event) => setLimitPrice(event.target.value)}
              placeholder="0.00"
              className="input tabular"
            />
          </div>
        ) : null}
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
            {" · "}
            {t(action === "buy" ? "order.noSellers" : "order.noBuyers")}
          </p>
        ) : null}
        {tPlusOne ? (
          <p className="text-[11px] font-medium text-gold">{t("order.tPlusOne")}</p>
        ) : null}
        {notice ? <p className="text-[11px] font-medium text-brass">{notice}</p> : null}
        <button
          onClick={submit}
          disabled={!canSubmit || busy}
          className={`btn w-full ${action === "buy" ? "btn-primary" : "btn-danger"}`}
        >
          {t(action === "buy" ? "order.buyShares" : "order.sellShares")}
        </button>
        {action === "buy" && mode === "market" ? (
          <div>
            <p className="mb-1.5 text-[11px] font-medium text-parch-600">
              {t("judgment.tag")}
            </p>
            <div className="grid grid-cols-4 gap-1">
              {[
                ["rally", t("judgment.thesis.rally")],
                ["dip", t("judgment.thesis.dip")],
                ["gamble", t("judgment.thesis.gamble")],
                ["value", t("judgment.thesis.value")],
              ].map(([thesis, label]) => (
                <button
                  key={thesis}
                  onClick={() => {
                    api
                      .createJudgment(stock.ticker, thesis)
                      .then(() => setNotice(t("judgment.recorded")))
                      .catch((error) => setNotice(error.message));
                  }}
                  className="btn btn-ghost px-1 py-1 text-[10px]"
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        ) : null}
        <p className="text-[11px] leading-4 text-parch-600">
          {t("order.minimum", { min: 10, cash: money(cash) })}{" "}
          {action === "sell"
            ? t("order.youHold", { shares: (holding?.shares || 0).toFixed(4) })
            : t("order.maxBuy", { shares: maxBuy.toFixed(2) })}
        </p>
      </div>
      {stockOrders.length > 0 ? (
        <div className="border-t border-ink-600/70">
          <div className="flex items-center gap-2 px-4 py-2.5">
            <ListOrdered size={13} className="text-brass" />
            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-parch-600">
              {t("order.openOrders")}
            </p>
          </div>
          <ul className="divide-y divide-ink-600/50">
            {stockOrders.map((order) => (
              <li key={order.id} className="flex items-center gap-2 px-4 py-2 text-xs">
                <span className="rounded-[3px] border border-brass/40 bg-brass/10 px-1.5 py-0.5 text-[10px] font-semibold text-brass">
                  {t(`order.kind.${order.kind}`)}
                </span>
                <span className="tabular text-parch-300">{money(order.price)}</span>
                <span className="tabular text-parch-500">{order.shares.toFixed(4)}</span>
                <span className="ml-auto text-[10px] uppercase tracking-wide text-parch-600">
                  {order.status}
                </span>
                {order.status === "open" ? (
                  <button
                    onClick={() => cancelOrder(order.id)}
                    className="rounded p-1 text-parch-600 transition-colors hover:bg-ink-700 hover:text-risk"
                    aria-label={t("order.cancel")}
                  >
                    <X size={12} />
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
