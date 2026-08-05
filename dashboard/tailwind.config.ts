import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#FBFAF8",
          card: "#FFFFFF",
        },
        ink: {
          DEFAULT: "#111111",
          muted: "#6B6560",
          soft: "#9A948C",
        },
        border: {
          DEFAULT: "#e5e2dd",
          soft: "#f0ede8",
        },
        brand: {
          DEFAULT: "#05B5DB",
          soft: "rgba(5, 181, 219, 0.12)",
        },
        success: {
          DEFAULT: "#0DA387",
          soft: "rgba(13, 163, 135, 0.12)",
        },
        ai: {
          DEFAULT: "#9B95FE",
          soft: "rgba(155, 149, 254, 0.12)",
        },
        alert: {
          DEFAULT: "#DD6539",
          soft: "rgba(221, 101, 57, 0.12)",
        },
        highlight: {
          DEFAULT: "#F7CA63",
          soft: "rgba(247, 202, 99, 0.18)",
        },
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
        display: [
          "Outfit",
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
      },
      boxShadow: {
        card: "0 1px 2px rgba(17, 17, 17, 0.04), 0 4px 16px rgba(17, 17, 17, 0.03)",
        soft: "0 8px 30px rgba(17, 17, 17, 0.04)",
        focus: "0 0 0 3px rgba(5, 181, 219, 0.2)",
      },
      borderRadius: {
        xl: "14px",
        "2xl": "18px",
      },
    },
  },
  plugins: [],
};

export default config;
