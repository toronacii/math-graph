// TypeScript types for the v0.3.1 export contract emitted by
// scripts/v03/build_db.py. Mirrored on the frontend so consumers can
// safely access optional fields.

export type EntityType =
  | "definition"
  | "proposition"
  | "theorem"
  | "lemma"
  | "corollary"
  | "axiom"
  | "conjecture"
  | "proof";

export type Status =
  | "draft"
  | "extracted"
  | "needs_review"
  | "reviewed"
  | "verified"
  | "deprecated"
  | "redirected";

export type Confidence = "high" | "medium" | "low";
export type LatexStatus =
  | "present"
  | "missing"
  | "in_progress"
  | "not_applicable";

export type EdgeRelation = "uses" | "proves" | "depends_on";

// ---------------- graph.json ---------------------------------------------

export interface GraphNode {
  id: string;
  kind: "statement" | "proof";
  type: EntityType;
  status: Status;
  // statement-only summaries
  primary_domain?: string;
  semantic_kinds?: string[];
  latex_status?: LatexStatus;
  // both
  quality_overall?: Confidence;
  // proof-only
  style?: string;
}

export interface GraphLink {
  source: string;
  target: string;
  relation: EdgeRelation;
  role?: string;
  confidence?: Confidence;
  implicit?: boolean;
}

export interface GraphPayload {
  directed: true;
  multigraph: true;
  schema_version: string;
  nodes: GraphNode[];
  links: GraphLink[];
}

// ---------------- node-details.json --------------------------------------

export interface I18nText {
  text: string;
  is_original: boolean;
  origin?: string;
  review_status?: string;
}

export interface LatexBody {
  body: string | null;
  status: LatexStatus;
  review_status: string;
}

export interface QualityAxes {
  extraction?: Confidence;
  dependency?: Confidence;
  semantic?: Confidence;
  translation?: Confidence;
  latex?: Confidence;
  source_alignment?: Confidence;
}

export interface Provenance {
  schema_version?: string;
  rerun_id?: string;
  extracted_by?: string;
  extracted_at?: string;
  redirected_to?: string;
}

export interface Source {
  work: string;
  author?: string;
  edition?: string;
  year?: number;
  chapter?: string;
  section?: string;
  theorem_label?: string;
  page?: string;
  locator?: string;
  url?: string;
  source_language?: string;
}

export interface DependsOn {
  id: string;
  role: string;
  confidence?: Confidence;
  notes?: string;
}

export interface Generality {
  target: string;
  relation: string;
}

export interface ProofUse {
  id: string;
  role: string;
  confidence: Confidence;
  implicit: boolean;
  locality?: string;
  notes?: string;
}

export interface ProofPart {
  name: string;
  kind: string;
  description?: string;
}

export interface StatementDetails {
  id: string;
  kind: "statement";
  type: EntityType;
  status: Status;
  original_language?: string;
  notes?: string;
  title?: Record<string, I18nText>;
  natural?: Record<string, I18nText>;
  latex?: LatexBody;
  domains?: { primary?: string[]; secondary?: string[] };
  ambient_structures?: string[];
  ontology?: { semantic_kind?: string[]; keywords?: string[] };
  quality?: QualityAxes;
  provenance?: Provenance;
  derived_from?: string[];
  proved_by?: string[];
  depends_on?: DependsOn[];
  generality?: Generality[];
  sources?: Source[];
}

export interface ProofDetails {
  id: string;
  kind: "proof";
  type: "proof";
  status: Status;
  proves: string;
  style: string;
  notes?: string;
  uses?: ProofUse[];
  parts?: ProofPart[];
  quality?: QualityAxes;
  provenance?: Provenance;
  sources?: Source[];
}

export type NodeDetails = StatementDetails | ProofDetails;
export type NodeDetailsMap = Record<string, NodeDetails>;
