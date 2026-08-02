import { useEffect, useRef } from "react";
import {
  ColorType,
  CrosshairMode,
  createChart,
} from "lightweight-charts";

const UP = "#22c55e";
const DOWN = "#ef4444";

export default function PriceChart({
  data,
  height = 340,
  showVolume = true,
  markers = [],
}) {
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || data.length === 0) return;

    const chart = createChart(container, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#7d8fa3",
        fontSize: 11,
        fontFamily:
          "SFMono-Regular, Consolas, 'Liberation Mono', monospace",
      },
      grid: {
        vertLines: { color: "rgba(51, 70, 90, 0.22)" },
        horzLines: { color: "rgba(51, 70, 90, 0.22)" },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: "#38bdf8", width: 1, style: 2, labelBackgroundColor: "#1d2833" },
        horzLine: { color: "#38bdf8", width: 1, style: 2, labelBackgroundColor: "#1d2833" },
      },
      timeScale: {
        borderColor: "#22303e",
        timeVisible: false,
        rightOffset: 4,
        barSpacing: 7,
      },
      rightPriceScale: {
        borderColor: "#22303e",
        scaleMargins: { top: 0.08, bottom: showVolume ? 0.28 : 0.08 },
      },
      localization: {
        locale: "en-US",
        priceFormatter: (price) =>
          price >= 1000 ? `$${price.toFixed(0)}` : `$${price.toFixed(2)}`,
      },
    });

    const candles = chart.addCandlestickSeries({
      upColor: UP,
      downColor: DOWN,
      borderUpColor: UP,
      borderDownColor: DOWN,
      wickUpColor: UP,
      wickDownColor: DOWN,
    });
    candles.setData(
      data.map((point) => ({
        time: point.date,
        open: point.open,
        high: point.high,
        low: point.low,
        close: point.close,
      }))
    );
    if (markers.length > 0) {
      candles.setMarkers(markers);
    }

    let volume;
    if (showVolume) {
      volume = chart.addHistogramSeries({
        priceFormat: { type: "volume" },
        priceScaleId: "volume",
        color: "rgba(56, 189, 248, 0.35)",
      });
      chart.priceScale("volume").applyOptions({
        scaleMargins: { top: 0.82, bottom: 0 },
      });
      volume.setData(
        data.map((point) => ({
          time: point.date,
          value: point.volume,
          color:
            point.close >= point.open
              ? "rgba(34, 197, 94, 0.32)"
              : "rgba(239, 68, 68, 0.32)",
        }))
      );
    }

    chart.timeScale().fitContent();
    const resize = () => chart.applyOptions({ width: container.clientWidth });
    const observer = new ResizeObserver(resize);
    observer.observe(container);

    return () => {
      observer.disconnect();
      chart.remove();
    };
  }, [data, showVolume, markers]);

  return <div ref={containerRef} style={{ height }} className="w-full" />;
}
