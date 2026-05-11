import type { GraphData, EntityType } from "../types";
import type { GraphMetrics } from "../graphAnalysis";
import { TYPE_LABELS, UI_TEXT, type Locale } from "../i18n";

interface Props {
  data: GraphData;
  metrics: GraphMetrics;
  visibleStats: {
    visibleNodes: number;
    visibleEdges: number;
    visibleTypeCounts: Record<EntityType, number>;
    visibleRoots: number;
    visibleLeaves: number;
  };
  typeCounts: Record<EntityType, number>;
  longestChainPreview: {
    length: number;
    start: string;
    end: string;
  } | null;
  locale: Locale;
}

export default function StatsBar({
  data,
  metrics,
  visibleStats,
  typeCounts,
  longestChainPreview,
  locale,
}: Props) {
  const text = UI_TEXT[locale];
  const statements = data.nodes.filter((n) => n.kind === "statement").length;
  const proofs = data.nodes.filter((n) => n.kind === "proof").length;

  return (
    <div className="stats-bar">
      <div className="stat-card">
        <span className="stat-label">{text.statsVisibleGraph}</span>
        <strong>
          {visibleStats.visibleNodes}/{data.nodes.length}
        </strong>
        <span className="stat-detail">
          {text.nodes} · {visibleStats.visibleEdges}/{data.links.length} {text.edges}
        </span>
        <span className="stat-detail">
          {visibleStats.visibleRoots} {text.visibleRoots} · {visibleStats.visibleLeaves} {text.visibleLeaves}
        </span>
      </div>

      <div className="stat-card">
        <span className="stat-label">{text.statsEntityMix}</span>
        <strong>
          {statements} {text.statements} · {proofs} {text.proofs}
        </strong>
        <span className="stat-detail">
          {metrics.roots.size} {text.roots} · {metrics.leaves.size} {text.leaves}
        </span>
      </div>

      <div className="stat-card">
        <span className="stat-label">{text.statsStructure}</span>
        <strong>{metrics.components.length} {text.components}</strong>
        <span className="stat-detail">
          {metrics.isDag ? text.dagCompatible : text.cyclesDetected}
        </span>
      </div>

      <div className="stat-card">
        <span className="stat-label">{text.statsLongestChain}</span>
        <strong>
          {longestChainPreview ? `${longestChainPreview.length} ${text.hops}` : text.notAvailable}
        </strong>
        <span className="stat-detail">
          {longestChainPreview
            ? `${longestChainPreview.start} -> ${longestChainPreview.end}`
            : text.notAvailable}
        </span>
      </div>

      <div className="type-summary">
        {Object.entries(typeCounts).map(([type, count]) => {
          if (count === 0) return null;
          const visibleCount = visibleStats.visibleTypeCounts[type as EntityType] ?? 0;
          return (
            <span key={type} className="type-summary-pill">
              {TYPE_LABELS[locale][type as EntityType]} {visibleCount}/{count}
            </span>
          );
        })}
      </div>
    </div>
  );
}
