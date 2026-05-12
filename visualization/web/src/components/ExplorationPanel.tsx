// Neighborhood exploration + path highlighting controls.
// Appears in the left sidebar when a node is selected.

import clsx from "clsx";
import { useExplorer, type ExplorationMode } from "../state/store";
import type { NodeDetailsMap } from "../data/types";
import { TYPE_COLORS } from "../theme";

interface Props {
  details: NodeDetailsMap;
}

const MODES: { mode: ExplorationMode; label: string; title: string }[] = [
  { mode: "full", label: "Full", title: "Show full graph" },
  { mode: "neighborhood", label: "Neighbors", title: "Immediate neighbors (all edges)" },
  { mode: "ancestors", label: "Needs", title: "Everything this node depends on (outbound BFS)" },
  { mode: "descendants", label: "Used by", title: "Everything that depends on this (inbound BFS)" },
  { mode: "proof-neighborhood", label: "Proof nbr", title: "Neighbors via proves/uses edges" },
  { mode: "conceptual-neighborhood", label: "Concept nbr", title: "Neighbors via depends_on edges" },
];

export default function ExplorationPanel({ details }: Props) {
  const selectedId = useExplorer((s) => s.selectedId);
  const explorationMode = useExplorer((s) => s.explorationMode);
  const pathPinnedId = useExplorer((s) => s.pathPinnedId);
  const setExplorationMode = useExplorer((s) => s.setExplorationMode);
  const pinPath = useExplorer((s) => s.pinPath);
  const select = useExplorer((s) => s.select);

  if (!selectedId) return null;

  const d = details[selectedId];
  const label =
    (d?.kind === "statement" &&
      (d.title?.[d.original_language ?? "en"]?.text ??
        d.title?.en?.text ??
        d.title?.es?.text)) ||
    selectedId;

  const pinnedD = pathPinnedId ? details[pathPinnedId] : null;
  const pinnedLabel =
    (pinnedD?.kind === "statement" &&
      (pinnedD.title?.[pinnedD.original_language ?? "en"]?.text ??
        pinnedD.title?.en?.text ??
        pinnedD.title?.es?.text)) ||
    pathPinnedId;

  return (
    <div className="space-y-4 rounded-xl border border-slate-200 bg-slate-50 p-3">
      <div>
        <h2 className="mb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
          Explore from
        </h2>
        <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-2.5 py-2">
          {d?.type && (
            <span
              className="inline-block h-2.5 w-2.5 flex-shrink-0 rounded-full"
              style={{ background: TYPE_COLORS[d.type] }}
            />
          )}
          <span className="truncate text-[12px] font-medium text-slate-800">
            {label}
          </span>
        </div>
      </div>

      <div>
        <h3 className="mb-1.5 text-[10px] font-medium text-slate-500">
          View mode
        </h3>
        <div className="flex flex-wrap gap-1">
          {MODES.map(({ mode, label, title }) => (
            <button
              key={mode}
              title={title}
              onClick={() => setExplorationMode(mode)}
              className={clsx(
                "rounded-full border px-2.5 py-1 text-[11px] font-medium transition",
                explorationMode === mode
                  ? "border-blue-500 bg-blue-500 text-white"
                  : "border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50",
              )}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="mb-1.5 text-[10px] font-medium text-slate-500">
          Path highlighting
        </h3>
        {!pathPinnedId ? (
          <button
            onClick={() => pinPath(selectedId)}
            className="w-full rounded-lg border border-amber-300 bg-amber-50 px-3 py-1.5 text-[12px] font-medium text-amber-800 hover:bg-amber-100"
          >
            Pin as path start
          </button>
        ) : (
          <div className="space-y-1.5">
            <div className="flex items-start justify-between gap-2 rounded-lg border border-amber-300 bg-amber-50 px-2.5 py-2">
              <div className="min-w-0">
                <div className="text-[10px] text-amber-700">Pinned start</div>
                <div className="truncate text-[12px] font-medium text-amber-900">
                  {pinnedLabel}
                </div>
              </div>
              <button
                onClick={() => pinPath(null)}
                className="flex-shrink-0 text-[11px] text-amber-600 hover:text-amber-900"
              >
                ✕
              </button>
            </div>
            {selectedId !== pathPinnedId && (
              <div className="rounded-lg border border-green-300 bg-green-50 px-2.5 py-1.5 text-[11px] text-green-800">
                Path: <span className="font-medium">{pinnedLabel}</span>
                {" → "}
                <button
                  className="font-medium underline"
                  onClick={() => select(pathPinnedId)}
                >
                  {label}
                </button>
              </div>
            )}
            {selectedId === pathPinnedId && (
              <p className="text-[11px] text-slate-500">
                Select another node to find the path.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
