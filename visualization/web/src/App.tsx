import { useState, useEffect, useMemo, useCallback, useDeferredValue, useRef } from "react";
import type { GraphData, EntityType, NodeDetailsIndex } from "./types";
import CytoscapeGraph from "./components/CytoscapeGraph";
import DetailsPanel from "./components/DetailsPanel";
import FilterBar from "./components/FilterBar";
import StatsBar from "./components/StatsBar";
import { UI_TEXT, type Locale } from "./i18n";
import {
  buildGraphMetrics,
  type BoundaryFilter,
  type LabelMode,
  type LayoutMode,
  getSelectionContext,
  formatNodeLabel,
} from "./graphAnalysis";

const ALL_ENTITY_TYPES: EntityType[] = [
  "axiom", "definition", "lemma", "proposition",
  "theorem", "corollary", "conjecture", "proof",
];

interface GraphViewApi {
  exportPng: () => void;
  exportSvg: () => void;
}

export default function App() {
  const [data, setData] = useState<GraphData | null>(null);
  const [nodeDetails, setNodeDetails] = useState<NodeDetailsIndex | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [visibleTypes, setVisibleTypes] = useState<Set<EntityType>>(
    () => new Set(ALL_ENTITY_TYPES),
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [boundaryFilter, setBoundaryFilter] = useState<BoundaryFilter>("all");
  const [layoutMode, setLayoutMode] = useState<LayoutMode>("breadthfirst");
  const [labelMode, setLabelMode] = useState<LabelMode>("title");
  const [locale, setLocale] = useState<Locale>("es");
  const graphApiRef = useRef<GraphViewApi | null>(null);
  const deferredSearchQuery = useDeferredValue(searchQuery);
  const text = UI_TEXT[locale];

  useEffect(() => {
    Promise.all([
      fetch("/graph.json").then((r) => {
        if (!r.ok) throw new Error(`graph.json HTTP ${r.status}`);
        return r.json() as Promise<GraphData>;
      }),
      fetch("/node-details.json").then((r) => {
        if (!r.ok) throw new Error(`node-details.json HTTP ${r.status}`);
        return r.json() as Promise<NodeDetailsIndex>;
      }),
    ])
      .then(([graphData, detailsData]) => {
        setData(graphData);
        setNodeDetails(detailsData);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  const metrics = useMemo(() => (data ? buildGraphMetrics(data) : null), [data]);

  const typeCounts = useMemo(() => {
    const counts: Record<EntityType, number> = {} as Record<EntityType, number>;
    for (const t of ALL_ENTITY_TYPES) counts[t] = 0;
    if (data) {
      for (const n of data.nodes) counts[n.type] = (counts[n.type] ?? 0) + 1;
    }
    return counts;
  }, [data]);

  const handleToggleType = useCallback((type: EntityType) => {
    setVisibleTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  }, []);

  const visibleNodeIds = useMemo(() => {
    if (!data || !metrics) return new Set<string>();

    const candidates = data.nodes.filter((node) => {
      if (!visibleTypes.has(node.type)) return false;
      if (boundaryFilter === "roots" && !metrics.roots.has(node.id)) return false;
      if (boundaryFilter === "leaves" && !metrics.leaves.has(node.id)) return false;
      return true;
    });

    return new Set(candidates.map((node) => node.id));
  }, [boundaryFilter, data, metrics, visibleTypes]);

  const visibleStats = useMemo(() => {
    if (!data || !metrics) return null;

    const visibleLinks = data.links.filter(
      (link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target),
    );

    const visibleNodes = data.nodes.filter((node) => visibleNodeIds.has(node.id));
    const visibleCounts: Record<EntityType, number> = {} as Record<EntityType, number>;
    for (const type of ALL_ENTITY_TYPES) visibleCounts[type] = 0;
    for (const node of visibleNodes) visibleCounts[node.type] += 1;

    return {
      visibleNodes: visibleNodes.length,
      visibleEdges: visibleLinks.length,
      visibleTypeCounts: visibleCounts,
      visibleRoots: visibleNodes.filter((node) => metrics.roots.has(node.id)).length,
      visibleLeaves: visibleNodes.filter((node) => metrics.leaves.has(node.id)).length,
    };
  }, [data, metrics, visibleNodeIds]);

  const longestChainPreview = useMemo(() => {
    if (!metrics || metrics.longestChain.length === 0) return null;
    const first = metrics.nodeById.get(metrics.longestChain[0]);
    const last = metrics.nodeById.get(metrics.longestChain.at(-1) ?? "");
    if (!first || !last) return null;

    return {
      length: Math.max(metrics.longestChain.length - 1, 0),
      start: formatNodeLabel(first, "title", locale),
      end: formatNodeLabel(last, "title", locale),
    };
  }, [locale, metrics]);

  const activeSelectionContext = useMemo(
    () => (metrics ? getSelectionContext(selectedNode, metrics) : null),
    [metrics, selectedNode],
  );

  const handleExportSnapshot = useCallback(() => {
    if (!data) return;

    const visibleLinks = data.links.filter(
      (link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target),
    );
    const visibleNodes = data.nodes.filter((node) => visibleNodeIds.has(node.id));

    const payload = {
      exported_at: new Date().toISOString(),
      layout_mode: layoutMode,
      label_mode: labelMode,
      locale,
      boundary_filter: boundaryFilter,
      search_query: deferredSearchQuery,
      visible_types: [...visibleTypes],
      selected_node: selectedNode,
      visible_nodes: visibleNodes,
      visible_links: visibleLinks,
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "mkg-graph-snapshot.json";
    anchor.click();
    URL.revokeObjectURL(url);
  }, [
    boundaryFilter,
    data,
    deferredSearchQuery,
    labelMode,
    locale,
    layoutMode,
    selectedNode,
    visibleNodeIds,
    visibleTypes,
  ]);

  if (error) {
    return (
      <div className="app-error">
        <h1>{text.loadErrorTitle}</h1>
        <p>{error}</p>
        <p>{text.loadErrorHint}</p>
      </div>
    );
  }

  if (!data || !nodeDetails) {
    return <div className="app-loading">{text.loading}</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="app-kicker">{text.appKicker}</p>
          <h1>{text.appTitle}</h1>
        </div>
        {metrics && visibleStats && (
          <StatsBar
            data={data}
            metrics={metrics}
            visibleStats={visibleStats}
            typeCounts={typeCounts}
            longestChainPreview={longestChainPreview}
            locale={locale}
          />
        )}
      </header>

      <FilterBar
        visibleTypes={visibleTypes}
        onToggleType={handleToggleType}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        typeCounts={typeCounts}
        locale={locale}
        onLocaleChange={setLocale}
        boundaryFilter={boundaryFilter}
        onBoundaryFilterChange={setBoundaryFilter}
        layoutMode={layoutMode}
        onLayoutModeChange={setLayoutMode}
        labelMode={labelMode}
        onLabelModeChange={setLabelMode}
        onExportPng={() => graphApiRef.current?.exportPng()}
        onExportSvg={() => graphApiRef.current?.exportSvg()}
        onExportSnapshot={handleExportSnapshot}
      />

      <div className="app-main">
        <div className={`graph-container ${selectedNode ? "with-panel" : ""}`}>
          <CytoscapeGraph
            data={data}
            metrics={metrics!}
            visibleTypes={visibleTypes}
            visibleNodeIds={visibleNodeIds}
            searchQuery={deferredSearchQuery}
            selectedNode={selectedNode}
            selectionContext={activeSelectionContext}
            layoutMode={layoutMode}
            labelMode={labelMode}
            locale={locale}
            onSelectNode={setSelectedNode}
            onRegisterApi={(api) => {
              graphApiRef.current = api;
            }}
          />
        </div>

        {metrics && (
          <DetailsPanel
            data={data}
            detailsIndex={nodeDetails}
            metrics={metrics}
            selectionContext={activeSelectionContext}
            nodeId={selectedNode}
            locale={locale}
            onClose={() => setSelectedNode(null)}
            onSelectNode={setSelectedNode}
          />
        )}
      </div>
    </div>
  );
}
