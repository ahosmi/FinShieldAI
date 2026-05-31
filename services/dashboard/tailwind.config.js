/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy:    { DEFAULT: "#0a0e1a", card: "#0f1629", border: "#1a2040" },
        cyber:   { blue: "#00d4ff", green: "#00ff88", red: "#ff3366", yellow: "#ffd700", purple: "#a855f7" },
      },
      fontFamily: { mono: ["'JetBrains Mono'", "monospace"] },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "slide-in":   "slideIn 0.3s ease-out",
        "fade-in":    "fadeIn 0.5s ease-out",
      },
      keyframes: {
        slideIn:  { from: { transform: "translateY(-8px)", opacity: 0 }, to: { transform: "translateY(0)", opacity: 1 } },
        fadeIn:   { from: { opacity: 0 }, to: { opacity: 1 } },
      },
    },
  },
  plugins: [],
};
