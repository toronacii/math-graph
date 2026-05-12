// Debounced search across id, all-language titles, natural text and
// source theorem labels. Pressing Enter or clicking a result selects
// the node, which the GraphCanvas then focuses.

import { useEffect, useMemo, useRef, useState } from "react";
import { useExplorer } from "../state/store";
import type { NodeDetailsMap } from "../data/types";
import { TYPE_COLORS } from "../theme";

interface Props {
  details: NodeDetailsMap;
}

interface Hit {
  id: string;
  label: string;
  hint: string;
  type?: string;
}

const DEBOUNCE_MS = 150;
const MAX_RESULTS = 20;

const buildIndex = (details: NodeDetailsMap): Hit[] => {
  const out: Hit[] = [];
  for (const [id, d] of Object.entries(details)) {
    let label: string = id;
    let hint: string = d.kind;
    if (d.kind === "statement") {
      const orig = d.original_language ?? "en";
      label = d.title?.[orig]?.text ?? d.title?.en?.text ?? id;
      hint = d.type;
    } else if (d.kind === "proof") {
      label = d.id;
      hint = `proof of ${d.proves}`;
    }
    out.push({ id, label, hint, type: d.type });
  }
  return out;
};

const score = (hit: Hit, q: string, details: NodeDetailsMap): number => {
  const n = q.toLowerCase();
  if (hit.id.toLowerCase().includes(n)) return 3;
  if (hit.label.toLowerCase().includes(n)) return 2;
  const d = details[hit.id];
  if (d?.kind === "statement") {
    if (d.natural) {
      for (const v of Object.values(d.natural))
        if (v.text.toLowerCase().includes(n)) return 1;
    }
    if (d.sources) {
      for (const s of d.sources) {
        if (s.theorem_label?.toLowerCase().includes(n)) return 1;
        if (s.work.toLowerCase().includes(n)) return 1;
      }
    }
  }
  return 0;
};

export default function SearchBox({ details }: Props) {
  const search = useExplorer((s) => s.searchQuery);
  const setSearch = useExplorer((s) => s.setSearch);
  const select = useExplorer((s) => s.select);

  const [draft, setDraft] = useState(search);
  const [open, setOpen] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setSearch(draft), DEBOUNCE_MS);
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [draft, setSearch]);

  const index = useMemo(() => buildIndex(details), [details]);

  const results = useMemo(() => {
    if (!draft.trim()) return [];
    const scored = index
      .map((h) => ({ hit: h, s: score(h, draft, details) }))
      .filter((x) => x.s > 0)
      .sort((a, b) => b.s - a.s)
      .slice(0, MAX_RESULTS);
    return scored.map((x) => x.hit);
  }, [draft, index, details]);

  return (
    <div className="relative">
      <input
        type="search"
        placeholder="Search id, title, statement, source…"
        value={draft}
        onChange={(e) => {
          setDraft(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 120)}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-[13px] outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
      />
      {open && results.length > 0 && (
        <ul className="absolute z-30 mt-1 max-h-80 w-full overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg">
          {results.map((r) => (
            <li key={r.id}>
              <button
                onMouseDown={(e) => {
                  e.preventDefault();
                  select(r.id);
                  setDraft("");
                  setSearch("");
                  setOpen(false);
                }}
                className="flex w-full items-start gap-2 px-3 py-2 text-left hover:bg-slate-50"
              >
                {r.type && (
                  <span
                    className="mt-1 inline-block h-2.5 w-2.5 flex-shrink-0 rounded-full"
                    style={{
                      background:
                        TYPE_COLORS[r.type as keyof typeof TYPE_COLORS] ??
                        "#94a3b8",
                    }}
                  />
                )}
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[13px] font-medium text-slate-800">
                    {r.label}
                  </div>
                  <div className="truncate text-[10px] text-slate-500">
                    {r.id} · {r.hint}
                  </div>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
