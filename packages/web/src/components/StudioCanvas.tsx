import { IconCompare, IconUpload } from "./icons";

type Props = {
  hasImage: boolean;
  displayBefore: string | null;
  afterUrl: string | null;
  scrub: number;
  onScrub: (v: number) => void;
  isLiveRender: boolean;
  enhanceMs: number | null;
  hdPreview: boolean;
  previewMax: number;
  busy: boolean;
  dragOver: boolean;
  fileName: string | null;
  onDrop: (e: React.DragEvent) => void;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: () => void;
  onPickFile: () => void;
};

export function StudioCanvas({
  hasImage,
  displayBefore,
  afterUrl,
  scrub,
  onScrub,
  isLiveRender,
  enhanceMs,
  hdPreview,
  previewMax,
  busy,
  dragOver,
  fileName,
  onDrop,
  onDragOver,
  onDragLeave,
  onPickFile,
}: Props) {
  return (
    <div
      className={`studio-canvas ${dragOver ? "drag-over" : ""} ${busy && !isLiveRender ? "busy" : ""}`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      {!hasImage || !displayBefore ? (
        <div className="canvas-empty">
          <IconUpload size={40} className="canvas-empty-icon" />
          <p className="canvas-empty-title">drop a photo here</p>
          <p className="canvas-empty-hint">JPEG · PNG · HEIC · TIFF · ARW</p>
          <button type="button" className="studio-btn primary" onClick={onPickFile}>
            <IconUpload size={16} /> open photo
          </button>
        </div>
      ) : (
        <>
          <div className="canvas-toolbar">
            <span className="canvas-filename">{fileName}</span>
            <div className="canvas-badges">
              {isLiveRender && <span className="live-pill">live</span>}
              {enhanceMs != null && (
                <span className="canvas-timing">
                  {enhanceMs}ms · {hdPreview ? "hd" : "live"} {previewMax}px
                </span>
              )}
            </div>
          </div>

          <div className="canvas-stage">
            {afterUrl ? (
              <img src={afterUrl} alt="edited" className="canvas-img" draggable={false} />
            ) : (
              <img src={displayBefore} alt="processing" className="canvas-img canvas-dim" draggable={false} />
            )}
            <img
              src={displayBefore}
              alt="before"
              className="canvas-img canvas-before"
              style={{ clipPath: `inset(0 ${100 - scrub}% 0 0)` }}
              draggable={false}
            />
            {isLiveRender && <div className="canvas-live-shimmer" aria-hidden />}
          </div>

          <div className="canvas-footer">
            <IconCompare size={16} className="canvas-footer-icon" />
            <input
              type="range"
              min={0}
              max={100}
              value={scrub}
              className="canvas-scrub"
              onChange={(e) => onScrub(Number(e.target.value))}
              aria-label="before after compare"
            />
            <span className="canvas-scrub-label">{scrub < 50 ? "before" : scrub > 50 ? "after" : "compare"}</span>
          </div>
        </>
      )}
    </div>
  );
}
