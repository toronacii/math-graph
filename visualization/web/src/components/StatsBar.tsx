// Top-bar stats. Total nodes/edges, breakdown by entity type and
// edge relation, and selection size when a node is active.

import { useMemo } from "react";
import { useExplorer } from "../state/store";
import type { GraphPayload } from "../data/types";
import { RELATION_STYLES, TYPE_COLORS, TYPE_LABELS } from "../theme";

interface Props {
  payload: GraphPayload;
}

export default function StatsBar({ payload }: Props) {
  const selectedId = useExplorer((s) => s.selectedId);

  const summary = useMemo(() => {
    const byType: Record<string, number> = {};
    for (const n of payload.nodes) byType[n.type] = (byType[n.type] ?? 0) + 1;
    const byRel: Record<string, number> = {};
    for (const l of payload.links)
      byRel[l.relation] = (byRel[l.relation] ?? 0) + 1;
    return { byType, byRel };
  }, [payload]);

  return (
    <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
      <div className="text-sm text-slate-700">
        <span className="font-semibold">{payload.nodes.length}</span>
        <span className="ml-1 text-slate-500">nodes</span>
        <span className="mx-2 text-slate-300">·</span>
        <span className="font-semibold">{payload.links.length}</span>
        <span className="ml-1 text-slate-500">edges</span>
        <span className="mx-2 text-slate-300">·</span>
        <span className="text-[11px] uppercase tracking-wider text-slate-500">
          v{payload.schema_version}
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {Object.entries(summary.byType)
          .sort((a, b) => b[1] - a[1])
          .map(([t, n]) => (
            <span
              key={t}
              className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-[11px]"
            >
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{
                  background:
                    TYPE_COLORS[t as keyof typeof TYPE_COLORS] ?? "#94a3b8",
                }}
              />
              <span className="text-slate-600">
                {TYPE_LABELS[t as keyof typeof TYPE_LABELS] ?? t}
              </span>
              <span className="font-semibold text-slate-800">{n}</span>
            </span>
          ))}
      </div>

      <div className="flex flex-wrap gap-1.5">
        {Object.entries(summary.byRel).map(([r, n]) => (
          <span
            key={r}
            className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-[11px]"
          >
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{
                background:
                  RELATION_STYLES[r as keyof typeof RELATION_STYLES]?.color ??
                  "#94a3b8",
              }}
            />
            <span className="text-slate-600">{r}</span>
            <span className="font-semibold text-slate-800">{n}</span>
          </span>
        ))}
      </div>

      {selectedId && (
        <div className="ml-auto text-[11px] text-slate-500">
          selected: <code className="text-slate-700">{selectedId}</code>
        </div>
      )}
    </div>
  );
}
