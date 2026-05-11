import { useEffect, useEffectEvent, useMemo, useRef, useState } from "react";
import cytoscape, {
  type Core,
  type EventObject,
  type LayoutOptions,
  type NodeSingular,
  type StylesheetStyle,
} from "cytoscape";
import coseBilkent from "cytoscape-cose-bilkent";
import cytoscapeDagre from "cytoscape-dagre";
import dagreLib from "dagre";
import svg from "cytoscape-svg";
import type { GraphData, EntityType, GraphNode } from "../types";
import { TYPE_COLORS } from "../constants";
import { getTypeLabel, type Locale } from "../i18n";
import {
  formatNodeLabel,
  type GraphMetrics,
  type LabelMode,
  type LayoutMode,
  type SelectionContext,
} from "../graphAnalysis";

cytoscape.use(coseBilkent);
cytoscape.use(cytoscapeDagre);
cytoscape.use(svg);

interface Props {
  data: GraphData;
  metrics: GraphMetrics;
  visibleTypes: Set<EntityType>;
  visibleNodeIds: Set<string>;
  searchQuery: string;
  selectedNode: string | null;
  selectionContext: SelectionContext | null;
  layoutMode: LayoutMode;
  labelMode: LabelMode;
  locale: Locale;
  onSelectNode: (nodeId: string | null) => void;
  onRegisterApi: (api: { exportPng: () => void; exportSvg: () => void } | null) => void;
}

interface HoveredNode {
  id: string;
  label: string;
  type: string;
  x: number;
  y: number;
}

type SvgCapableCore = Core & {
  svg: (options?: { full?: boolean; scale?: number; bg?: string }) => string;
};

type PresetPositions = Record<string, { x: number; y: number }>;

function downloadFile(href: string, filename: string) {
  const anchor = document.createElement("a");
  anchor.href = href;
  anchor.download = filename;
  anchor.click();
}

function buildElements(data: GraphData, labelMode: LabelMode, locale: Locale) {
  const nodes = data.nodes.map((node) => ({
    data: {
      ...node,
      label: formatNodeLabel(node, labelMode, locale),
    },
  }));

  const edges = data.links.map((link, index) => ({
    data: {
      id: `e${index}`,
      source: link.source,
      target: link.target,
      relation: link.relation,
    },
  }));

  return [...nodes, ...edges];
}

function estimateNodeDimensions(node: GraphNode, labelMode: LabelMode, locale: Locale) {
  const label = formatNodeLabel(node, labelMode, locale);
  const baseWidth = node.kind === "proof" ? 72 : 124;
  const extraWidth = Math.min(label.length * 4.2, 110);
  const width = baseWidth + extraWidth;
  const height = node.kind === "proof" ? 52 : 74;
  return { width, height };
}

function buildComponentPresetPositions(
  data: GraphData,
  metrics: GraphMetrics,
  visibleNodeIds: Set<string>,
  labelMode: LabelMode,
  locale: Locale,
) {
  const visibleComponents = metrics.components
    .map((component) => component.filter((nodeId) => visibleNodeIds.has(nodeId)))
    .filter((component) => component.length > 0);

  const componentLayouts = visibleComponents.map((component) => {
    const graph = new dagreLib.graphlib.Graph();
    graph.setGraph({
      rankdir: "LR",
      ranksep: 120,
      nodesep: 58,
      edgesep: 24,
    });
    graph.setDefaultEdgeLabel(() => ({}));

    for (const nodeId of component) {
      const node = metrics.nodeById.get(nodeId);
      if (!node) continue;
      graph.setNode(nodeId, estimateNodeDimensions(node, labelMode, locale));
    }

    for (const link of data.links) {
      if (!visibleNodeIds.has(link.source) || !visibleNodeIds.has(link.target)) continue;
      if (!component.includes(link.source) || !component.includes(link.target)) continue;
      graph.setEdge(link.source, link.target);
    }

    dagreLib.layout(graph);

    const nodes = component.map((nodeId) => {
      const position = graph.node(nodeId) ?? { x: 0, y: 0 };
      return { id: nodeId, x: position.x, y: position.y };
    });

    const minX = Math.min(...nodes.map((node) => node.x), 0);
    const minY = Math.min(...nodes.map((node) => node.y), 0);
    const maxX = Math.max(...nodes.map((node) => node.x), 0);
    const maxY = Math.max(...nodes.map((node) => node.y), 0);

    return {
      nodes,
      width: maxX - minX,
      height: maxY - minY,
      minX,
      minY,
    };
  });

  const columns = Math.max(1, Math.ceil(Math.sqrt(componentLayouts.length)));
  const cellWidth = Math.max(...componentLayouts.map((layout) => layout.width), 260) + 180;
  const cellHeight = Math.max(...componentLayouts.map((layout) => layout.height), 180) + 180;
  const positions: PresetPositions = {};

  componentLayouts.forEach((layout, index) => {
    const column = index % columns;
    const row = Math.floor(index / columns);
    const offsetX = column * cellWidth + 120;
    const offsetY = row * cellHeight + 120;

    for (const node of layout.nodes) {
      positions[node.id] = {
        x: offsetX + (node.x - layout.minX),
        y: offsetY + (node.y - layout.minY),
      };
    }
  });

  return positions;
}

