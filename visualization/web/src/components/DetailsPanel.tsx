// Right-side details panel for the currently selected node.
// Renders i18n title/natural, LaTeX (KaTeX), domains, ambient, ontology,
// quality, sources, provenance, proved_by/uses/depends_on with click-to-
// navigate links.

import clsx from "clsx";
import { useExplorer } from "../state/store";
import type {
  NodeDetails,
  NodeDetailsMap,
  ProofDetails,
  StatementDetails,
} from "../data/types";
import { TYPE_COLORS, TYPE_LABELS } from "../theme";
import MathBlock from "./MathBlock";

interface Props {
  details: NodeDetailsMap;
}

const Section = ({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) => (
  <section className="mt-5">
    <h3 className="mb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
      {title}
    </h3>
    {children}
  </section>
);

const Chip = ({
  children,
  color,
}: {
  children: React.ReactNode;
  color?: string;
}) => (
  <span
    className="mr-1.5 mb-1.5 inline-flex items-center rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-[11px] font-medium text-slate-700"
    style={color ? { background: color, color: "#fff", borderColor: color } : undefined}
  >
    {children}
  </span>
);

const NodeLink = ({
  id,
  details,
  onSelect,
  meta,
}: {
  id: string;
  details: NodeDetailsMap;
  onSelect: (id: string) => void;
  meta?: React.ReactNode;
}) => {
  const d = details[id];
  const label =
    (d?.kind === "statement" &&
      (d.title?.[d.original_language ?? "en"]?.text ??
        d.title?.en?.text ??
        d.title?.es?.text)) ||
    id;
  const type = d?.type;
  return (
    <button
      onClick={() => onSelect(id)}
      className="block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-left text-[13px] hover:border-slate-300 hover:bg-slate-50"
    >
      <div className="flex items-center gap-2">
        {type && (
          <span
            className="inline-block h-2.5 w-2.5 rounded-full"
            style={{ background: TYPE_COLORS[type] }}
          />
        )}
        <span className="font-medium text-slate-800">{label}</span>
      </div>
      <code className="mt-1 block text-[10px] text-slate-500">{id}</code>
      {meta}
    </button>
  );
};

const TypeBadge = ({ type }: { type: keyof typeof TYPE_COLORS }) => (
  <span
    className="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wider text-white"
    style={{ background: TYPE_COLORS[type] }}
  >
    {TYPE_LABELS[type]}
  </span>
);

const renderStatement = (
  d: StatementDetails,
  details: NodeDetailsMap,
  onSelect: (id: string) => void,
) => {
  const origLang = d.original_language ?? "en";
  const title =
    d.title?.[origLang]?.text ?? d.title?.en?.text ?? d.title?.es?.text ?? d.id;
  const naturalEntries = d.natural ? Object.entries(d.natural) : [];
  return (
    <>
      <header className="border-b border-slate-200 px-5 py-4">
        <div className="mb-2 flex items-center gap-2">
          <TypeBadge type={d.type} />
          <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500">
            {d.status}
          </span>
        </div>
        <h2 className="font-serif text-xl leading-tight text-slate-900">
          {title}
        </h2>
        <code className="mt-1 block text-[11px] text-slate-500">{d.id}</code>
      </header>

      <div className="overflow-y-auto px-5 pb-6 pt-3">
        {d.natural && (
          <Section title="Natural language">
            {naturalEntries.map(([lang, n]) => (
              <div key={lang} className="mb-2">
                <div className="mb-1 flex items-center gap-2 text-[10px] uppercase tracking-wider text-slate-500">
                  <span>{lang}</span>
                  {n.is_original && (
                    <span className="rounded bg-amber-100 px-1.5 py-0.5 text-amber-800">
                      original
                    </span>
                  )}
                </div>
                <p className="text-[13px] leading-relaxed text-slate-800">
                  {n.text}
                </p>
              </div>
            ))}
          </Section>
        )}

        {d.latex?.body && (
          <Section title={`LaTeX · ${d.latex.status}`}>
            <MathBlock expression={d.latex.body} />
          </Section>
        )}

        {d.domains && (
          <Section title="Domains">
            {d.domains.primary?.map((x) => (
              <Chip key={"p-" + x} color="#2f6fdb">
                {x}
              </Chip>
            ))}
            {d.domains.secondary?.map((x) => (
              <Chip key={"s-" + x}>{x}</Chip>
            ))}
          </Section>
        )}

        {d.ambient_structures && d.ambient_structures.length > 0 && (
          <Section title="Ambient structures">
            {d.ambient_structures.map((x) => (
              <Chip key={x}>{x}</Chip>
            ))}
          </Section>
        )}

        {d.ontology && (
          <Section title="Ontology">
            {d.ontology.semantic_kind?.map((x) => (
              <Chip key={"k-" + x} color="#7c4dff">
                {x}
              </Chip>
            ))}
            {d.ontology.keywords?.map((x) => (
              <Chip key={"w-" + x}>{x}</Chip>
            ))}
          </Section>
        )}

        {d.quality && (
          <Section title="Quality">
            <dl className="grid grid-cols-2 gap-x-3 gap-y-1 text-[12px]">
              {Object.entries(d.quality).map(([k, v]) => (
                <div key={k} className="flex justify-between">
                  <dt className="text-slate-500">{k}</dt>
                  <dd
                    className={clsx(
                      "font-medium",
                      v === "high" && "text-emerald-700",
                      v === "medium" && "text-amber-700",
                      v === "low" && "text-rose-700",
                    )}
                  >
                    {v}
                  </dd>
                </div>
              ))}
            </dl>
          </Section>
        )}

        {d.proved_by && d.proved_by.length > 0 && (
          <Section title={`Proved by (${d.proved_by.length})`}>
            <div className="space-y-1.5">
              {d.proved_by.map((id) => (
                <NodeLink
                  key={id}
                  id={id}
                  details={details}
                  onSelect={onSelect}
                />
              ))}
            </div>
          </Section>
        )}

        {d.depends_on && d.depends_on.length > 0 && (
          <Section title={`Depends on · concept (${d.depends_on.length})`}>
            <div className="space-y-1.5">
              {d.depends_on.map((dep) => (
                <NodeLink
                  key={dep.id}
                  id={dep.id}
                  details={details}
                  onSelect={onSelect}
                  meta={
                    <div className="mt-1 text-[10px] text-slate-500">
                      role: <span className="font-medium">{dep.role}</span>
                      {dep.confidence && (
                        <>
                          {" · "}conf:{" "}
                          <span className="font-medium">{dep.confidence}</span>
                        </>
                      )}
                    </div>
                  }
                />
              ))}
            </div>
          </Section>
        )}

        {d.generality && d.generality.length > 0 && (
          <Section title="Generality">
            <div className="space-y-1.5">
              {d.generality.map((g) => (
                <NodeLink
                  key={g.target + g.relation}
                  id={g.target}
                  details={details}
                  onSelect={onSelect}
                  meta={
                    <div className="mt-1 text-[10px] text-slate-500">
                      relation:{" "}
                      <span className="font-medium">{g.relation}</span>
                    </div>
                  }
                />
              ))}
            </div>
          </Section>
        )}

        {d.sources && d.sources.length > 0 && (
          <Section title="Sources">
            <div className="space-y-2">
              {d.sources.map((s, i) => (
                <div
                  key={i}
                  className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-[12px]"
                >
                  <div className="font-medium text-slate-800">{s.work}</div>
                  <div className="mt-1 text-[11px] text-slate-500">
                    {[
                      s.author,
                      s.edition && `ed. ${s.edition}`,
                      s.chapter && `ch. ${s.chapter}`,
                      s.section && `§${s.section}`,
                      s.theorem_label,
                      s.page && `p. ${s.page}`,
                    ]
                      .filter(Boolean)
                      .join(" · ")}
                  </div>
                  {s.locator && (
                    <div className="mt-1 text-[11px] italic text-slate-500">
                      {s.locator}
                    </div>
                  )}
                  {s.url && (
                    <a
                      className="mt-1 block break-all text-[11px] text-blue-600 hover:underline"
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {s.url}
                    </a>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {d.provenance && (
          <Section title="Provenance">
            <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-[11px]">
              {Object.entries(d.provenance).map(([k, v]) => (
                <div key={k} className="contents">
                  <dt className="text-slate-500">{k}</dt>
                  <dd className="break-all text-slate-700">{String(v)}</dd>
                </div>
              ))}
            </dl>
          </Section>
        )}

        {d.notes && (
          <Section title="Notes">
            <p className="rounded-lg border border-slate-200 bg-amber-50 px-3 py-2 text-[12px] leading-relaxed text-slate-700">
              {d.notes}
            </p>
          </Section>
        )}
      </div>
    </>
  );
};

const renderProof = (
  d: ProofDetails,
  details: NodeDetailsMap,
  onSelect: (id: string) => void,
) => (
  <>
    <header className="border-b border-slate-200 px-5 py-4">
      <div className="mb-2 flex items-center gap-2">
        <TypeBadge type="proof" />
        <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500">
          {d.status}
        </span>
        {d.style && (
          <span className="text-[11px] text-slate-500">style: {d.style}</span>
        )}
      </div>
      <h2 className="font-serif text-lg leading-tight text-slate-900">
        Proof of <span className="text-slate-700">{d.proves}</span>
      </h2>
      <code className="mt-1 block text-[11px] text-slate-500">{d.id}</code>
    </header>

    <div className="overflow-y-auto px-5 pb-6 pt-3">
      <Section title="Proves">
        <NodeLink id={d.proves} details={details} onSelect={onSelect} />
      </Section>

      {d.uses && d.uses.length > 0 && (
        <Section title={`Uses (${d.uses.length})`}>
          <div className="space-y-1.5">
            {d.uses.map((u, i) => (
              <NodeLink
                key={u.id + i}
                id={u.id}
                details={details}
                onSelect={onSelect}
                meta={
                  <div className="mt-1 text-[10px] text-slate-500">
                    role: <span className="font-medium">{u.role}</span> · conf:{" "}
                    <span className="font-medium">{u.confidence}</span>
                    {u.implicit && (
                      <span className="ml-1 rounded bg-amber-100 px-1 text-amber-700">
                        implicit
                      </span>
                    )}
                    {u.locality && <> · loc: {u.locality}</>}
                  </div>
                }
              />
            ))}
          </div>
        </Section>
      )}

      {d.parts && d.parts.length > 0 && (
        <Section title="Parts">
          <div className="space-y-1.5">
            {d.parts.map((p) => (
              <div
                key={p.name}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-[12px]"
              >
                <div className="font-medium text-slate-800">
                  {p.name}{" "}
                  <span className="ml-1 text-[10px] uppercase text-slate-500">
                    {p.kind}
                  </span>
                </div>
                {p.description && (
                  <p className="mt-1 whitespace-pre-wrap text-[12px] text-slate-600">
                    {p.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {d.quality && (
        <Section title="Quality">
          <dl className="grid grid-cols-2 gap-x-3 gap-y-1 text-[12px]">
            {Object.entries(d.quality).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <dt className="text-slate-500">{k}</dt>
                <dd className="font-medium">{v}</dd>
              </div>
            ))}
          </dl>
        </Section>
      )}

      {d.sources && d.sources.length > 0 && (
        <Section title="Sources">
          <div className="space-y-2">
            {d.sources.map((s, i) => (
              <div
                key={i}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-[12px]"
              >
                <div className="font-medium text-slate-800">{s.work}</div>
                <div className="mt-1 text-[11px] text-slate-500">
                  {[
                    s.chapter && `ch. ${s.chapter}`,
                    s.section && `§${s.section}`,
                    s.theorem_label,
                    s.page && `p. ${s.page}`,
                  ]
                    .filter(Boolean)
                    .join(" · ")}
                </div>
                {s.locator && (
                  <div className="mt-1 text-[11px] italic text-slate-500">
                    {s.locator}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {d.notes && (
        <Section title="Notes">
          <p className="rounded-lg border border-slate-200 bg-amber-50 px-3 py-2 text-[12px] leading-relaxed text-slate-700">
            {d.notes}
          </p>
        </Section>
      )}
    </div>
  </>
);

export default function DetailsPanel({ details }: Props) {
  const selectedId = useExplorer((s) => s.selectedId);
  const select = useExplorer((s) => s.select);

  if (!selectedId) {
    return (
      <aside className="flex h-full w-full flex-col items-center justify-center p-6 text-center text-sm text-slate-500">
        <div className="mb-2 text-4xl">·</div>
        Select a node to inspect.
        <p className="mt-2 max-w-xs text-xs text-slate-400">
          Pan and zoom in the canvas. Click a node to see its definition,
          proofs, and dependencies.
        </p>
      </aside>
    );
  }

  const d: NodeDetails | undefined = details[selectedId];
  if (!d) {
    return (
      <aside className="flex h-full w-full flex-col items-center justify-center p-6 text-center text-sm text-rose-600">
        Node not found in details: <code>{selectedId}</code>
      </aside>
    );
  }

  return (
    <aside className="flex h-full flex-col">
      {d.kind === "statement"
        ? renderStatement(d as StatementDetails, details, select)
        : renderProof(d as ProofDetails, details, select)}
    </aside>
  );
}
