import { create } from "zustand";
import type { EdgeRelation, EntityType } from "../data/types";

export interface Filters {
  types: Set<EntityType>;
  relations: Set<EdgeRelation>;
  works: Set<string>;
  status: Set<string>;
}

export type ExplorationMode =
  | "full"
  | "neighborhood"
  | "ancestors"
  | "descendants"
  | "proof-neighborhood"
  | "conceptual-neighborhood";

interface ExplorerState {
  selectedId: string | null;
  hoveredId: string | null;
  searchQuery: string;
  filters: Filters;
  layoutTick: number;
  explorationMode: ExplorationMode;
  pathPinnedId: string | null;
  visibleCount: number;

  select: (id: string | null) => void;
  hover: (id: string | null) => void;
  setSearch: (q: string) => void;
  toggleType: (t: EntityType) => void;
  toggleRelation: (r: EdgeRelation) => void;
  toggleWork: (w: string) => void;
  toggleStatus: (s: string) => void;
  resetFilters: () => void;
  bumpLayout: () => void;
  setExplorationMode: (mode: ExplorationMode) => void;
  pinPath: (id: string | null) => void;
  setVisibleCount: (n: number) => void;
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
  explorationMode: "full",
  pathPinnedId: null,
  visibleCount: 0,
  select: (id) => set({ selectedId: id, explorationMode: "full" }),
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
  setExplorationMode: (mode) => set({ explorationMode: mode }),
  pinPath: (id) => set({ pathPinnedId: id }),
  setVisibleCount: (n) => set({ visibleCount: n }),
}));
