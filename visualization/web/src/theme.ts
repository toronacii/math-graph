// Color palette + relation/edge styles for the graph explorer.
// Kept in one file so visual tweaks are contained.

import type { EdgeRelation, EntityType } from "./data/types";

// Saturated, distinct hues for the 8 entity types.
export const TYPE_COLORS: Record<EntityType, string> = {
  definition: "#2f6fdb",
  proposition: "#e67e22",
  theorem: "#2f9e44",
  lemma: "#d4a017",
  corollary: "#17a2b8",
  axiom: "#d94841",
  conjecture: "#7c4dff",
  proof: "#7b8794",
};

export const TYPE_LABELS: Record<EntityType, string> = {
  definition: "Definition",
  proposition: "Proposition",
  theorem: "Theorem",
  lemma: "Lemma",
  corollary: "Corollary",
  axiom: "Axiom",
  conjecture: "Conjecture",
  proof: "Proof",
};

export const RELATION_STYLES: Record<
  EdgeRelation,
  { color: string; size: number; label: string }
> = {
  proves: { color: "#2f9e44", size: 2.2, label: "proves" },
  uses: { color: "#94a3b8", size: 1.4, label: "uses" },
  depends_on: { color: "#7c4dff", size: 1.0, label: "depends_on" },
};

export const CONFIDENCE_COLORS: Record<string, string> = {
  high: "#2f9e44",
  medium: "#d4a017",
  low: "#d94841",
};
