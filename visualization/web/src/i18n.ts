import type { EntityType, GraphNode, LocalizedText, SourceMetadata } from "./types";

export type Locale = "es" | "en";

type Dictionary = {
  appKicker: string;
  appTitle: string;
  loading: string;
  loadErrorTitle: string;
  loadErrorHint: string;
  search: string;
  searchPlaceholder: string;
  boundary: string;
  layout: string;
  labels: string;
  language: string;
  export: string;
  boundaryOptions: Record<"all" | "roots" | "leaves", string>;
  layoutOptions: Record<"dagre" | "breadthfirst" | "cose", string>;
  labelOptions: Record<"title" | "id", string>;
  statsVisibleGraph: string;
  statsEntityMix: string;
  statsStructure: string;
  statsLongestChain: string;
  nodes: string;
  edges: string;
  visibleRoots: string;
  visibleLeaves: string;
  statements: string;
  proofs: string;
  roots: string;
  leaves: string;
  components: string;
  dagCompatible: string;
  cyclesDetected: string;
  hops: string;
  notAvailable: string;
  detailsEmptyKicker: string;
  detailsEmptyTitle: string;
  detailsEmptyBody: string;
  detailsKickerStatement: string;
  detailsKickerProof: string;
  explanation: string;
  dataCoverage: string;
  graphSemantics: string;
  id: string;
  type: string;
  status: string;
  role: string;
  incomingOutgoing: string;
  primaryLabel: string;
  alternateLabel: string;
  naturalText: string;
  mathematicalForm: string;
  notes: string;
  sourceList: string;
  proofStyle: string;
  sourceMetadata: string;
  confidence: string;
  ancestryDescendants: string;
  uses: string;
  provedBy: string;
  proves: string;
  usedByProofs: string;
  connectedNodes: string;
  from: string;
  to: string;
  root: string;
  nonRoot: string;
  leaf: string;
  nonLeaf: string;
  fullMetadataUnavailable: string;
  confidenceUnavailable: string;
  sourceHintPrefix: string;
  noNotes: string;
  noNaturalText: string;
  noLatex: string;
  close: string;
};

