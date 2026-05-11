import type { GraphNode, GraphData, NodeDetailsEntry, NodeDetailsIndex } from "../types";
import type { GraphMetrics, SelectionContext } from "../graphAnalysis";
import type { Locale } from "../i18n";
import MathBlock from "./MathBlock";
import {
  UI_TEXT,
  describeDataCoverage,
  describeGraphSemantics,
  explainNode,
  formatSource,
  getAlternateNodeTitle,
  getLocalizedText,
  getTypeLabel,
} from "../i18n";
import {
  formatNodeLabel,
  getDirectRelations,
  getNodeSourceHint,
} from "../graphAnalysis";

interface Props {
  data: GraphData;
  detailsIndex: NodeDetailsIndex;
  metrics: GraphMetrics;
  selectionContext: SelectionContext | null;
  nodeId: string | null;
  locale: Locale;
  onClose: () => void;
  onSelectNode: (nodeId: string) => void;
}

function RelatedNodeButton({
  node,
  locale,
  onSelectNode,
}: {
  node: GraphNode;
  locale: Locale;
  onSelectNode: (nodeId: string) => void;
}) {
  return (
    <button className="related-node-btn" onClick={() => onSelectNode(node.id)}>
      <span>{formatNodeLabel(node, "title", locale)}</span>
      <code>{node.id}</code>
    </button>
  );
}

function EmptyPanel({ locale }: { locale: Locale }) {
  const text = UI_TEXT[locale];

  return (
    <aside className="details-panel">
      <div className="details-header">
        <div>
          <p className="details-kicker">{text.detailsEmptyKicker}</p>
          <h2>{text.detailsEmptyTitle}</h2>
        </div>
      </div>

      <div className="details-body">
        <div className="details-note-card">
          <p>{text.detailsEmptyBody}</p>
        </div>
      </div>
    </aside>
  );
}

