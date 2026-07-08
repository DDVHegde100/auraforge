import { useCallback, useEffect, useRef, useState } from "react";
import { ErrorBanner } from "../components/ErrorBanner";

type AnalysisSummary = Record<string, string | number | boolean>;
type EnhanceMode = "natural" | "portrait" | "land" | "food" | "glow";
type ExportFormat = "jpeg" | "tiff";

type LookItem = {
  id: string;
  name: string;
  kind: string;
  tags: string[];
  experimental?: boolean;
};

type HistorySnap = {
  strength: number;
  mode: EnhanceMode;
  gradeId: string | null;
  signatureId: string | null;
  showMasks: boolean;
  proSafe: boolean;
  useA6000: boolean;
};

const MODES: EnhanceMode[] = ["natural", "portrait", "land", "food", "glow"];
const GRADE_TAGS = ["all", "portrait", "food", "landscape", "street", "wedding", "cinema", "still"];

async function paintPreview(canvas: HTMLCanvasElement, dataUrl: string) {
  const img = new Image();
  img.decoding = "async";
  await new Promise<void>((resolve, reject) => {
    img.onload = () => resolve();
    img.onerror = () => reject(new Error("image decode failed"));
  });
  img.src = dataUrl;
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
  return (
    <details className="debug-panel" open>
      <summary>scene analysis</summary>
      <dl className="debug-grid">
        {Object.entries(data).map(([k, v]) => (
          <div key={k} className="debug-row">
            <dt>{k.replace(/_/g, " ")}</dt>
            <dd>{typeof v === "number" ? v.toFixed(3) : String(v)}</dd>
          </div>
        ))}
      </dl>
    </details>
  );
}