function buildLayout(layoutMode: LayoutMode, metrics: GraphMetrics): LayoutOptions {
  if (layoutMode === "breadthfirst") {
    return {
      name: "breadthfirst",
      directed: true,
      circle: false,
      fit: true,
      padding: 60,
      spacingFactor: 1.2,
      roots: [...metrics.roots],
      animate: false,
    } as LayoutOptions;
  }

  return {
    name: "cose-bilkent",
    animate: false,
    nodeDimensionsIncludeLabels: true,
    idealEdgeLength: 120,
    nodeRepulsion: 7000,
    gravity: 0.25,
    padding: 60,
  } as LayoutOptions;
}

const stylesheet: StylesheetStyle[] = [
  {
    selector: "node",
    style: {
      label: "data(label)",
      "font-size": 11,
      "font-family": "Avenir Next, Segoe UI, sans-serif",
      "font-weight": 600,
      "text-valign": "bottom",
      "text-margin-y": 8,
      "text-wrap": "ellipsis",
      "text-max-width": "140px",
      width: 34,
      height: 34,
      "border-width": 2,
      "border-color": "#fbf7ef",
      "background-color": "#8b949e",
      color: "#23303d",
      "text-background-color": "#f8f3ea",
      "text-background-opacity": 0.9,
      "text-background-padding": "2px",
      "text-background-shape": "roundrectangle",
    },
  },
  ...Object.entries(TYPE_COLORS).reduce<StylesheetStyle[]>((blocks, [type, color]) => {
    if (type === "proof") return blocks;
    blocks.push({
      selector: `node[type="${type}"]`,
      style: { "background-color": color, shape: "ellipse" as const },
    });
    return blocks;
  }, []),
  {
    selector: 'node[kind="proof"]',
    style: {
      "background-color": TYPE_COLORS.proof,
      shape: "diamond",
      width: 28,
      height: 28,
      "font-size": 9,
      color: "#1f2933",
    },
  },
  {
    selector: "node.is-root",
    style: {
      "border-style": "dashed",
      "border-width": 3,
      "border-color": "#8da2b8",
    },
  },
  {
    selector: "node.is-leaf",
    style: {
      "border-width": 4,
      "border-color": "#d1a951",
    },
  },
  {
    selector: "edge",
    style: {
      width: 2,
      "line-color": "#8d99a6",
      "target-arrow-color": "#8d99a6",
      "target-arrow-shape": "triangle",
      "curve-style": "bezier",
      "arrow-scale": 0.9,
      opacity: 0.85,
    },
  },
  {
    selector: 'edge[relation="proves"]',
    style: {
      "line-color": "#2f9e44",
      "target-arrow-color": "#2f9e44",
      "line-style": "solid",
    },
  },
  {
    selector: 'edge[relation="uses"]',
    style: {
      "line-color": "#7b8794",
      "target-arrow-color": "#7b8794",
      "line-style": "dashed",
    },
  },
  {
    selector: "node.filtered-out, edge.filtered-out",
    style: {
      display: "none",
    },
  },
  {
    selector: "node.context-dim",
    style: {
      opacity: 0.15,
    },
  },
  {
    selector: "edge.context-dim",
    style: {
      opacity: 0.08,
    },
  },
  {
    selector: "node.search-match",
    style: {
      "border-width": 4,
      "border-color": "#b7791f",
    },
  },
  {
    selector: "node.selected-focus",
    style: {
      "border-width": 5,
      "border-color": "#1f2933",
      "text-outline-color": "#f8f3ea",
      "text-outline-width": 2,
      "underlay-color": "#f0d9a4",
      "underlay-opacity": 0.45,
      "underlay-padding": 8,
    },
  },
  {
    selector: "node.is-ancestor",
    style: {
      "border-width": 4,
      "border-color": "#2f6fdb",
      "underlay-color": "rgba(47, 111, 219, 0.12)",
      "underlay-opacity": 1,
      "underlay-padding": 6,
    },
  },
  {
    selector: "node.is-descendant",
    style: {
      "border-width": 4,
      "border-color": "#2f9e44",
      "underlay-color": "rgba(47, 158, 68, 0.12)",
      "underlay-opacity": 1,
      "underlay-padding": 6,
    },
  },
];

