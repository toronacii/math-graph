/** Types mirroring the graph.json schema produced by scripts/build_graph.py */

export type EntityType =
  | "axiom"
  | "definition"
  | "lemma"
  | "proposition"
  | "theorem"
  | "corollary"
  | "conjecture"
  | "proof";

export interface GraphNode {
  id: string;
  kind: "statement" | "proof";
  type: EntityType;
  status: string;
  title_en?: string;
  title_es?: string;
  style?: string;
}

export interface GraphLink {
  source: string;
  target: string;
  relation: "uses" | "proves";
}

export interface GraphData {
  directed: boolean;
  multigraph: boolean;
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface LocalizedText {
  en?: string;
  es?: string;
  [key: string]: string | undefined;
}

export interface SourceMetadata {
  work?: string;
  author?: string;
  edition?: string;
  chapter?: string;
  section?: string;
  page?: string;
  locator?: string;
  url?: string;
}

export interface NodeDetailsEntry {
  id: string;
  kind: "statement" | "proof";
  type: EntityType;
  status: string;
  title?: LocalizedText;
  natural?: LocalizedText;
  latex?: string;
  style?: string;
  proves?: string;
  uses?: string[];
  sources?: SourceMetadata[];
  confidence?: string;
  notes?: string;
}

export type NodeDetailsIndex = Record<string, NodeDetailsEntry>;
