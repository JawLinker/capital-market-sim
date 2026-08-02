/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0b0906",
          900: "#120e0a",
          850: "#17120b",
          800: "#1d170e",
          750: "#231c11",
          700: "#2d2415",
          600: "#423520",
          500: "#63513a",
        },
        parch: {
          100: "#f4ecd6",
          200: "#eadfc0",
          300: "#dfd0a8",
          400: "#cfb986",
          500: "#b49c6a",
          600: "#8f7a52",
          700: "#6b5a3e",
        },
        mint: "#7ba05b",
        risk: "#c05a45",
        brass: "#b08d57",
        gold: "#c9a24b",
        signal: "#7f9db5",
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
        display: [
          "Noto Serif SC",
          "Songti SC",
          "STSong",
          "Georgia",
          "serif",
        ],
      },
      boxShadow: {
        panel: "0 1px 0 rgba(240,230,200,0.04) inset, 0 12px 34px rgba(0,0,0,0.45)",
        paper: "0 1px 0 rgba(255,255,255,0.45) inset, 0 10px 26px rgba(0,0,0,0.35)",
      },
    },
  },
  plugins: [],
};
