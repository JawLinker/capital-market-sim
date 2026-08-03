import {
  Briefcase,
  Coins,
  Flame,
  Gem,
  Landmark,
  Moon,
  Rocket,
  Shield,
  Sparkles,
  Star,
  TrendingDown,
  TrendingUp,
  Trophy,
} from "lucide-react";

const ICONS = {
  "trending-up": TrendingUp,
  "trending-down": TrendingDown,
  moon: Moon,
  coins: Coins,
  shield: Shield,
  rocket: Rocket,
  flame: Flame,
  landmark: Landmark,
  star: Star,
  trophy: Trophy,
  gem: Gem,
  sparkles: Sparkles,
  briefcase: Briefcase,
};

const ICON_KEYS = Object.keys(ICONS);

const PALETTE = [
  { bg: "bg-risk/15", text: "text-risk", border: "border-risk/45" },
  { bg: "bg-brass/15", text: "text-brass", border: "border-brass/45" },
  { bg: "bg-mint/15", text: "text-mint", border: "border-mint/45" },
  { bg: "bg-sky/15", text: "text-sky", border: "border-sky/45" },
  { bg: "bg-gold/15", text: "text-gold", border: "border-gold/45" },
  { bg: "bg-parch-400/10", text: "text-parch-200", border: "border-parch-400/40" },
];

function hashSeed(seed) {
  let hash = 0;
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash * 31 + seed.charCodeAt(index)) >>> 0;
  }
  return hash;
}

export default function Avatar({ seed = "", iconKey, size = 28, className = "" }) {
  const hash = hashSeed(seed);
  const palette = PALETTE[hash % PALETTE.length];
  const key = iconKey || ICON_KEYS[hash % ICON_KEYS.length];
  const Icon = ICONS[key];
  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center rounded-[4px] border ${palette.border} ${palette.bg} ${className}`}
      style={{ width: size, height: size }}
      title={seed}
    >
      <Icon size={Math.max(12, Math.round(size * 0.56))} className={palette.text} />
    </span>
  );
}
