import { ImageResponse } from "next/og";

// ForceIA brand mark — Signal Cyan rounded square + "F" glyph.

export const runtime = "edge";
export const size = { width: 32, height: 32 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#27C6E5",
          borderRadius: 8,
        }}
      >
        <span
          style={{
            color: "#0A0A0B",
            fontSize: 18,
            fontWeight: 700,
            lineHeight: 1,
            fontFamily: "system-ui, sans-serif",
          }}
        >
          F
        </span>
      </div>
    ),
    { ...size },
  );
}
