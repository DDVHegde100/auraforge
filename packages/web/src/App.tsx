import { useCallback, useEffect, useState } from "react";

export default function App() {
  const [status, setStatus] = useState("checking api…");
  const [lookCount, setLookCount] = useState<number | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [dragOver, setDragOver] = useState(false);

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
      setPreview(data.preview);
      setStatus(`preview ${data.width}×${data.height}`);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "preview failed");
      setPreview(null);
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
      {preview && (
        <div className="preview-wrap">
          <img src={preview} alt="preview" className="preview" />
        </div>
      )}
    </main>
  );
}
