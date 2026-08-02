import { useEffect, useRef } from "react";
import {
  ColorType,
  createChart,
  LineStyle,
} from "lightweight-charts";

export default function LineChart({
  data,
  height = 300,
  color = "#38bdf8",
  baseline,
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
        fontFamily: "SFMono-Regular, Consolas, 'Liberation Mono', monospace",
      },
      grid: {
        vertLines: { color: "rgba(51, 70, 90, 0.18)" },
        horzLines: { color: "rgba(51, 70, 90, 0.18)" },
      },
      crosshair: {
        vertLine: { color: "#38bdf8", labelBackgroundColor: "#1d2833" },
        horzLine: { color: "#38bdf8", labelBackgroundColor: "#1d2833" },
      },
      timeScale: {
        borderColor: "#22303e",
        rightOffset: 4,
        barSpacing: 9,
      },
      rightPriceScale: {
        borderColor: "#22303e",
        scaleMargins: { top: 0.12, bottom: 0.12 },
      },
      localization: {
        locale: "en-US",
        priceFormatter: (price) => `$${price.toFixed(0)}`,
      },
    });

    const series = chart.addAreaSeries({
      lineColor: color,
      topColor: `${color}55`,
      bottomColor: "rgba(10, 15, 20, 0)",
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: true,
      crosshairMarkerVisible: true,
    });
    series.setData(data.map((point) => ({ time: point.date, value: point.value })));

    if (baseline !== undefined && baseline !== null) {
      const baselineSeries = chart.addLineSeries({
        color: "#64748b",
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        priceLineVisible: false,
        lastValueVisible: false,
      });
      baselineSeries.setData(
        data.map((point) => ({ time: point.date, value: baseline }))
      );
    }

    chart.timeScale().fitContent();
    const observer = new ResizeObserver(() => {
      chart.applyOptions({ width: container.clientWidth });
    });
    observer.observe(container);

    return () => {
      observer.disconnect();
      chart.remove();
    };
  }, [data, color, baseline]);

  return <div ref={containerRef} style={{ height }} className="w-full" />;
}
