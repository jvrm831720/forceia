/** ForceIA Design System 2.0 — silent UI, data-first, controlled contrast */
export const colors = {
  brand: { DEFAULT: "#05B5DB", hover: "#049FBF", soft: "rgba(5,181,219,0.10)" },
  success: { DEFAULT: "#0DA387", soft: "rgba(13,163,135,0.10)" },
  ai: { DEFAULT: "#9B95FE", soft: "rgba(155,149,254,0.12)" },
  warning: { DEFAULT: "#DD6539", soft: "rgba(221,101,57,0.10)" },
  highlight: { DEFAULT: "#F7CA63", soft: "rgba(247,202,99,0.14)" },
  danger: { DEFAULT: "#E5484D", soft: "rgba(229,72,77,0.10)" },
} as const;
export const spacing = {
  1: "4px", 2: "8px", 3: "12px", 4: "16px", 5: "20px", 6: "24px",
  8: "32px", 10: "40px", 12: "48px", 16: "64px", 20: "80px", 24: "96px",
} as const;
export const radius = {
  none: "0", xs: "4px", sm: "6px", md: "8px", lg: "10px", xl: "12px", full: "9999px",
} as const;
export const shadows = {
  sm: "0 1px 2px rgba(17,17,17,0.04)",
  md: "0 2px 8px rgba(17,17,17,0.05)",
  lg: "0 8px 24px rgba(17,17,17,0.06)",
  focus: "0 0 0 3px rgba(5,181,219,0.22)",
} as const;
export const motion = {
  fast: "120ms", base: "160ms", slow: "200ms",
  ease: "cubic-bezier(0.2, 0.8, 0.2, 1)",
} as const;