export const UI_TEXT: Record<Locale, Dictionary> = {
  es: {
    appKicker: "Mathematical Knowledge Graph",
    appTitle: "Atlas MKG",
    loading: "Cargando grafo…",
    loadErrorTitle: "No se pudo cargar el grafo",
    loadErrorHint: "Asegúrate de copiar graph.json y node-details.json dentro de visualization/web/public/.",
    search: "Buscar",
    searchPlaceholder: "ID o título",
    boundary: "Frontera",
    layout: "Layout",
    labels: "Etiquetas",
    language: "Idioma",
    export: "Exportar",
    boundaryOptions: {
      all: "Todos",
      roots: "Raíces",
      leaves: "Hojas",
    },
    layoutOptions: {
      dagre: "Jerárquico",
      breadthfirst: "Por niveles",
      cose: "Fuerza",
    },
    labelOptions: {
      title: "Títulos",
      id: "IDs",
    },
    statsVisibleGraph: "Grafo visible",
    statsEntityMix: "Tipos de entidad",
    statsStructure: "Estructura",
    statsLongestChain: "Cadena más larga",
    nodes: "nodos",
    edges: "aristas",
    visibleRoots: "raíces visibles",
    visibleLeaves: "hojas visibles",
    statements: "statements",
    proofs: "proofs",
    roots: "raíces",
    leaves: "hojas",
    components: "componentes",
    dagCompatible: "Compatible con DAG",
    cyclesDetected: "Se detectaron ciclos",
    hops: "saltos",
    notAvailable: "No disponible",
    detailsEmptyKicker: "Inspector del nodo",
    detailsEmptyTitle: "Selecciona un nodo",
    detailsEmptyBody:
      "Haz clic en un statement o proof para ver su rol, sus conexiones y cómo participa dentro del grafo matemático.",
    detailsKickerStatement: "statement",
    detailsKickerProof: "proof",
    explanation: "Qué representa",
    dataCoverage: "Cobertura del artefacto",
    graphSemantics: "Semántica del grafo",
    id: "ID",
    type: "Tipo",
    status: "Estado",
    role: "Rol",
    incomingOutgoing: "Entradas / salidas",
    primaryLabel: "Etiqueta principal",
    alternateLabel: "Etiqueta alternativa",
    naturalText: "Enunciado",
    mathematicalForm: "Forma matemática",
    notes: "Notas",
    sourceList: "Fuentes",
    proofStyle: "Estilo de prueba",
    sourceMetadata: "Metadatos de fuente",
    confidence: "Confianza",
    ancestryDescendants: "Ancestros / descendientes",
    uses: "Usa",
    provedBy: "Demostrado por",
    proves: "Demuestra",
    usedByProofs: "Usado por proofs",
    connectedNodes: "Nodos conectados",
    from: "desde",
    to: "hacia",
    root: "raíz",
    nonRoot: "no raíz",
    leaf: "hoja",
    nonLeaf: "no hoja",
    fullMetadataUnavailable: "No disponible en node-details.json",
    confidenceUnavailable: "No disponible en node-details.json",
    sourceHintPrefix: "Pista de fuente",
    noNotes: "Sin notas adicionales",
    noNaturalText: "No disponible",
    noLatex: "No disponible",
    close: "Cerrar",
  },
  en: {
    appKicker: "Mathematical Knowledge Graph",
    appTitle: "MKG Atlas",
    loading: "Loading graph…",
    loadErrorTitle: "Failed to load graph",
    loadErrorHint: "Make sure graph.json and node-details.json are copied into visualization/web/public/.",
    search: "Search",
    searchPlaceholder: "ID or title",
    boundary: "Boundary",
    layout: "Layout",
    labels: "Labels",
    language: "Language",
    export: "Export",
    boundaryOptions: {
      all: "All",
      roots: "Roots",
      leaves: "Leaves",
    },
    layoutOptions: {
      dagre: "Hierarchical",
      breadthfirst: "Breadth-first",
      cose: "Force",
    },
    labelOptions: {
      title: "Titles",
      id: "IDs",
    },
    statsVisibleGraph: "Visible graph",
    statsEntityMix: "Entity mix",
    statsStructure: "Structure",
    statsLongestChain: "Longest chain",
    nodes: "nodes",
    edges: "edges",
    visibleRoots: "visible roots",
    visibleLeaves: "visible leaves",
    statements: "statements",
    proofs: "proofs",
    roots: "roots",
    leaves: "leaves",
    components: "components",
    dagCompatible: "DAG-compatible",
    cyclesDetected: "Cycles detected",
    hops: "hops",
    notAvailable: "Not available",
    detailsEmptyKicker: "Node inspector",
    detailsEmptyTitle: "Select a node",
    detailsEmptyBody:
      "Click a statement or proof to inspect its role, its connections, and how it participates in the mathematical graph.",
    detailsKickerStatement: "statement",
    detailsKickerProof: "proof",
    explanation: "What this represents",
    dataCoverage: "Artifact coverage",
    graphSemantics: "Graph semantics",
    id: "ID",
    type: "Type",
    status: "Status",
    role: "Role",
    incomingOutgoing: "Incoming / outgoing",
    primaryLabel: "Primary label",
    alternateLabel: "Alternate label",
    naturalText: "Statement text",
    mathematicalForm: "Mathematical form",
    notes: "Notes",
    sourceList: "Sources",
    proofStyle: "Proof style",
    sourceMetadata: "Source metadata",
    confidence: "Confidence",
    ancestryDescendants: "Ancestors / descendants",
    uses: "Uses",
    provedBy: "Proved by",
    proves: "Proves",
    usedByProofs: "Used by proofs",
    connectedNodes: "Connected nodes",
    from: "from",
    to: "to",
    root: "root",
    nonRoot: "non-root",
    leaf: "leaf",
    nonLeaf: "non-leaf",
    fullMetadataUnavailable: "Not available in node-details.json",
    confidenceUnavailable: "Not available in node-details.json",
    sourceHintPrefix: "Source hint",
    noNotes: "No additional notes",
    noNaturalText: "Not available",
    noLatex: "Not available",
    close: "Close",
  },
};

