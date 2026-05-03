import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui"],
        display: ["var(--font-display)", "ui-serif", "serif"]
      },
      colors: {
        ink: "#07100f",
        panel: "#0d1718",
        line: "rgba(255,255,255,0.12)",
        mint: "#7fffd4",
        violet: "#9b87ff",
        ice: "#d9fff3"
      },
      boxShadow: {
        glow: "0 0 80px rgba(127, 255, 212, 0.16)"
      }
    }
  },
  plugins: []
};

export default config;
