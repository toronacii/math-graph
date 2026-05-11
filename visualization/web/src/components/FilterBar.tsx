import type { EntityType } from "../types";
import { TYPE_COLORS } from "../constants";
import type { BoundaryFilter, LabelMode, LayoutMode } from "../graphAnalysis";
import { TYPE_LABELS, UI_TEXT, type Locale } from "../i18n";

const ALL_TYPES: EntityType[] = [
  "axiom", "definition", "lemma", "proposition",
  "theorem", "corollary", "conjecture", "proof",
];

const BOUNDARY_OPTIONS: BoundaryFilter[] = ["all", "roots", "leaves"];
const LAYOUT_OPTIONS: LayoutMode[] = ["dagre", "breadthfirst", "cose"];
const LABEL_OPTIONS: LabelMode[] = ["title", "id"];
const LOCALE_OPTIONS: Locale[] = ["es", "en"];

interface Props {
  visibleTypes: Set<EntityType>;
  onToggleType: (type: EntityType) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  typeCounts: Record<EntityType, number>;
  locale: Locale;
  onLocaleChange: (locale: Locale) => void;
  boundaryFilter: BoundaryFilter;
  onBoundaryFilterChange: (filter: BoundaryFilter) => void;
  layoutMode: LayoutMode;
  onLayoutModeChange: (layout: LayoutMode) => void;
  labelMode: LabelMode;
  onLabelModeChange: (mode: LabelMode) => void;
  onExportPng: () => void;
  onExportSvg: () => void;
  onExportSnapshot: () => void;
}

export default function FilterBar({
  visibleTypes,
  onToggleType,
  searchQuery,
  onSearchChange,
  typeCounts,
  locale,
  onLocaleChange,
  boundaryFilter,
  onBoundaryFilterChange,
  layoutMode,
  onLayoutModeChange,
  labelMode,
  onLabelModeChange,
  onExportPng,
  onExportSvg,
  onExportSnapshot,
}: Props) {
  const text = UI_TEXT[locale];

  return (
    <div className="filter-bar">
      <div className="toolbar-group toolbar-group--search">
        <label className="toolbar-label" htmlFor="graph-search">
          {text.search}
        </label>
        <input
          id="graph-search"
          type="text"
          className="search-input"
          placeholder={text.searchPlaceholder}
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      <div className="toolbar-group">
        <span className="toolbar-label">{text.boundary}</span>
        <div className="segmented-control">
          {BOUNDARY_OPTIONS.map((option) => (
            <button
              key={option}
              className={`segment ${boundaryFilter === option ? "segment--active" : ""}`}
              onClick={() => onBoundaryFilterChange(option)}
            >
              {text.boundaryOptions[option]}
            </button>
          ))}
        </div>
      </div>

      <div className="toolbar-group">
        <label className="toolbar-label" htmlFor="layout-mode">
          {text.layout}
        </label>
        <select
          id="layout-mode"
          className="toolbar-select"
          value={layoutMode}
          onChange={(e) => onLayoutModeChange(e.target.value as LayoutMode)}
        >
          {LAYOUT_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {text.layoutOptions[option]}
            </option>
          ))}
        </select>
      </div>

      <div className="toolbar-group">
        <label className="toolbar-label" htmlFor="label-mode">
          {text.labels}
        </label>
        <select
          id="label-mode"
          className="toolbar-select"
          value={labelMode}
          onChange={(e) => onLabelModeChange(e.target.value as LabelMode)}
        >
          {LABEL_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {text.labelOptions[option]}
            </option>
          ))}
        </select>
      </div>

      <div className="toolbar-group">
        <label className="toolbar-label" htmlFor="locale-mode">
          {text.language}
        </label>
        <select
          id="locale-mode"
          className="toolbar-select"
          value={locale}
          onChange={(e) => onLocaleChange(e.target.value as Locale)}
        >
          {LOCALE_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option === "es" ? "Español" : "English"}
            </option>
          ))}
        </select>
      </div>

      <div className="toolbar-group toolbar-group--exports">
        <span className="toolbar-label">{text.export}</span>
        <div className="action-row">
          <button className="action-btn" onClick={onExportPng}>
            PNG
          </button>
          <button className="action-btn" onClick={onExportSvg}>
            SVG
          </button>
          <button className="action-btn" onClick={onExportSnapshot}>
            Snapshot
          </button>
        </div>
      </div>

      <div className="type-filters">
        {ALL_TYPES.map((type) => {
          const count = typeCounts[type] ?? 0;
          if (count === 0) return null;
          const active = visibleTypes.has(type);
          return (
            <button
              key={type}
              className={`type-toggle ${active ? "active" : ""}`}
              style={{
                borderColor: TYPE_COLORS[type],
                backgroundColor: active ? TYPE_COLORS[type] : "transparent",
                color: active ? "#fff" : TYPE_COLORS[type],
              }}
              onClick={() => onToggleType(type)}
            >
              {TYPE_LABELS[locale][type]} ({count})
            </button>
          );
        })}
      </div>
    </div>
  );
}
