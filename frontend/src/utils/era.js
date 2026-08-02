const ERAS = [
  { key: "2019", zh: "科创板元年", en: "The STAR Year", from: "2019-01-01", to: "2019-12-31" },
  { key: "2020", zh: "疫情与熔断", en: "Pandemic & Circuit Breaker", from: "2020-01-01", to: "2020-12-31" },
  { key: "2021", zh: "抱团与新能源", en: "Crowding & New Energy", from: "2021-01-01", to: "2021-12-31" },
  { key: "2022", zh: "熊市寒冬", en: "Bear Market Winter", from: "2022-01-01", to: "2022-12-31" },
  { key: "2023", zh: "存量博弈", en: "Zero-Sum Year", from: "2023-01-01", to: "2023-12-31" },
  { key: "2024", zh: "AI 与玄学", en: "AI & Mysticism", from: "2024-01-01", to: "2024-12-31" },
  { key: "2025", zh: "修复之年", en: "The Recovery Year", from: "2025-01-01", to: "2025-12-31" },
  { key: "2026", zh: "变革时代", en: "The Age of Change", from: "2026-01-01", to: "2026-12-31" },
];

export function eraForDate(date, lang) {
  if (!date) return { key: "2019", label: lang === "zh" ? ERAS[0].zh : ERAS[0].en };
  const year = String(date).slice(0, 4);
  const era = ERAS.find((item) => item.key === year) || ERAS[ERAS.length - 1];
  return { key: era.key, label: lang === "zh" ? era.zh : era.en };
}

export function playableEras(lang) {
  return ERAS.map((era) => ({ key: era.key, label: lang === "zh" ? era.zh : era.en }));
}
