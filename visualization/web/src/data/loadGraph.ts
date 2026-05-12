// Loads graph.json + node-details.json from /public and builds a
// graphology MultiDirectedGraph with random initial positions.
//
// Node attrs include the v0.3.1 summary fields (primary_domain,
// semantic_kinds, latex_status, quality_overall) plus visual attrs
// (label, color, size, x, y) consumed by Sigma.

import { MultiDirectedGraph } from "graphology";
import type {
  EdgeRelation,
  GraphNode,
  GraphPayload,
  NodeDetailsMap,
} from "./types";
import { TYPE_COLORS, RELATION_STYLES } from "../theme";

export interface LoadedGraph {
  graph: MultiDirectedGraph;
  details: NodeDetailsMap;
  payload: GraphPayload;
}

const labelOf = (id: string, details: NodeDetailsMap): string => {
  const d = details[id];
  if (d?.kind === "statement") {
    const title = d.title;
    if (title) {
      const lang = d.original_language ?? "en";
      const orig = title[lang] ?? title.en ?? title.es;
      if (orig?.text) return orig.text;
    }
  } else if (d?.kind === "proof") {
    return d.id;
  }
  return id;
};

export async function loadGraph(): Promise<LoadedGraph> {
  const [graphRes, detailsRes] = await Promise.all([
    fetch("graph.json", { cache: "no-cache" }),
    fetch("node-details.json", { cache: "no-cache" }),
  ]);
  if (!graphRes.ok || !detailsRes.ok) {
    throw new Error(
      `Failed to fetch graph data (graph.json=${graphRes.status}, ` +
        `node-details.json=${detailsRes.status}). ` +
        `Did you run \`npm run sync\`?`,
    );
  }
  const payload = (await graphRes.json()) as GraphPayload;
  const details = (await detailsRes.json()) as NodeDetailsMap;

  const graph = new MultiDirectedGraph();

  // Random initial layout in a unit square; ForceAtlas2 will refine.
  for (const n of payload.nodes) {
    const color = TYPE_COLORS[n.type] ?? "#94a3b8";
    const isProof = n.kind === "proof";
    graph.addNode(n.id, {
      ...(n as Partial<GraphNode>),
      label: labelOf(n.id, details),
      color,
      // Proofs render smaller; all nodes use "circle" (Sigma 3 default program).
      // Visual distinction between proof and statement is via color + size.
      size: isProof ? 4 : 6,
      type: "circle",
      // duplicate v0.3 entity type under a different key so it isn't
      // shadowed by Sigma's node-program "type" attribute.
      entity_type: n.type,
      x: Math.random(),
      y: Math.random(),
    });
  }

  for (const l of payload.links) {
    const style = RELATION_STYLES[l.relation as EdgeRelation];
    graph.addEdge(l.source, l.target, {
      relation: l.relation,
      role: l.role,
      confidence: l.confidence,
      implicit: l.implicit,
      color: style.color,
      size: style.size,
      // Sigma edge program: line by default; dashed handled via reducer.
      type: l.implicit ? "line" : "line",
    });
  }

  return { graph, details, payload };
}
