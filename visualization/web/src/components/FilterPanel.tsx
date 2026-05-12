import clsx from "clsx";
import { useMemo } from "react";
import { useExplorer } from "../state/store";
import type { GraphPayload, NodeDetailsMap } from "../data/types";
import { TYPE_COLORS, TYPE_LABELS, RELATION_STYLES } from "../theme";

interface Props {
  payload: GraphPayload;
  details: NodeDetailsMap;
}

const ALL_TYPES = Object.keys(TYPE_LABELS) as Array<keyof typeof TYPE_LABELS>;
const ALL_RELATIONS = Object.keys(RELATION_STYLES) as Array<
  keyof typeof RELATION_STYLES
>;

export default function FilterPanel({ payload, details }: Props) {
  const filters = useExplorer((s) => s.filters);
  const toggleType = useExplorer((s) => s.toggleType);
  const toggleRelation = useExplorer((s) => s.toggleRelation);
  const toggleWork = useExplorer((s) => s.toggleWork);
  const toggleStatus = useExplorer((s) => s.toggleStatus);
  const reset = useExplorer((s) => s.resetFilters);

  const allStatuses = useMemo(() => {
    const s = new Set<string>();
    for (const n of payload.nodes) s.add(n.status);
    return [...s].sort();
  }, [payload]);

  const allWorks = useMemo(() => {
    const works = new Set<string>();
    for (const d of Object.values(details)) {
      if (d.kind === "statement" && d.sources) {
        for (const s of d.sources) works.add(s.work);
      }
    }
    return [...works].sort();
  }, [details]);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
          Filters
        </h2>
        <button
          onClick={reset}
          className="text-[11px] text-blue-600 hover:underline"
        >
          reset
        </button>
      </div>

      <div>
        <h3 className="mb-2 text-[11px] font-medium text-slate-700">
          Entity type
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {ALL_TYPES.map((t) => {
            const active = filters.types.has(t);
            return (
              <button
                key={t}
                onClick={() => toggleType(t)}
                className={clsx(
                  "rounded-full border px-2.5 py-1 text-[11px] font-medium transition",
                  active
                    ? "text-white shadow-sm"
                    : "border-slate-200 bg-white text-slate-500 hover:border-slate-300",
                )}
                style={
                  active
                    ? { background: TYPE_COLORS[t], borderColor: TYPE_COLORS[t] }
                    : undefined
                }
              >
                {TYPE_LABELS[t]}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-[11px] font-medium text-slate-700">
          Edge relation
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {ALL_RELATIONS.map((r) => {
            const active = filters.relations.has(r);
            const style = RELATION_STYLES[r];
            return (
              <button
                key={r}
                onClick={() => toggleRelation(r)}
                className={clsx(
                  "rounded-full border px-2.5 py-1 text-[11px] font-medium transition",
                  active
                    ? "text-white"
                    : "border-slate-200 bg-white text-slate-500 hover:border-slate-300",
                )}
                style={
                  active
                    ? { background: style.color, borderColor: style.color }
                    : undefined
                }
              >
                {style.label}
              </button>
            );
          })}
        </div>
      </div>

      {allStatuses.length > 1 && (
        <div>
          <h3 className="mb-2 text-[11px] font-medium text-slate-700">
            Status
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {allStatuses.map((s) => {
              const active =
                filters.status.size === 0 || filters.status.has(s);
              return (
                <button
                  key={s}
                  onClick={() => toggleStatus(s)}
                  className={clsx(
                    "rounded-full border px-2.5 py-1 text-[11px] font-medium transition",
                    active
                      ? "border-slate-700 bg-slate-700 text-white"
                      : "border-slate-200 bg-white text-slate-500 hover:border-slate-300",
                  )}
                >
                  {s}
                </button>
              );
            })}
          </div>
          <p className="mt-1 text-[10px] text-slate-400">
            empty = show all
          </p>
        </div>
      )}

      {allWorks.length > 0 && (
        <div>
          <h3 className="mb-2 text-[11px] font-medium text-slate-700">
            Source / work
          </h3>
          <div className="space-y-1">
            {allWorks.map((w) => {
              const active = filters.works.size === 0 || filters.works.has(w);
              return (
                <button
                  key={w}
                  onClick={() => toggleWork(w)}
                  className={clsx(
                    "flex w-full items-center gap-2 rounded-lg border px-2.5 py-1.5 text-left text-[11px] transition",
                    filters.works.has(w)
                      ? "border-blue-400 bg-blue-50 font-medium text-blue-800"
                      : active
                        ? "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
                        : "border-slate-200 bg-white text-slate-300 line-through",
                  )}
                >
                  <span
                    className={clsx(
                      "inline-block h-2 w-2 flex-shrink-0 rounded-full",
                      filters.works.has(w) ? "bg-blue-500" : "bg-slate-300",
                    )}
                  />
                  <span className="truncate">{w}</span>
                </button>
              );
            })}
          </div>
          {filters.works.size > 0 && (
            <p className="mt-1 text-[10px] text-slate-400">
              showing nodes from selected works
            </p>
          )}
        </div>
      )}
    </div>
  );
}
