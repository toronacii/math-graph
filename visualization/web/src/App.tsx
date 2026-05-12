// MKG Graph Explorer — root layout.
//
//  ┌──── Top bar (StatsBar) ──────────────────────────────────────┐
//  │ Left          │   Sigma canvas      │ Right                  │
//  │ Search +      │                     │ DetailsPanel           │
//  │ FilterPanel   │                     │                        │
//  └───────────────┴─────────────────────┴────────────────────────┘

import { useEffect, useState } from "react";
import { loadGraph, type LoadedGraph } from "./data/loadGraph";
import GraphCanvas from "./components/GraphCanvas";
import DetailsPanel from "./components/DetailsPanel";
import FilterPanel from "./components/FilterPanel";
import SearchBox from "./components/SearchBox";
import StatsBar from "./components/StatsBar";
import { useExplorer } from "./state/store";

export default function App() {
  const [loaded, setLoaded] = useState<LoadedGraph | null>(null);
  const [error, setError] = useState<string | null>(null);
  const bumpLayout = useExplorer((s) => s.bumpLayout);

  useEffect(() => {
    loadGraph()
      .then(setLoaded)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 p-8 text-center">
        <h1 className="text-lg font-semibold text-rose-600">
          Failed to load the graph
        </h1>
        <p className="max-w-md text-sm text-slate-600">{error}</p>
        <p className="text-xs text-slate-500">
          From the repo root, run{" "}
          <code className="rounded bg-slate-100 px-1.5 py-0.5">
            python -m scripts.v03.build_db
          </code>{" "}
          and then{" "}
          <code className="rounded bg-slate-100 px-1.5 py-0.5">
            npm run sync
          </code>
          .
        </p>
      </div>
    );
  }

  if (!loaded) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-slate-500">
        Loading graph…
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 bg-white px-5 py-3">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
            Mathematical Knowledge Graph
          </p>
          <h1 className="font-serif text-lg leading-tight text-slate-900">
            MKG Explorer
          </h1>
        </div>
        <StatsBar payload={loaded.payload} />
        <button
          onClick={bumpLayout}
          className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-[12px] text-slate-700 hover:bg-slate-50"
        >
          Re-run layout
        </button>
      </header>

      <main className="flex flex-1 min-h-0">
        <aside className="w-72 flex-shrink-0 overflow-y-auto border-r border-slate-200 bg-white p-4">
          <div className="mb-4">
            <SearchBox details={loaded.details} />
          </div>
          <FilterPanel payload={loaded.payload} />
        </aside>

        <section className="relative flex-1 min-w-0">
          <GraphCanvas graph={loaded.graph} details={loaded.details} />
        </section>

        <aside className="w-96 flex-shrink-0 overflow-hidden border-l border-slate-200 bg-white">
          <DetailsPanel details={loaded.details} />
        </aside>
      </main>
    </div>
  );
}