export default function Editor() {
  const [status, setStatus] = useState("checking api…");
  const [lookCount, setLookCount] = useState<number | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [hasImage, setHasImage] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisSummary | null>(null);
  const [strength, setStrength] = useState(50);
  const [mode, setMode] = useState<EnhanceMode>("natural");
  const [showMasks, setShowMasks] = useState(false);
  const [proSafe, setProSafe] = useState(true);
  const [useA6000, setUseA6000] = useState(false);
  const [grades, setGrades] = useState<LookItem[]>([]);
  const [signatures, setSignatures] = useState<LookItem[]>([]);
  const [gradeTag, setGradeTag] = useState("all");
  const [selectedGrade, setSelectedGrade] = useState<string | null>(null);
  const [selectedSignature, setSelectedSignature] = useState<string | null>(null);
  const [beforeUrl, setBeforeUrl] = useState<string | null>(null);
  const [afterUrl, setAfterUrl] = useState<string | null>(null);
  const [scrub, setScrub] = useState(50);
  const [exportFormat, setExportFormat] = useState<ExportFormat>("jpeg");
  const [history, setHistory] = useState<HistorySnap[]>([]);
  const [offline, setOffline] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [cacheHits, setCacheHits] = useState<number | null>(null);
  const [batchFolder, setBatchFolder] = useState("");
  const [batchOut, setBatchOut] = useState("");
  const [batchResult, setBatchResult] = useState<string | null>(null);
  const beforeRef = useRef<HTMLCanvasElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const fileRef = useRef<File | null>(null);
  const debounceRef = useRef<number | null>(null);

  const loadGrades = useCallback(async (tag: string) => {
    const q = tag === "all" ? "" : `?tag=${encodeURIComponent(tag)}`;
    const res = await fetch(`/api/grades${q}`);
    if (!res.ok) throw new Error("grades unavailable");
    const data = await res.json();
    setGrades(data.grades ?? []);
  }, []);

  const loadSignatures = useCallback(async () => {
    const res = await fetch("/api/signatures");
    if (!res.ok) throw new Error("signatures unavailable");
    const data = await res.json();
    setSignatures(data.signatures ?? []);
  }, []);

  const refreshHealth = useCallback(async () => {
    try {
      const [health, looks, cache] = await Promise.all([
        fetch("/api/health").then((r) => r.json()),
        fetch("/api/looks").then((r) => r.json()),
        fetch("/api/cache/stats").then((r) => r.json()),
      ]);
      setOffline(false);
      setErrorMsg(null);
      setStatus(health.ok ? `engine ${health.engine}` : "api down");
      setLookCount(looks.count ?? 0);
      setCacheHits(typeof cache.hits === "number" ? cache.hits : null);
    } catch {
      setOffline(true);
      setErrorMsg("api offline — run ./dev.sh from the auraforge repo");
      setStatus("offline");
    }
  }, []);

  useEffect(() => {
    void refreshHealth();
    void loadGrades("all");
    void loadSignatures();
  }, [loadGrades, loadSignatures, refreshHealth]);

  const pushHistory = useCallback((snap: HistorySnap) => {
    setHistory((prev) => [...prev.slice(-19), snap]);
  }, []);

  const runEnhance = useCallback(
    async (
      file: File,
      snap: HistorySnap,
      opts?: { skipHistory?: boolean },
    ) => {
      setBusy(true);
      setErrorMsg(null);
      try {
        if (snap.showMasks) {
          const body = new FormData();
          body.append("file", file);
          const res = await fetch("/api/process/masks", { method: "POST", body });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || "mask preview failed");
          setAfterUrl(data.preview);
          setStatus("mask debug · cyan sky · magenta skin · yellow subject");
          setOffline(false);
          return;
        }
        const body = new FormData();
        body.append("file", file);
        body.append("strength", String(snap.strength));
        body.append("mode", snap.mode);
        body.append("pro_safe", snap.proSafe ? "true" : "false");
        body.append("use_a6000_profile", snap.useA6000 ? "true" : "false");
        if (snap.gradeId) body.append("grade_id", snap.gradeId);
        if (snap.signatureId) body.append("signature_id", snap.signatureId);
        const res = await fetch("/api/process/enhance", { method: "POST", body });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "enhance failed");
        setAfterUrl(data.preview);
        setAnalysis(data.analysis ?? null);
        setOffline(false);
        const sig = data.signature_id ? String(data.signature_id).replace("sig_", "") : "—";
        const clamped = data.signature_clamped ? " · clamped" : "";
        const cached = data.cached ? " · cached" : "";
        const a6000 = data.a6000_profile ? " · a6000" : "";
        setStatus(
          `enhance ${snap.strength}% · ${snap.mode} · sig ${sig}${clamped}${cached}${a6000}`,
        );
        if (!opts?.skipHistory) pushHistory(snap);
      } catch (err) {
        const msg = err instanceof Error ? err.message : "enhance failed";
        setErrorMsg(msg);
        setStatus(msg);
        if (msg.includes("fetch") || msg.includes("network")) setOffline(true);
      } finally {
        setBusy(false);
      }
    },
    [pushHistory],
  );

  const currentSnap = useCallback(
    (): HistorySnap => ({
      strength,
      mode,
      gradeId: selectedGrade,
      signatureId: selectedSignature,
      showMasks,
      proSafe,
      useA6000,
    }),
    [mode, proSafe, selectedGrade, selectedSignature, showMasks, strength, useA6000],
  );

  const scheduleEnhance = useCallback(
    (snap: HistorySnap) => {
      const file = fileRef.current;
      if (!file) return;
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
      debounceRef.current = window.setTimeout(() => {
        void runEnhance(file, snap);
      }, 280);
    },
    [runEnhance],
  );

  const openFile = useCallback(
    async (file: File) => {
      setBusy(true);
      setFileName(file.name);
      fileRef.current = file;
      setHistory([]);
      setErrorMsg(null);
      try {
        const body = new FormData();
        body.append("file", file);
        const res = await fetch("/api/process/preview", { method: "POST", body });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "preview failed");
        setBeforeUrl(data.preview);
        const before = beforeRef.current;
        if (before) await paintPreview(before, data.preview);
        setHasImage(true);
        setAnalysis(data.analysis ?? null);
        setOffline(false);
        const snap = currentSnap();
        await runEnhance(file, snap);
      } catch (err) {
        const msg = err instanceof Error ? err.message : "preview failed";
        setErrorMsg(msg);
        setStatus(msg);
        setHasImage(false);
        setAnalysis(null);
      } finally {
        setBusy(false);
      }
    },
    [currentSnap, runEnhance],
  );

  const undo = useCallback(() => {
    if (history.length < 2) return;
    const prev = history[history.length - 2];
    setHistory((h) => h.slice(0, -1));
    setStrength(prev.strength);
    setMode(prev.mode);
    setSelectedGrade(prev.gradeId);
    setSelectedSignature(prev.signatureId);
    setShowMasks(prev.showMasks);
    setProSafe(prev.proSafe);
    setUseA6000(prev.useA6000);
    const file = fileRef.current;
    if (file) void runEnhance(file, prev, { skipHistory: true });
  }, [history, runEnhance]);

  const exportImage = useCallback(async () => {
    const file = fileRef.current;
    if (!file) return;
    setBusy(true);
    try {
      const snap = currentSnap();
      const body = new FormData();
      body.append("file", file);
      body.append("strength", String(snap.strength));
      body.append("mode", snap.mode);
      body.append("fmt", snap.showMasks ? "jpeg" : exportFormat);
      body.append("pro_safe", snap.proSafe ? "true" : "false");
      body.append("use_a6000_profile", snap.useA6000 ? "true" : "false");
      if (snap.gradeId) body.append("grade_id", snap.gradeId);
      if (snap.signatureId) body.append("signature_id", snap.signatureId);
      const res = await fetch("/api/process/export", { method: "POST", body });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "export failed");
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = exportFormat === "tiff" ? "auraforge.tif" : "auraforge.jpg";
      a.click();
      URL.revokeObjectURL(url);
      setStatus(`exported ${exportFormat}`);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "export failed");
    } finally {
      setBusy(false);
    }
  }, [currentSnap, exportFormat]);

  const runBatch = useCallback(async () => {
    if (!batchFolder.trim()) return;
    setBusy(true);
    setBatchResult(null);
    setErrorMsg(null);
    try {
      const snap = currentSnap();
      const body = new FormData();
      body.append("folder", batchFolder.trim());
      if (batchOut.trim()) body.append("out_dir", batchOut.trim());
      body.append("strength", String(snap.strength));
      body.append("mode", snap.mode);
      body.append("pro_safe", snap.proSafe ? "true" : "false");
      body.append("use_a6000_profile", snap.useA6000 ? "true" : "false");
      if (snap.gradeId) body.append("grade_id", snap.gradeId);
      if (snap.signatureId) body.append("signature_id", snap.signatureId);
      const res = await fetch("/api/process/batch", { method: "POST", body });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "batch failed");
      setBatchResult(`batch ok ${data.ok}/${data.count}${data.output_dir ? ` → ${data.output_dir}` : ""}`);
      setStatus(`batch ${data.ok}/${data.count}`);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "batch failed");
    } finally {
      setBusy(false);
    }
  }, [batchFolder, batchOut, currentSnap]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === "z") {
        e.preventDefault();
        undo();
      }
      if (mod && e.key === "e") {
        e.preventDefault();
        if (hasImage) void exportImage();
      }
      if (mod && e.key === "o") {
        e.preventDefault();
        fileInputRef.current?.click();
      }
      if (!mod && hasImage && beforeUrl && afterUrl) {
        if (e.key === "ArrowLeft") setScrub((s) => Math.max(0, s - 5));
        if (e.key === "ArrowRight") setScrub((s) => Math.min(100, s + 5));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [afterUrl, beforeUrl, exportImage, hasImage, undo]);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) void openFile(file);
  };

  const filteredGrades =
    gradeTag === "all"
      ? grades
      : grades.filter((g) => g.tags.map((t) => t.toLowerCase()).includes(gradeTag));

  const applySnap = (partial: Partial<HistorySnap>) => {
    const snap: HistorySnap = { ...currentSnap(), ...partial };
    if (partial.strength !== undefined) setStrength(partial.strength);
    if (partial.mode !== undefined) setMode(partial.mode);
    if (partial.gradeId !== undefined) setSelectedGrade(partial.gradeId);
    if (partial.signatureId !== undefined) setSelectedSignature(partial.signatureId);
    if (partial.showMasks !== undefined) setShowMasks(partial.showMasks);
    if (partial.proSafe !== undefined) setProSafe(partial.proSafe);
    if (partial.useA6000 !== undefined) setUseA6000(partial.useA6000);
    scheduleEnhance(snap);
  };

  return (
    <main className="shell shell-wide editor-shell">
      <header className="editor-header">
        <div>
          <h1>auraforge</h1>
          <p className="tag">my version of luminar neo but free</p>
        </div>
        <nav className="editor-nav">
          <a href="/" className="active">
            editor
          </a>
          <a href="/showcase">showcase</a>
          <a href="/research">research</a>
        </nav>
      </header>

      <div className="editor-status-row">
        <p className="muted">{status}</p>
        {lookCount !== null && <p className="muted">{lookCount} looks</p>}
        {cacheHits !== null && <p className="muted">cache hits {cacheHits}</p>}
        <p className="muted shortcuts-hint">⌘Z undo · ⌘E export · ⌘O open · ←→ scrub</p>
      </div>

      {(offline || errorMsg) && (
        <ErrorBanner
          message={errorMsg || "api offline — run ./dev.sh"}
          offline={offline}
          onRetry={() => void refreshHealth()}
        />
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
            ref={fileInputRef}
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

      <section className="batch-panel">
        <p className="section-label">batch folder (local path)</p>
        <div className="batch-row">
          <input
            className="batch-input"
            type="text"
            placeholder="/Users/you/Photos/inbox"
            value={batchFolder}
            onChange={(e) => setBatchFolder(e.target.value)}
          />
          <input
            className="batch-input"
            type="text"
            placeholder="output dir (optional)"
            value={batchOut}
            onChange={(e) => setBatchOut(e.target.value)}
          />
          <button type="button" className="tool-btn primary" disabled={busy || !batchFolder.trim()} onClick={() => void runBatch()}>
            run batch
          </button>
        </div>
        {batchResult && <p className="muted">{batchResult}</p>}
      </section>

      <section className="grade-browser">
        <p className="section-label">grades</p>
        <div className="mode-row">
          {GRADE_TAGS.map((tag) => (
            <button
              key={tag}
              type="button"
              className={tag === gradeTag ? "mode active" : "mode"}
              onClick={() => {
                setGradeTag(tag);
                void loadGrades(tag);
              }}
            >
              {tag}
            </button>
          ))}
        </div>
        <div className="grade-list">
          <button
            type="button"
            className={selectedGrade === null ? "grade-chip active" : "grade-chip"}
            onClick={() => applySnap({ gradeId: null })}
          >
            none
          </button>
          {filteredGrades.map((g) => (
            <button
              key={g.id}
              type="button"
              className={selectedGrade === g.id ? "grade-chip active" : "grade-chip"}
              onClick={() => applySnap({ gradeId: g.id })}
            >
              {g.name}
            </button>
          ))}
        </div>
      </section>

      <section className="grade-browser">
        <p className="section-label">signatures</p>
        <div className="sig-gallery">
          <button
            type="button"
            className={selectedSignature === null ? "sig-thumb active" : "sig-thumb"}
            onClick={() => applySnap({ signatureId: null })}
          >
            none
          </button>
          {signatures.map((s) => (
            <button
              key={s.id}
              type="button"
              className={selectedSignature === s.id ? "sig-thumb active" : "sig-thumb"}
              onClick={() => applySnap({ signatureId: s.id })}
            >
              <span className="sig-name">{s.name}</span>
              {s.experimental && <span className="sig-badge">exp</span>}
            </button>
          ))}
        </div>
        <label className="mask-toggle">
          <input
            type="checkbox"
            checked={proSafe}
            onChange={(e) => applySnap({ proSafe: e.target.checked })}
          />
          pro-safe clamp (experimental sigs max 60%)
        </label>
        <label className="mask-toggle">
          <input
            type="checkbox"
            checked={useA6000}
            onChange={(e) => applySnap({ useA6000: e.target.checked })}
          />
          a6000 base profile (auto when EXIF says ILCE-6000)
        </label>
      </section>

      {hasImage && (
        <section className="enhance-controls">
          <label className="slider-label">
            ai enhance
            <input
              type="range"
              min={0}
              max={100}
              value={strength}
              onChange={(e) => applySnap({ strength: Number(e.target.value) })}
            />
            <span className="slider-value">{strength}</span>
          </label>
          <div className="mode-row">
            {MODES.map((m) => (
              <button
                key={m}
                type="button"
                className={m === mode ? "mode active" : "mode"}
                onClick={() => applySnap({ mode: m })}
              >
                {m}
              </button>
            ))}
          </div>
          <label className="mask-toggle">
            <input
              type="checkbox"
              checked={showMasks}
              onChange={(e) => applySnap({ showMasks: e.target.checked })}
            />
            show mask debug overlay
          </label>
          <div className="toolbar-row">
            <button type="button" className="tool-btn" disabled={history.length < 2} onClick={undo}>
              undo
            </button>
            <select
              className="export-select"
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value as ExportFormat)}
            >
              <option value="jpeg">jpeg</option>
              <option value="tiff">tiff 16-bit</option>
            </select>
            <button type="button" className="tool-btn primary" onClick={() => void exportImage()}>
              export
            </button>
          </div>
        </section>
      )}

      {hasImage && beforeUrl && afterUrl && (
        <section className="compare-section">
          <p className="label">before / after</p>
          <div className="compare-wrap">
            <img src={afterUrl} alt="after" className="compare-img" />
            <img
              src={beforeUrl}
              alt="before"
              className="compare-img compare-before"
              style={{ clipPath: `inset(0 ${100 - scrub}% 0 0)` }}
            />
          </div>
          <label className="slider-label scrub-label">
            scrub
            <input
              type="range"
              min={0}
              max={100}
              value={scrub}
              onChange={(e) => setScrub(Number(e.target.value))}
            />
            <span className="slider-value">{scrub}</span>
          </label>
        </section>
      )}

      <canvas ref={beforeRef} className="hidden-canvas" aria-hidden />

      <DebugPanel data={analysis} />
    </main>
  );
}
