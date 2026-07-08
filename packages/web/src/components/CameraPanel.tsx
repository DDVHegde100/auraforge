import { cameraSwatch, type CameraItem } from "../lib/cameras";

type Props = {
  items: CameraItem[];
  tags: string[];
  activeTag: string;
  selectedId: string | null;
  lookAmount: number;
  live: boolean;
  onTag: (tag: string) => void;
  onSelect: (id: string | null) => void;
  onLookAmount: (v: number) => void;
};

export function CameraPanel({
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

  const selected = items.find((i) => i.id === selectedId);

  return (
    <div className="camera-panel">
      <p className="panel-title">Camera emulation</p>
      <p className="panel-hint">Film-stock color science + lens character. Strength scales the full camera chain.</p>

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

      <div className="camera-grid">
        <button
          type="button"
          className={selectedId === null ? "camera-card active" : "camera-card"}
          onClick={() => onSelect(null)}
        >
          <span className="camera-swatch none" />
          <span className="camera-card-name">none</span>
        </button>
        {filtered.map((cam) => (
          <button
            key={cam.id}
            type="button"
            className={selectedId === cam.id ? "camera-card active" : "camera-card"}
            onClick={() => onSelect(cam.id)}
          >
            <span
              className="camera-swatch"
              style={{ background: cameraSwatch(cam.name, cam.meta) }}
            />
            <span className="camera-card-name">{cam.name}</span>
            {cam.meta?.format && <span className="camera-card-sub">{cam.meta.format}</span>}
          </button>
        ))}
      </div>

      {selected && selected.meta && (
        <div className="camera-detail">
          <p className="camera-detail-title">{selected.name}</p>
          {selected.meta.lens && <p className="camera-detail-row"><span>Lens</span>{selected.meta.lens}</p>}
          {selected.meta.stock && <p className="camera-detail-row"><span>Stock</span>{selected.meta.stock}</p>}
          {selected.meta.era && <p className="camera-detail-row"><span>Era</span>{selected.meta.era}</p>}
          {selected.meta.character && <p className="camera-detail-desc">{selected.meta.character}</p>}
          {selected.notes && <p className="camera-detail-desc muted">{selected.notes}</p>}
        </div>
      )}

      {selectedId != null && (
        <label className="studio-slider look-strength">
          <div className="studio-slider-head">
            <span>Camera intensity</span>
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
      {live && selectedId != null && <span className="live-pill">updating preview…</span>}
    </div>
  );
}
