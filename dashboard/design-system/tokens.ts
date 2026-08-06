/**
 * ForceIA Design System — Foundation
 * Dark-first · dense · semantic color only · 4px grid
 */

export const colors = {
  bg: "#090909",
  canvas: "#0E0E0E",
  surface: "#141414",
  elevated: "#1A1A1A",
  border: "#232323",
  divider: "#2B2B2B",
  text: {
    primary: "#F5F5F5",
    secondary: "#A7A7A7",
    tertiary: "#707070",
  },
  brand: { DEFAULT: "#05B5DB", soft: "rgba(5,181,219,0.12)" },
  success: { DEFAULT: "#0DA387", soft: "rgba(13,163,135,0.12)" },
  ai: { DEFAULT: "#9B95FE", soft: "rgba(155,149,254,0.14)" },
  warning: { DEFAULT: "#DD6539", soft: "rgba(221,101,57,0.12)" },
  highlight: { DEFAULT: "#F7CA63", soft: "rgba(247,202,99,0.14)" },
  danger: { DEFAULT: "#E5484D", soft: "rgba(229,72,77,0.12)" },
} as const;

/** 4px grid */
export const spacing = {
  0: "0",
  1: "4px",
  2: "8px",
  3: "12px",
  4: "16px",
  5: "20px",
  6: "24px",
  8: "32px",
  10: "40px",
  12: "48px",
  16: "64px",
} as const;

export const radius = {
  none: "0",
  xs: "2px",
  sm: "4px",
  md: "6px",
  lg: "8px",
  full: "9999px",
} as const;

export const motion = {
  fast: "120ms",
  base: "160ms",
  slow: "180ms",
  ease: "cubic-bezier(0.2, 0.8, 0.2, 1)",
} as const;

/**
 * Type scale — use only these roles across the product.
 * sizes in rem for accessibility; weights limited to 400/500/600.
 */
export const typography = {
  title: { size: "14px", weight: 500, lineHeight: "20px", tracking: "-0.01em" },
  section: { size: "13px", weight: 500, lineHeight: "18px", tracking: "-0.01em" },
  body: { size: "13px", weight: 400, lineHeight: "18px", tracking: "0" },
  bodyMuted: { size: "12px", weight: 400, lineHeight: "16px", tracking: "0" },
  meta: { size: "11px", weight: 400, lineHeight: "14px", tracking: "0" },
  label: { size: "10px", weight: 500, lineHeight: "12px", tracking: "0.08em" },
  metric: { size: "20px", weight: 500, lineHeight: "24px", tracking: "-0.02em" },
  metricSm: { size: "16px", weight: 500, lineHeight: "20px", tracking: "-0.02em" },
  mono: { size: "11px", weight: 400, lineHeight: "14px", tracking: "0" },
  badge: { size: "10px", weight: 500, lineHeight: "12px", tracking: "0.02em" },
} as const;

/** Lucide defaults — single icon language */
export const icon = {
  strokeWidth: 1.75,
  sizes: { xs: 12, sm: 14, md: 16, lg: 20 } as const,
} as const;

/** Shared panel chrome */
export const panel = {
  headerHeight: "36px",
  headerPx: "12px",
  rowPy: "8px",
  rowPx: "12px",
} as const;
