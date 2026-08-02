/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#070b10",
          900: "#0a0f14",
          850: "#0d141c",
          800: "#10171f",
          750: "#131c26",
          700: "#18232f",
          600: "#22303e",
          500: "#33465a",
        },
        mint: "#22c55e",
        risk: "#ef4444",
        signal: "#38bdf8",
        gold: "#f59e0b",
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "SFMono-Regular",
          "JetBrains Mono",
          "Consolas",
          "Liberation Mono",
          "monospace",
        ],
      },
      boxShadow: {
        panel: "0 1px 0 rgba(255,255,255,0.03) inset, 0 10px 30px rgba(0,0,0,0.25)",
      },
    },
  },
  plugins: [],
};
