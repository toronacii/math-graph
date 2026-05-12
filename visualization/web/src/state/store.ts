// Zustand store for explorer UI state.
//
// The graph itself (graphology instance + node-details map) lives in
// React state inside <App />; this store carries the lightweight
// interaction state shared across components (selection, filters,
// search, hover).

import { create } from "zustand";
import type { EdgeRelation, EntityType } from "../data/types";

export interface Filters {
  types: Set<EntityType>;
  relations: Set<EdgeRelation>;
  works: Set<string>;
  status: Set<string>;
}

interface ExplorerState {
  selectedId: string | null;
  hoveredId: string | null;
  searchQuery: string;
  filters: Filters;
  layoutTick: number;

  select: (id: string | null) => void;
  hover: (id: string | null) => void;
  setSearch: (q: string) => void;
  toggleType: (t: EntityType) => void;
  toggleRelation: (r: EdgeRelation) => void;
  toggleWork: (w: string) => void;
  toggleStatus: (s: string) => void;
  resetFilters: () => void;
  bumpLayout: () => void;
}

const ALL_TYPES: EntityType[] = [
  "definition",
  "proposition",
  "theorem",
  "lemma",
  "corollary",
  "axiom",
  "conjecture",
  "proof",
];

const ALL_RELATIONS: EdgeRelation[] = ["uses", "proves", "depends_on"];

const initialFilters = (): Filters => ({
  types: new Set(ALL_TYPES),
  relations: new Set(ALL_RELATIONS),
  works: new Set(),
  status: new Set(),
});

const toggle = <T>(set: Set<T>, value: T): Set<T> => {
  const next = new Set(set);
  if (next.has(value)) next.delete(value);
  else next.add(value);
  return next;
};

export const useExplorer = create<ExplorerState>((set) => ({
  selectedId: null,
  hoveredId: null,
  searchQuery: "",
  filters: initialFilters(),
  layoutTick: 0,
  select: (id) => set({ selectedId: id }),
  hover: (id) => set({ hoveredId: id }),
  setSearch: (q) => set({ searchQuery: q }),
  toggleType: (t) =>
    set((s) => ({ filters: { ...s.filters, types: toggle(s.filters.types, t) } })),
  toggleRelation: (r) =>
    set((s) => ({
      filters: { ...s.filters, relations: toggle(s.filters.relations, r) },
    })),
  toggleWork: (w) =>
    set((s) => ({ filters: { ...s.filters, works: toggle(s.filters.works, w) } })),
  toggleStatus: (st) =>
    set((s) => ({
      filters: { ...s.filters, status: toggle(s.filters.status, st) },
    })),
  resetFilters: () => set({ filters: initialFilters() }),
  bumpLayout: () => set((s) => ({ layoutTick: s.layoutTick + 1 })),
}));
