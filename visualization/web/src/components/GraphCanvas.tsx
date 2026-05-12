import { useEffect, useMemo, useRef } from "react";
import Sigma from "sigma";
import forceAtlas2 from "graphology-layout-forceatlas2";
import { bfsFromNode } from "graphology-traversal";
import { bidirectional } from "graphology-shortest-path/unweighted";
import type { MultiDirectedGraph } from "graphology";

import { useExplorer } from "../state/store";
import type { EdgeRelation, EntityType, NodeDetailsMap } from "../data/types";

interface Props {
  graph: MultiDirectedGraph;
  details: NodeDetailsMap;
}

const DIM = "#e2e8f0";
const DIM_EDGE = "#f1f5f9";

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

// Build a set of node IDs that match the work filter.
const buildWorkNodeSet = (
  details: NodeDetailsMap,
  works: Set<string>,
): Set<string> | null => {
  if (works.size === 0) return null;
  const set = new Set<string>();
  for (const [id, d] of Object.entries(details)) {
    if (d.kind === "statement" && d.sources) {
      for (const s of d.sources) {
        if (works.has(s.work)) {
          set.add(id);
          break;
        }
      }
    }
  }
  return set;
};

export default function GraphCanvas({ graph, details }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const sigmaRef = useRef<Sigma | null>(null);

  const selectedId = useExplorer((s) => s.selectedId);
  const hoveredId = useExplorer((s) => s.hoveredId);
  const searchQuery = useExplorer((s) => s.searchQuery);
  const filters = useExplorer((s) => s.filters);
  const layoutTick = useExplorer((s) => s.layoutTick);
  const explorationMode = useExplorer((s) => s.explorationMode);
  const pathPinnedId = useExplorer((s) => s.pathPinnedId);
  const select = useExplorer((s) => s.select);
  const hover = useExplorer((s) => s.hover);
  const setVisibleCount = useExplorer((s) => s.setVisibleCount);

  // Mount Sigma + initial FA2 settle.
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
      allowInvalidContainer: true,
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

  // Camera pan to selected node using Sigma's display coordinate space.
  // getNodeDisplayData returns x,y in the same framed space as the camera —
  // using raw graphology coordinates would send the camera off-screen.
  useEffect(() => {
    if (!selectedId || !sigmaRef.current) return;
    const sigma = sigmaRef.current;
    const displayData = sigma.getNodeDisplayData(selectedId);
    if (!displayData) return;
    sigma.getCamera().animate(
      { x: displayData.x, y: displayData.y },
      { duration: 400 },
    );
  }, [selectedId, graph]);

  // Highlighted neighborhood of selected node.
  const highlighted = useMemo(() => {
    if (!selectedId) return null;
    const set = new Set<string>([selectedId]);
    if (graph.hasNode(selectedId)) {
      graph.forEachNeighbor(selectedId, (n) => set.add(n));
    }
    return set;
  }, [graph, selectedId]);

  // Exploration set: nodes visible in the current exploration mode.
  const explorationSet = useMemo((): Set<string> | null => {
    if (!selectedId || explorationMode === "full") return null;

    const set = new Set<string>([selectedId]);

    if (explorationMode === "neighborhood") {
      graph.forEachNeighbor(selectedId, (n) => set.add(n));
      return set;
    }

    if (explorationMode === "ancestors") {
      // Follow outgoing edges: what this node depends on.
      bfsFromNode(graph, selectedId, (n) => { set.add(n); }, { mode: "outbound" });
      return set;
    }

    if (explorationMode === "descendants") {
      // Follow incoming edges: what depends on this.
      bfsFromNode(graph, selectedId, (n) => { set.add(n); }, { mode: "inbound" });
      return set;
    }

    if (explorationMode === "proof-neighborhood") {
      graph.forEachEdge(selectedId, (_e, attrs, source, target) => {
        const rel = attrs.relation as EdgeRelation;
        if (rel === "proves" || rel === "uses") {
          set.add(source === selectedId ? target : source);
        }
      });
      return set;
    }

    if (explorationMode === "conceptual-neighborhood") {
      graph.forEachEdge(selectedId, (_e, attrs, source, target) => {
        if (attrs.relation === "depends_on") {
          set.add(source === selectedId ? target : source);
        }
      });
      return set;
    }

    return set;
  }, [graph, selectedId, explorationMode]);

  // Shortest path between selectedId and pathPinnedId.
  const pathSet = useMemo((): Set<string> | null => {
    if (!selectedId || !pathPinnedId || selectedId === pathPinnedId) return null;
    try {
      const path = bidirectional(graph, selectedId, pathPinnedId);
      if (!path) return null;
      return new Set(path);
    } catch {
      return null;
    }
  }, [graph, selectedId, pathPinnedId]);

  // Work filter node set.
  const workNodeSet = useMemo(
    () => buildWorkNodeSet(details, filters.works),
    [details, filters.works],
  );

  // Update reducers whenever interaction state changes.
  useEffect(() => {
    const sigma = sigmaRef.current;
    if (!sigma) return;

    sigma.setSetting("nodeReducer", (id, attrs) => {
      const out: Record<string, unknown> = { ...attrs };
      const t = (attrs.entity_type ?? attrs.type) as EntityType;

      const visibleByType = filters.types.has(t);
      const visibleByStatus =
        filters.status.size === 0 || filters.status.has(attrs.status as string);
      const visibleByWork = workNodeSet === null || workNodeSet.has(id);

      if (!visibleByType || !visibleByStatus || !visibleByWork) {
        out.hidden = true;
        return out;
      }

      // Exploration mode: dim nodes outside the exploration set.
      if (explorationSet && !explorationSet.has(id)) {
        out.color = DIM;
        out.label = "";
        out.size = (attrs.size as number) * 0.6;
        return out;
      }

      // Path mode: highlight nodes on the path.
      if (pathSet) {
        if (!pathSet.has(id)) {
          out.color = DIM;
          out.label = "";
        } else {
          out.color = id === selectedId || id === pathPinnedId
            ? "#f59e0b"
            : "#2f9e44";
          out.zIndex = 3;
          out.size = (attrs.size as number) * 1.6;
          out.forceLabel = true;
        }
      }

      const matches = matchesSearch(id, details, searchQuery);
      if (searchQuery && !matches) {
        out.color = DIM;
        out.label = "";
      }

      if (!pathSet && !explorationSet) {
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
      } else if (explorationSet && explorationSet.has(id)) {
        if (id === selectedId) {
          out.zIndex = 3;
          out.size = (attrs.size as number) * 1.6;
          out.forceLabel = true;
        } else {
          out.zIndex = 2;
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

      const [u, v] = graph.extremities(id);

      // Dim edges whose endpoints are outside exploration set.
      if (explorationSet && (!explorationSet.has(u) || !explorationSet.has(v))) {
        out.color = DIM_EDGE;
        out.size = 0.3;
        return out;
      }

      // Path edges: highlight edges between path nodes.
      if (pathSet) {
        if (pathSet.has(u) && pathSet.has(v)) {
          out.color = "#f59e0b";
          out.size = (attrs.size as number) + 1.5;
          out.zIndex = 3;
        } else {
          out.color = DIM_EDGE;
          out.size = 0.3;
        }
        return out;
      }

      if (highlighted) {
        if (!highlighted.has(u) || !highlighted.has(v)) {
          out.color = DIM_EDGE;
          out.size = 0.5;
        } else {
          out.size = (attrs.size as number) + 0.6;
          out.zIndex = 2;
        }
      }

      return out;
    });

    sigma.refresh();
    // Count "focused" nodes: those that are not hidden AND not dimmed by exploration/path/highlight.
    // We count after refresh so nodeDataCache is current.
    // Counting inside the reducer closure would double-count because setSetting triggers
    // its own internal refresh pass before the explicit refresh() call.
    let visible = 0;
    const focusSet = explorationSet ?? pathSet ?? (highlighted ?? null);
    graph.forEachNode((id) => {
      const d = sigma.getNodeDisplayData(id);
      if (!d || d.hidden) return;
      if (focusSet && !focusSet.has(id)) return;
      if (searchQuery && !matchesSearch(id, details, searchQuery)) return;
      visible++;
    });
    setVisibleCount(visible);
  }, [
    filters,
    searchQuery,
    highlighted,
    hoveredId,
    details,
    graph,
    explorationSet,
    pathSet,
    pathPinnedId,
    selectedId,
    workNodeSet,
    setVisibleCount,
  ]);

  return <div ref={containerRef} className="absolute inset-0 bg-white" />;
}
