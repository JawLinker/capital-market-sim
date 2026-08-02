import { industryColor } from "../../utils/format.js";

export default function DonutChart({
  data,
  size = 168,
  thickness = 22,
  centerTitle,
  centerValue,
}) {
  const radius = (size - thickness) / 2;
  const circumference = 2 * Math.PI * radius;
  const total = data.reduce((sum, item) => sum + item.weight, 0) || 1;

  let offset = 0;
  const segments = data.map((item) => {
    const fraction = item.weight / total;
    const segment = {
      ...item,
      dash: `${fraction * circumference} ${circumference}`,
      offset: -offset * circumference,
    };
    offset += fraction;
    return segment;
  });

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(51, 70, 90, 0.35)"
          strokeWidth={thickness}
        />
        {segments.map((segment) => (
          <circle
            key={segment.industry || segment.label}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={segment.color || industryColor(segment.industry)}
            strokeWidth={thickness}
            strokeDasharray={segment.dash}
            strokeDashoffset={segment.offset}
            strokeLinecap="butt"
          />
        ))}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        {centerTitle ? (
          <span className="text-[11px] font-medium uppercase tracking-wide text-parch-600">
            {centerTitle}
          </span>
        ) : null}
        <span className="text-lg font-semibold text-parch-100 tabular">{centerValue}</span>
      </div>
    </div>
  );
}