export const TYPE_LABELS: Record<Locale, Record<EntityType, string>> = {
  es: {
    axiom: "Axioma",
    definition: "Definición",
    lemma: "Lema",
    proposition: "Proposición",
    theorem: "Teorema",
    corollary: "Corolario",
    conjecture: "Conjetura",
    proof: "Prueba",
  },
  en: {
    axiom: "Axiom",
    definition: "Definition",
    lemma: "Lemma",
    proposition: "Proposition",
    theorem: "Theorem",
    corollary: "Corollary",
    conjecture: "Conjecture",
    proof: "Proof",
  },
};

export function getNodeTitle(node: GraphNode, locale: Locale) {
  if (locale === "es") return node.title_es || node.title_en || null;
  return node.title_en || node.title_es || null;
}

export function getAlternateNodeTitle(node: GraphNode, locale: Locale) {
  const primary = getNodeTitle(node, locale);
  const alternate = locale === "es" ? node.title_en || null : node.title_es || null;
  if (!alternate || alternate === primary) return null;
  return alternate;
}

export function getTypeLabel(type: EntityType, locale: Locale) {
  return TYPE_LABELS[locale][type];
}

export function getLocalizedText(text: LocalizedText | undefined, locale: Locale) {
  if (!text) return null;
  if (locale === "es") return text.es || text.en || Object.values(text).find(Boolean) || null;
  return text.en || text.es || Object.values(text).find(Boolean) || null;
}

export function formatSource(source: SourceMetadata) {
  const parts = [
    source.work,
    source.author,
    source.edition ? `ed. ${source.edition}` : undefined,
    source.chapter ? `ch. ${source.chapter}` : undefined,
    source.section ? `sec. ${source.section}` : undefined,
    source.page ? `p. ${source.page}` : undefined,
    source.locator,
  ].filter(Boolean);

  return parts.join(" · ");
}

export function explainNode(node: GraphNode, locale: Locale) {
  if (locale === "es") {
    if (node.kind === "proof") {
      return "Este nodo representa una prueba. En el MKG, una prueba conecta los statements que usa con el statement que demuestra.";
    }

    return `Este nodo representa ${
      /^[aeiouáéíóú]/i.test(getTypeLabel(node.type, locale)) ? "una" : "un"
    } ${getTypeLabel(node.type, locale).toLowerCase()}. En el MKG, los statements no se conectan directamente entre sí: participan en proofs que los usan o los establecen.`;
  }

  if (node.kind === "proof") {
    return "This node represents a proof. In the MKG, a proof connects the statements it uses with the statement it establishes.";
  }

  return `This node represents a ${getTypeLabel(node.type, locale).toLowerCase()}. In the MKG, statements do not connect directly to other statements: they participate in proofs that use or establish them.`;
}

export function describeDataCoverage(locale: Locale) {
  if (locale === "es") {
    return "El panel ahora combina graph.json con node-details.json. Cuando un nodo lo incluye, aquí se muestran enunciado, LaTeX, fuentes, confianza y notas.";
  }

  return "The panel now combines graph.json with node-details.json. When a node includes them, this view shows statement text, LaTeX, sources, confidence, and notes.";
}

export function describeGraphSemantics(locale: Locale, node: GraphNode) {
  if (locale === "es") {
    return node.kind === "proof"
      ? "Las aristas entrantes suelen corresponder a statements usados por esta prueba, y la arista saliente principal apunta al statement demostrado."
      : "Las aristas que llegan desde proofs indican cómo se establece este statement. Las aristas hacia proofs muestran dónde vuelve a reutilizarse.";
  }

  return node.kind === "proof"
    ? "Incoming edges usually correspond to statements used by this proof, and the main outgoing edge points to the statement it proves."
    : "Incoming edges from proofs show how this statement is established. Outgoing edges to proofs show where it is reused.";
}