function nodeMatchesQuery(node: GraphNode, query: string, locale: Locale) {
  const normalized = query.toLowerCase().trim();
  if (!normalized) return false;

  const candidates = [
    node.id,
    node.title_en ?? "",
    node.title_es ?? "",
    formatNodeLabel(node, "title", locale),
  ];

  return candidates.some((value) => value.toLowerCase().includes(normalized));
}

export default function CytoscapeGraph({
  data,
  metrics,
  visibleTypes,
  visibleNodeIds,
  searchQuery,
  selectedNode,
  selectionContext,
  layoutMode,
  labelMode,
  locale,
  onSelectNode,
  onRegisterApi,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [hoveredNode, setHoveredNode] = useState<HoveredNode | null>(null);

  const layoutOptions = useMemo(() => buildLayout(layoutMode, metrics), [layoutMode, metrics]);
  const presetPositions = useMemo(
    () =>
      buildComponentPresetPositions(data, metrics, visibleNodeIds, labelMode, locale),
    [data, labelMode, locale, metrics, visibleNodeIds],
  );
  const handleSelectNode = useEffectEvent((nodeId: string | null) => {
    onSelectNode(nodeId);
  });

  useEffect(() => {
    if (!containerRef.current) return;

    const initialLayout =
      layoutMode === "dagre"
        ? ({
            name: "preset",
            fit: true,
            padding: 80,
            animate: false,
            positions: (node: NodeSingular) => presetPositions[node.id()] ?? { x: 0, y: 0 },
          } as LayoutOptions)
        : layoutOptions;

    const cy = cytoscape({
      container: containerRef.current,
      elements: buildElements(data, labelMode, locale),
      style: stylesheet,
      layout: initialLayout,
      minZoom: 0.15,
      maxZoom: 4,
      wheelSensitivity: 0.18,
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [data, labelMode, layoutMode, layoutOptions, locale, presetPositions]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    onRegisterApi({
      exportPng: () => {
        const uri = cy.png({
          full: true,
          scale: 2,
          bg: "#f6f1e8",
        });
        downloadFile(uri, "mkg-graph.png");
      },
      exportSvg: () => {
        const content = (cy as SvgCapableCore).svg({
          full: true,
          bg: "#f6f1e8",
        });
        const blob = new Blob([content], { type: "image/svg+xml;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        downloadFile(url, "mkg-graph.svg");
        URL.revokeObjectURL(url);
      },
    });

    return () => {
      onRegisterApi(null);
    };
  }, [onRegisterApi]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.batch(() => {
      for (const node of data.nodes) {
        const label = formatNodeLabel(node, labelMode, locale);
        cy.$id(node.id).data("label", label);
      }
    });
  }, [data.nodes, labelMode, locale]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    const handleTap = (event: EventObject) => {
      if (event.target === cy) {
        handleSelectNode(null);
        return;
      }

      if (event.target.isNode()) {
        handleSelectNode(event.target.id());
      }
    };

    const handleMouseOver = (event: EventObject) => {
      if (!containerRef.current || !event.target.isNode()) return;
      const node = event.target;
      const position = node.renderedPosition();
      setHoveredNode({
        id: node.id(),
        label: node.data("label") as string,
        type: getTypeLabel(node.data("type") as EntityType, locale),
        x: position.x,
        y: position.y,
      });
    };

    const clearHover = () => {
      setHoveredNode(null);
    };

    cy.on("tap", handleTap);
    cy.on("mouseover", "node", handleMouseOver);
    cy.on("mouseout", "node", clearHover);
    cy.on("pan zoom dragfree", clearHover);

    return () => {
      cy.off("tap", handleTap);
      cy.off("mouseover", "node", handleMouseOver);
      cy.off("mouseout", "node", clearHover);
      cy.off("pan zoom dragfree", clearHover);
    };
  }, [locale]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.batch(() => {
      cy.elements().removeClass(
        "filtered-out context-dim search-match selected-focus is-ancestor is-descendant is-root is-leaf",
      );

      for (const node of data.nodes) {
        const element = cy.$id(node.id);
        const isVisibleByType = visibleTypes.has(node.type);
        const isVisible = isVisibleByType && visibleNodeIds.has(node.id);

        if (!isVisible) {
          element.addClass("filtered-out");
          continue;
        }

        if (metrics.roots.has(node.id)) element.addClass("is-root");
        if (metrics.leaves.has(node.id)) element.addClass("is-leaf");

        if (selectionContext && !selectionContext.related.has(node.id)) {
          element.addClass("context-dim");
        }

        if (selectedNode === node.id) {
          element.addClass("selected-focus");
        } else if (selectionContext?.ancestors.has(node.id)) {
          element.addClass("is-ancestor");
        } else if (selectionContext?.descendants.has(node.id)) {
          element.addClass("is-descendant");
        }

        if (searchQuery && nodeMatchesQuery(node, searchQuery, locale)) {
          element.addClass("search-match");
        }
      }

      cy.edges().forEach((edge) => {
        const sourceVisible = visibleNodeIds.has(edge.source().id());
        const targetVisible = visibleNodeIds.has(edge.target().id());

        if (!sourceVisible || !targetVisible) {
          edge.addClass("filtered-out");
          return;
        }

        if (
          selectionContext &&
          (!selectionContext.related.has(edge.source().id()) ||
            !selectionContext.related.has(edge.target().id()))
        ) {
          edge.addClass("context-dim");
        }
      });

      cy.$(":selected").unselect();
      if (selectedNode) {
        cy.$id(selectedNode).select();
      }
    });
  }, [
    data.nodes,
    metrics.leaves,
    metrics.roots,
    searchQuery,
    selectedNode,
    selectionContext,
    locale,
    visibleNodeIds,
    visibleTypes,
  ]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    const nextLayout =
      layoutMode === "dagre"
        ? ({
            name: "preset",
            fit: true,
            padding: 80,
            animate: false,
            positions: (node: NodeSingular) => presetPositions[node.id()] ?? { x: 0, y: 0 },
          } as LayoutOptions)
        : layoutOptions;

    cy.layout(nextLayout).run();
  }, [layoutMode, layoutOptions, presetPositions, visibleNodeIds]);

  return (
    <div className="graph-shell">
      <div ref={containerRef} className="graph-canvas" />
      {hoveredNode && (
        <div
          className="graph-tooltip"
          style={{
            left: hoveredNode.x + 16,
            top: hoveredNode.y + 16,
          }}
        >
          <strong>{hoveredNode.label}</strong>
          <span>{hoveredNode.type}</span>
          <code>{hoveredNode.id}</code>
        </div>
      )}
    </div>
  );
}
