import type { GraphData, GraphLink, GraphNode } from "./types";
import type { Locale } from "./i18n";
import { getNodeTitle } from "./i18n";

export type LayoutMode = "dagre" | "breadthfirst" | "cose";
export type LabelMode = "title" | "id";
export type BoundaryFilter = "all" | "roots" | "leaves";

export interface GraphMetrics {
  nodeById: Map<string, GraphNode>;
  incoming: Map<string, string[]>;
  outgoing: Map<string, string[]>;
  roots: Set<string>;
  leaves: Set<string>;
  components: string[][];
  longestChain: string[];
  isDag: boolean;
}

export interface SelectionContext {
  ancestors: Set<string>;
  descendants: Set<string>;
  related: Set<string>;
}

function humanizeSlug(value: string) {
  const words: string[] = [];

  for (const part of value.split("-")) {
    if (!part) continue;
    words.push(part.charAt(0).toUpperCase() + part.slice(1));
  }

  return words.join(" ");
}

export function formatNodeLabel(node: GraphNode, labelMode: LabelMode, locale: Locale) {
  if (labelMode === "title") {
    const title = getNodeTitle(node, locale);
    if (title) return title;
  }

  const parts = node.id.split(".");
  const relevant =
    node.kind === "proof" && parts.length > 2 ? parts.slice(1, -1) : parts.slice(1);

  return humanizeSlug(relevant.join("-")) || node.id;
}

export function getNodeSourceHint(node: GraphNode) {
  if (node.kind !== "proof") return null;
  const parts = node.id.split(".");
  return parts.length > 2 ? humanizeSlug(parts.at(-1) ?? "") : null;
}

export function buildGraphMetrics(data: GraphData): GraphMetrics {
  const nodeById = new Map<string, GraphNode>();
  const incoming = new Map<string, string[]>();
  const outgoing = new Map<string, string[]>();
  const undirected = new Map<string, Set<string>>();

  for (const node of data.nodes) {
    nodeById.set(node.id, node);
    incoming.set(node.id, []);
    outgoing.set(node.id, []);
    undirected.set(node.id, new Set());
  }

  for (const link of data.links) {
    incoming.get(link.target)?.push(link.source);
    outgoing.get(link.source)?.push(link.target);
    undirected.get(link.source)?.add(link.target);
    undirected.get(link.target)?.add(link.source);
  }

  const roots = new Set<string>();
  const leaves = new Set<string>();

  for (const node of data.nodes) {
    if ((incoming.get(node.id)?.length ?? 0) === 0) roots.add(node.id);
    if ((outgoing.get(node.id)?.length ?? 0) === 0) leaves.add(node.id);
  }

  const components: string[][] = [];
  const seen = new Set<string>();

  for (const node of data.nodes) {
    if (seen.has(node.id)) continue;

    const queue = [node.id];
    const component: string[] = [];
    seen.add(node.id);

    while (queue.length > 0) {
      const current = queue.shift()!;
      component.push(current);

      for (const neighbor of undirected.get(current) ?? []) {
        if (seen.has(neighbor)) continue;
        seen.add(neighbor);
        queue.push(neighbor);
      }
    }

    components.push(component);
  }

  const indegree = new Map<string, number>();
  for (const node of data.nodes) {
    indegree.set(node.id, incoming.get(node.id)?.length ?? 0);
  }

  const topoQueue = [...roots];
  const topoOrder: string[] = [];

  while (topoQueue.length > 0) {
    const current = topoQueue.shift()!;
    topoOrder.push(current);

    for (const target of outgoing.get(current) ?? []) {
      const nextDegree = (indegree.get(target) ?? 0) - 1;
      indegree.set(target, nextDegree);
      if (nextDegree === 0) topoQueue.push(target);
    }
  }

  const isDag = topoOrder.length === data.nodes.length;
  let longestChain: string[] = [];

  if (isDag) {
    const distance = new Map<string, number>();
    const previous = new Map<string, string | null>();

    for (const node of data.nodes) {
      distance.set(node.id, Number.NEGATIVE_INFINITY);
      previous.set(node.id, null);
    }

    for (const root of roots) {
      distance.set(root, 0);
    }

    for (const current of topoOrder) {
      const currentDistance = distance.get(current) ?? Number.NEGATIVE_INFINITY;
      if (currentDistance === Number.NEGATIVE_INFINITY) continue;

      for (const target of outgoing.get(current) ?? []) {
        const candidate = currentDistance + 1;
        if (candidate > (distance.get(target) ?? Number.NEGATIVE_INFINITY)) {
          distance.set(target, candidate);
          previous.set(target, current);
        }
      }
    }

    let chainEnd: string | null = null;
    let maxDistance = Number.NEGATIVE_INFINITY;

    for (const [nodeId, nodeDistance] of distance.entries()) {
      if (nodeDistance > maxDistance) {
        maxDistance = nodeDistance;
        chainEnd = nodeId;
      }
    }

    if (chainEnd) {
      const path: string[] = [];
      let cursor: string | null = chainEnd;
      while (cursor) {
        path.push(cursor);
        cursor = previous.get(cursor) ?? null;
      }
      longestChain = path.reverse();
    }
  }

  return {
    nodeById,
    incoming,
    outgoing,
    roots,
    leaves,
    components,
    longestChain,
    isDag,
  };
}

function traverse(start: string, adjacency: Map<string, string[]>) {
  const seen = new Set<string>();
  const queue = [...(adjacency.get(start) ?? [])];

  while (queue.length > 0) {
    const current = queue.shift()!;
    if (seen.has(current)) continue;
    seen.add(current);

    for (const next of adjacency.get(current) ?? []) {
      if (!seen.has(next)) queue.push(next);
    }
  }

  return seen;
}

export function getSelectionContext(
  selectedNodeId: string | null,
  metrics: GraphMetrics,
): SelectionContext | null {
  if (!selectedNodeId || !metrics.nodeById.has(selectedNodeId)) return null;

  const ancestors = traverse(selectedNodeId, metrics.incoming);
  const descendants = traverse(selectedNodeId, metrics.outgoing);
  const related = new Set<string>([selectedNodeId, ...ancestors, ...descendants]);

  return { ancestors, descendants, related };
}

export function getDirectRelations(nodeId: string, links: GraphLink[]) {
  const incoming = links.filter((link) => link.target === nodeId);
  const outgoing = links.filter((link) => link.source === nodeId);
  return { incoming, outgoing };
}