export default function DetailsPanel({
  data,
  detailsIndex,
  metrics,
  selectionContext,
  nodeId,
  locale,
  onClose,
  onSelectNode,
}: Props) {
  if (!nodeId) {
    return <EmptyPanel locale={locale} />;
  }

  const node: GraphNode | undefined = data.nodes.find((n) => n.id === nodeId);
  if (!node) return <EmptyPanel locale={locale} />;
  const details: NodeDetailsEntry | undefined = detailsIndex[nodeId];

  const text = UI_TEXT[locale];
  const { incoming, outgoing } = getDirectRelations(nodeId, data.links);
  const uses: string[] = [];
  const proves: string[] = [];
  const provedBy: string[] = [];
  const usedByProofs: string[] = [];

  if (node.kind === "proof") {
    for (const edge of incoming) uses.push(edge.source);
  }

  for (const edge of outgoing) {
    if (edge.relation === "proves") proves.push(edge.target);
    if (edge.relation === "uses") usedByProofs.push(edge.target);
  }

  for (const edge of incoming) {
    if (edge.relation === "proves") provedBy.push(edge.source);
  }

  const sourceHint = getNodeSourceHint(node);
  const alternateTitle = getAlternateNodeTitle(node, locale);
  const naturalText = getLocalizedText(details?.natural, locale);
  const latex = details?.latex?.trim() || null;
  const notes = details?.notes?.trim() || null;
  const sourceList = details?.sources ?? [];

  return (
    <aside className="details-panel">
      <div className="details-header">
        <div>
          <p className="details-kicker">
            {node.kind === "proof" ? text.detailsKickerProof : text.detailsKickerStatement}
          </p>
          <h2>{formatNodeLabel(node, "title", locale)}</h2>
          {alternateTitle && <p className="details-subtitle">{alternateTitle}</p>}
        </div>
        <button className="close-btn" onClick={onClose} aria-label={text.close}>
          &times;
        </button>
      </div>

      <div className="details-body">
        <div className="details-note-card">
          <h3>{text.explanation}</h3>
          <p>{explainNode(node, locale)}</p>
        </div>

        <div className="details-note-card">
          <h3>{text.graphSemantics}</h3>
          <p>{describeGraphSemantics(locale, node)}</p>
        </div>

        <div className="details-note-card">
          <h3>{text.naturalText}</h3>
          <p>{naturalText ?? text.noNaturalText}</p>
        </div>

        <div className="details-note-card">
          <h3>{text.mathematicalForm}</h3>
          <MathBlock expression={latex} fallback={text.noLatex} />
        </div>

        <dl>
          <dt>{text.id}</dt>
          <dd><code>{node.id}</code></dd>

          <dt>{text.type}</dt>
          <dd><span className={`badge badge--${node.type}`}>{getTypeLabel(node.type, locale)}</span></dd>

          <dt>{text.status}</dt>
          <dd>{node.status}</dd>

          <dt>{text.role}</dt>
          <dd>
            {metrics.roots.has(node.id) ? text.root : text.nonRoot}
            {" · "}
            {metrics.leaves.has(node.id) ? text.leaf : text.nonLeaf}
          </dd>

          <dt>{text.incomingOutgoing}</dt>
          <dd>
            {(metrics.incoming.get(node.id)?.length ?? 0)} / {(metrics.outgoing.get(node.id)?.length ?? 0)}
          </dd>

          <dt>{text.primaryLabel}</dt>
          <dd>{formatNodeLabel(node, "title", locale)}</dd>

          {alternateTitle && (
            <>
              <dt>{text.alternateLabel}</dt>
              <dd>{alternateTitle}</dd>
            </>
          )}

          {node.style && (
            <>
              <dt>{text.proofStyle}</dt>
              <dd>{details?.style ?? node.style}</dd>
            </>
          )}

          <dt>{text.sourceMetadata}</dt>
          <dd>
            {sourceList.length > 0
              ? `${sourceList.length} ${text.sourceList.toLowerCase()}`
              : sourceHint
                ? `${text.sourceHintPrefix}: ${sourceHint}`
                : text.fullMetadataUnavailable}
          </dd>

          <dt>{text.confidence}</dt>
          <dd>{details?.confidence ?? text.confidenceUnavailable}</dd>

          <dt>{text.ancestryDescendants}</dt>
          <dd>
            {selectionContext?.ancestors.size ?? 0} / {selectionContext?.descendants.size ?? 0}
          </dd>
        </dl>

        <div className="details-note-card">
          <h3>{text.dataCoverage}</h3>
          <p>{describeDataCoverage(locale)}</p>
        </div>

        <section>
          <h3>{text.sourceList} ({sourceList.length})</h3>
          {sourceList.length > 0 ? (
            <div className="edge-list">
              {sourceList.map((source, index) => (
                <div
                  key={`${nodeId}-source-${source.work ?? "work"}-${source.section ?? "section"}-${source.page ?? "page"}-${index}`}
                  className="source-row"
                >
                  <span>{formatSource(source) || text.fullMetadataUnavailable}</span>
                  {source.url && (
                    <a href={source.url} target="_blank" rel="noreferrer">
                      {source.url}
                    </a>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="details-note-card">
              <p>{text.fullMetadataUnavailable}</p>
            </div>
          )}
        </section>

        <div className="details-note-card">
          <h3>{text.notes}</h3>
          <p>{notes ?? text.noNotes}</p>
        </div>

        {uses.length > 0 && (
          <section>
            <h3>{text.uses} ({uses.length})</h3>
            <div className="related-node-list">
              {uses.map((id) => {
                const relatedNode = metrics.nodeById.get(id);
                if (!relatedNode) return null;
                return (
                  <RelatedNodeButton
                    key={id}
                    node={relatedNode}
                    locale={locale}
                    onSelectNode={onSelectNode}
                  />
                );
              })}
            </div>
          </section>
        )}

        {provedBy.length > 0 && (
          <section>
            <h3>{text.provedBy} ({provedBy.length})</h3>
            <div className="related-node-list">
              {provedBy.map((id) => {
                const relatedNode = metrics.nodeById.get(id);
                if (!relatedNode) return null;
                return (
                  <RelatedNodeButton
                    key={id}
                    node={relatedNode}
                    locale={locale}
                    onSelectNode={onSelectNode}
                  />
                );
              })}
            </div>
          </section>
        )}

        {proves.length > 0 && (
          <section>
            <h3>{text.proves} ({proves.length})</h3>
            <div className="related-node-list">
              {proves.map((id) => {
                const relatedNode = metrics.nodeById.get(id);
                if (!relatedNode) return null;
                return (
                  <RelatedNodeButton
                    key={id}
                    node={relatedNode}
                    locale={locale}
                    onSelectNode={onSelectNode}
                  />
                );
              })}
            </div>
          </section>
        )}

        {usedByProofs.length > 0 && (
          <section>
            <h3>{text.usedByProofs} ({usedByProofs.length})</h3>
            <div className="related-node-list">
              {usedByProofs.map((id) => {
                const relatedNode = metrics.nodeById.get(id);
                if (!relatedNode) return null;
                return (
                  <RelatedNodeButton
                    key={id}
                    node={relatedNode}
                    locale={locale}
                    onSelectNode={onSelectNode}
                  />
                );
              })}
            </div>
          </section>
        )}

        {(incoming.length > 0 || outgoing.length > 0) && (
          <section>
            <h3>{text.connectedNodes} ({incoming.length + outgoing.length})</h3>
            <div className="edge-list">
              {incoming.map((edge) => (
                <button
                  key={`${edge.source}-${edge.target}-${edge.relation}-in`}
                  className="edge-row"
                  onClick={() => onSelectNode(edge.source)}
                >
                  <span className={`relation relation--${edge.relation}`}>{edge.relation}</span>
                  <span>{text.from} {edge.source}</span>
                </button>
              ))}
              {outgoing.map((edge) => (
                <button
                  key={`${edge.source}-${edge.target}-${edge.relation}-out`}
                  className="edge-row"
                  onClick={() => onSelectNode(edge.target)}
                >
                  <span className={`relation relation--${edge.relation}`}>{edge.relation}</span>
                  <span>{text.to} {edge.target}</span>
                </button>
              ))}
            </div>
          </section>
        )}
      </div>
    </aside>
  );
}
