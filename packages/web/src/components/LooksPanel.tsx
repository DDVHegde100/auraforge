type LookItem = {
  id: string;
  name: string;
  tags: string[];
  experimental?: boolean;
};

type Props = {
  kind: "grades" | "cameras" | "signatures";
  items: LookItem[];
  tags: string[];
  activeTag: string;
  selectedId: string | null;
  lookAmount: number;
  live: boolean;
  onTag: (tag: string) => void;
  onSelect: (id: string | null) => void;
  onLookAmount: (v: number) => void;
};

export function LooksPanel({
  kind,
  items,
  tags,
  activeTag,
  selectedId,
  lookAmount,
  live,
  onTag,
  onSelect,
  onLookAmount,
}: Props) {
  const filtered =
    activeTag === "all"
      ? items
      : items.filter((i) => i.tags.map((t) => t.toLowerCase()).includes(activeTag));

  return (
    <div className="looks-panel">
      <div className="tag-row">
        {tags.map((tag) => (
          <button
            key={tag}
            type="button"
            className={tag === activeTag ? "tag-chip active" : "tag-chip"}
            onClick={() => onTag(tag)}
          >
            {tag}
          </button>
        ))}
      </div>
      <div className="look-grid">
        <button
          type="button"
          className={selectedId === null ? "look-card active" : "look-card"}
          onClick={() => onSelect(null)}
        >
          <span className="look-card-name">none</span>
        </button>
        {filtered.map((item) => (
          <button
            key={item.id}
            type="button"
            className={selectedId === item.id ? "look-card active" : "look-card"}
            onClick={() => onSelect(item.id)}
          >
            <span className="look-card-name">{item.name}</span>
            {kind === "signatures" && item.experimental && <span className="look-card-badge">exp</span>}
          </button>
        ))}
      </div>
      {selectedId != null && (
        <label className="studio-slider look-strength">
          <div className="studio-slider-head">
            <span>Strength</span>
            <span className="studio-slider-val">{lookAmount}</span>
          </div>
          <input
            type="range"
            min={0}
            max={100}
            value={lookAmount}
            onChange={(e) => onLookAmount(Number(e.target.value))}
            onInput={(e) => onLookAmount(Number((e.target as HTMLInputElement).value))}
          />
        </label>
      )}
      {live && selectedId != null && (
        <span className="live-pill">updating preview…</span>
      )}
    </div>
  );
}
