import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}","./components/**/*.{js,ts,jsx,tsx,mdx}","./design-system/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        surface: { DEFAULT: "var(--surface)", hover: "var(--surface-hover)", strong: "var(--surface-strong)", card: "var(--surface)" },
        ink: { DEFAULT: "var(--foreground)", muted: "var(--muted)", soft: "var(--soft)" },
        border: { DEFAULT: "var(--border)", soft: "var(--divider)" },
        brand: { DEFAULT: "var(--brand)", hover: "var(--brand-hover)", soft: "var(--brand-soft)" },
        success: { DEFAULT: "var(--success)", soft: "var(--success-soft)" },
        ai: { DEFAULT: "var(--ai)", soft: "var(--ai-soft)" },
        alert: { DEFAULT: "var(--warning)", soft: "var(--warning-soft)" },
        warning: { DEFAULT: "var(--warning)", soft: "var(--warning-soft)" },
        highlight: { DEFAULT: "var(--highlight)", soft: "var(--highlight-soft)" },
        danger: { DEFAULT: "var(--danger)", soft: "var(--danger-soft)" },
      },
      fontFamily: {
        sans: ["Inter","ui-sans-serif","system-ui","sans-serif"],
        display: ["Outfit","Inter","ui-sans-serif","system-ui","sans-serif"],
        mono: ["IBM Plex Mono","ui-monospace","monospace"],
      },
      boxShadow: { sm: "var(--shadow-sm)", card: "var(--shadow-sm)", soft: "var(--shadow-md)", lg: "var(--shadow-lg)", focus: "var(--shadow-focus)" },
      borderRadius: { xs: "var(--radius-xs)", sm: "var(--radius-sm)", md: "var(--radius-md)", lg: "var(--radius-lg)", xl: "var(--radius-xl)", "2xl": "var(--radius-xl)" },
      transitionDuration: { fast: "120ms", base: "160ms", slow: "200ms" },
      transitionTimingFunction: { ui: "cubic-bezier(0.2, 0.8, 0.2, 1)" },
    },
  },
  plugins: [],
};
export default config;
