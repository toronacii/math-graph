// Sigma + Graphology canvas (no @react-sigma/core, since it doesn't yet
// support React 19). Mounts a Sigma renderer onto a ref'd <div>, runs
// ForceAtlas2 layout once at boot, and wires node/edge reducers to the
// Zustand explorer state (filters, search, selection, hover).

import { useEffect, useMemo, useRef } from "react";
import Sigma from "sigma";
import forceAtlas2 from "graphology-layout-forceatlas2";
import type { MultiDirectedGraph } from "graphology";

import { useExplorer } from "../state/store";
import type { EdgeRelation, EntityType, NodeDetailsMap } from "../data/types";

interface Props {
  graph: MultiDirectedGraph;
  details: NodeDetailsMap;
}

const DIM = "#e2e8f0";

const matchesSearch = (
  id: string,
  details: NodeDetailsMap,
  q: string,
): boolean => {
  if (!q) return true;
  const needle = q.toLowerCase();
  if (id.toLowerCase().includes(needle)) return true;
  const d = details[id];
  if (!d) return false;
  if (d.kind === "statement") {
    if (d.title) {
      for (const v of Object.values(d.title))
        if (v.text.toLowerCase().includes(needle)) return true;
    }
    if (d.natural) {
      for (const v of Object.values(d.natural))
        if (v.text.toLowerCase().includes(needle)) return true;
    }
    if (d.sources) {
      for (const s of d.sources) {
        if (
          s.work.toLowerCase().includes(needle) ||
          s.theorem_label?.toLowerCase().includes(needle) ||
          s.locator?.toLowerCase().includes(needle)
        )
          return true;
      }
    }
  }
  return false;
};

export default function GraphCanvas({ graph, details }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const sigmaRef = useRef<Sigma | null>(null);

  const selectedId = useExplorer((s) => s.selectedId);
  const hoveredId = useExplorer((s) => s.hoveredId);
  const searchQuery = useExplorer((s) => s.searchQuery);
  const filters = useExplorer((s) => s.filters);
  const layoutTick = useExplorer((s) => s.layoutTick);
  const select = useExplorer((s) => s.select);
  const hover = useExplorer((s) => s.hover);

  // Mount Sigma + initial FA2 settle. We intentionally only run on graph
  // change (graph reference is stable for a session).
  useEffect(() => {
    if (!containerRef.current) return;
    const settings = forceAtlas2.inferSettings(graph);
    forceAtlas2.assign(graph, { iterations: 250, settings });

    const renderer = new Sigma(graph, containerRef.current, {
      renderEdgeLabels: false,
      labelDensity: 0.5,
      labelGridCellSize: 80,
      labelRenderedSizeThreshold: 10,
      defaultEdgeType: "arrow",
      zIndex: true,
    });

    renderer.on("clickNode", (e) => select(e.node));
    renderer.on("enterNode", (e) => hover(e.node));
    renderer.on("leaveNode", () => hover(null));
    renderer.on("clickStage", () => select(null));

    sigmaRef.current = renderer;
    return () => {
      renderer.kill();
      sigmaRef.current = null;
    };
  }, [graph, select, hover]);

  // Manual relayout trigger.
  useEffect(() => {
    if (layoutTick === 0 || !sigmaRef.current) return;
    const settings = forceAtlas2.inferSettings(graph);
    forceAtlas2.assign(graph, { iterations: 150, settings });
    sigmaRef.current.refresh();
  }, [layoutTick, graph]);

  const highlighted = useMemo(() => {
    if (!selectedId) return null;
    const set = new Set<string>([selectedId]);
    if (graph.hasNode(selectedId)) {
      graph.forEachNeighbor(selectedId, (n) => set.add(n));
    }
    return set;
  }, [graph, selectedId]);

  // Update reducers whenever interaction state changes.
  useEffect(() => {
    const sigma = sigmaRef.current;
    if (!sigma) return;

    sigma.setSetting("nodeReducer", (id, attrs) => {
      const out: Record<string, unknown> = { ...attrs };
      const t = (attrs.entity_type ?? attrs.type) as EntityType;
      const visibleByType = filters.types.has(t);
      const visibleByStatus =
        filters.status.size === 0 ||
        filters.status.has(attrs.status as string);
      if (!visibleByType || !visibleByStatus) {
        out.hidden = true;
        return out;
      }
      const matches = matchesSearch(id, details, searchQuery);
      if (searchQuery && !matches) {
        out.color = DIM;
        out.label = "";
      }
      if (highlighted) {
        if (!highlighted.has(id)) {
          out.color = DIM;
          out.label = "";
        } else {
          out.zIndex = 2;
          out.size = (attrs.size as number) * 1.4;
          out.forceLabel = true;
        }
      }
      if (hoveredId === id) {
        out.size = (attrs.size as number) * 1.5;
        out.forceLabel = true;
      }
      return out;
    });

    sigma.setSetting("edgeReducer", (id, attrs) => {
      const out: Record<string, unknown> = { ...attrs };
      const rel = attrs.relation as EdgeRelation;
      if (!filters.relations.has(rel)) {
        out.hidden = true;
        return out;
      }
      if (highlighted) {
        const [u, v] = graph.extremities(id);
        if (!highlighted.has(u) || !highlighted.has(v)) {
          out.color = DIM;
          out.size = 0.5;
        } else {
          out.size = (attrs.size as number) + 0.6;
          out.zIndex = 2;
        }
      }
      return out;
    });

    sigma.refresh();
  }, [filters, searchQuery, highlighted, hoveredId, details, graph]);

  return <div ref={containerRef} className="absolute inset-0 bg-white" />;
}
