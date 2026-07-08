import { useCallback, useEffect, useRef, useState } from "react";

type AnalysisSummary = Record<string, string | number | boolean>;

async function paintPreview(canvas: HTMLCanvasElement, dataUrl: string) {
  const img = new Image();
  img.decoding = "async";
  const loaded = new Promise<void>((resolve, reject) => {
    img.onload = () => resolve();
    img.onerror = () => reject(new Error("image decode failed"));
  });
  img.src = dataUrl;
  await loaded;
  const maxW = canvas.parentElement?.clientWidth || 640;
  const scale = Math.min(1, maxW / img.width);
  const w = Math.max(1, Math.round(img.width * scale));
  const h = Math.max(1, Math.round(img.height * scale));
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.clearRect(0, 0, w, h);
  ctx.drawImage(img, 0, 0, w, h);
}

function DebugPanel({ data }: { data: AnalysisSummary | null }) {
  if (!data) return null;
  const rows = Object.entries(data);
  return (
    <details className="debug-panel" open>
      <summary>scene analysis</summary>
      <dl className="debug-grid">
        {rows.map(([k, v]) => (
          <div key={k} className="debug-row">
            <dt>{k.replace(/_/g, " ")}</dt>
            <dd>{typeof v === "number" ? v.toFixed(3) : String(v)}</dd>
          </div>
        ))}
      </dl>
    </details>
  );
}

export default function App() {
  const [status, setStatus] = useState("checking api…");
  const [lookCount, setLookCount] = useState<number | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [hasImage, setHasImage] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisSummary | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/health").then((r) => r.json()),
      fetch("/api/looks").then((r) => r.json()),
    ])
      .then(([health, looks]) => {
        setStatus(health.ok ? `engine ${health.engine}` : "api down");
        setLookCount(looks.count ?? 0);
      })
      .catch(() => setStatus("api offline — run ./dev.sh"));
  }, []);

  const openFile = useCallback(async (file: File) => {
    setBusy(true);
    setFileName(file.name);
    try {
      const body = new FormData();
      body.append("file", file);
      const res = await fetch("/api/process/preview", { method: "POST", body });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "preview failed");
      const canvas = canvasRef.current;
      if (canvas) {
        await paintPreview(canvas, data.preview);
        setHasImage(true);
      }
      setAnalysis(data.analysis ?? null);
      const exp = data.analysis?.exposure_class ?? "?";
      const content = data.analysis?.content_class ?? "?";
      setStatus(`before ${data.width}×${data.height} · ${content} · ${exp}`);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "preview failed");
      setHasImage(false);
      setAnalysis(null);
    } finally {
      setBusy(false);
    }
  }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) void openFile(file);
  };

  return (
    <main className="shell">
      <h1>auraforge</h1>
      <p className="tag">my version of luminar neo but free</p>
      <p className="muted">{status}</p>
      {lookCount !== null && (
        <p className="muted">{lookCount} looks registered (stubs for now)</p>
      )}

      <div
        className={`dropzone ${dragOver ? "active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <p>{busy ? "loading…" : "drop a local photo here"}</p>
        <label className="pick">
          or choose file
          <input
            type="file"
            accept="image/*,.arw,.dng,.nef,.cr2,.tif,.tiff"
            hidden
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void openFile(file);
            }}
          />
        </label>
      </div>

      {fileName && <p className="muted">{fileName}</p>}

      <div className={`canvas-wrap ${hasImage ? "show" : ""}`}>
        <p className="label">before</p>
        <canvas ref={canvasRef} className="before-canvas" />
      </div>

      <DebugPanel data={analysis} />
    </main>
  );
}
