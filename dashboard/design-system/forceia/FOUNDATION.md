# ForceIA Foundation Pass

## Typography (only these roles)
| Role | Class | Size | Weight | Use |
|------|-------|------|--------|-----|
| title | `.text-title` | 14px | 500 | Page / company name |
| section | `.text-section` | 13px | 500 | Panel headers |
| body | `.text-body` | 13px | 400 | Row titles |
| body-muted | `.text-body-muted` | 12px | 400 | Descriptions |
| meta | `.text-meta` | 11px | 400 | Secondary meta |
| label | `.text-label` | 10px | 500 | Uppercase labels |
| metric | `.text-metric` | 20px | 500 mono | KPI values |
| metric-sm | `.text-metric-sm` | 16px | 500 mono | Nested metrics |
| mono | `.text-mono` | 11px | 400 mono | Codes, deltas, times |
| badge | `.text-badge` | 10px | 500 | Badges |

Weights allowed: **400 / 500 / 600 only**.

## Icons
- Library: **Lucide only**
- Wrapper: `<Icon icon={X} size="sm|md|lg" />`
- strokeWidth: **1.75**
- sizes: 12 / 14 / 16 / 20

## Spacing (4px grid)
Panel header: h-9, px-3  
Panel row: px-3 py-2  
Section gap: gap-2 / 2.5  

## Surfaces
- Outer: `border border-border bg-canvas`
- Internal: `divide-y divide-border`
- Hover row: `hover:bg-surface`
- No card shadows
- Radius: sm (4px) for chips/badges only

## Shared chrome
`Panel` + `PanelHeader` + `PanelBody` for Timeline, Handoffs, Services, Agenda.
