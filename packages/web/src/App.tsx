import { useCallback, useEffect, useRef, useState } from "react";

type AnalysisSummary = Record<string, string | number | boolean>;
type EnhanceMode = "natural" | "portrait" | "land" | "food" | "glow";

type GradeLook = {
  id: string;
  name: string;
  kind: string;
  tags: string[];
};

const MODES: EnhanceMode[] = ["natural", "portrait", "land", "food", "glow"];
const GRADE_TAGS = ["all", "portrait", "food", "landscape", "street", "wedding", "cinema", "still"];

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
  const [strength, setStrength] = useState(50);
  const [mode, setMode] = useState<EnhanceMode>("natural");
  const [showMasks, setShowMasks] = useState(false);
  const [grades, setGrades] = useState<GradeLook[]>([]);
  const [gradeTag, setGradeTag] = useState("all");
  const [selectedGrade, setSelectedGrade] = useState<string | null>(null);
  const beforeRef = useRef<HTMLCanvasElement | null>(null);
  const afterRef = useRef<HTMLCanvasElement | null>(null);
  const fileRef = useRef<File | null>(null);
  const debounceRef = useRef<number | null>(null);

  const loadGrades = useCallback(async (tag: string) => {
    const q = tag === "all" ? "" : `?tag=${encodeURIComponent(tag)}`;
    const res = await fetch(`/api/grades${q}`);
    const data = await res.json();
    setGrades(data.grades ?? []);
  }, []);

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
    void loadGrades("all");
  }, [loadGrades]);

  const paintAfter = useCallback(async (dataUrl: string) => {
    const after = afterRef.current;
    if (after) {
      await paintPreview(after, dataUrl);
      setHasImage(true);
    }
  }, []);

  const loadMaskOverlay = useCallback(async (file: File) => {
    const body = new FormData();
    body.append("file", file);
    const res = await fetch("/api/process/masks", { method: "POST", body });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "mask preview failed");
    await paintAfter(data.preview);
  }, [paintAfter]);

  const runEnhance = useCallback(
    async (
      file: File,
      nextStrength: number,
      nextMode: EnhanceMode,
      masks: boolean,
      gradeId: string | null,
    ) => {
      setBusy(true);
      try {
        if (masks) {
          await loadMaskOverlay(file);
          setStatus("mask debug · cyan sky · magenta skin · yellow subject");
          return;
        }
        const body = new FormData();
        body.append("file", file);
        body.append("strength", String(nextStrength));
        body.append("mode", nextMode);
        if (gradeId) body.append("grade_id", gradeId);
        const res = await fetch("/api/process/enhance", { method: "POST", body });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "enhance failed");
        await paintAfter(data.preview);
        setAnalysis(data.analysis ?? null);
        const exp = data.analysis?.exposure_class ?? "?";
        const content = data.analysis?.content_class ?? "?";
        const grade = data.grade_id ? String(data.grade_id).replace("grade_", "") : "—";
        setStatus(
          `enhance ${nextStrength}% · ${nextMode} · grade ${grade} · ${content} · ${exp}`,
        );
      } catch (err) {
        setStatus(err instanceof Error ? err.message : "enhance failed");
      } finally {
        setBusy(false);
      }
    },
    [loadMaskOverlay, paintAfter],
  );

  const scheduleEnhance = useCallback(
    (
      nextStrength: number,
      nextMode: EnhanceMode,
      masks: boolean,
      gradeId: string | null,
    ) => {
      const file = fileRef.current;
      if (!file) return;
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
      debounceRef.current = window.setTimeout(() => {
        void runEnhance(file, nextStrength, nextMode, masks, gradeId);
      }, 280);
    },
    [runEnhance],
  );

  const openFile = useCallback(
    async (file: File) => {
      setBusy(true);
      setFileName(file.name);
      fileRef.current = file;
      try {
        const body = new FormData();
        body.append("file", file);
        const res = await fetch("/api/process/preview", { method: "POST", body });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "preview failed");
        const before = beforeRef.current;
        if (before) {
          await paintPreview(before, data.preview);
          setHasImage(true);
        }
        setAnalysis(data.analysis ?? null);
        await runEnhance(file, strength, mode, showMasks, selectedGrade);
      } catch (err) {
        setStatus(err instanceof Error ? err.message : "preview failed");
        setHasImage(false);
        setAnalysis(null);
      } finally {
        setBusy(false);
      }
    },
    [mode, runEnhance, selectedGrade, showMasks, strength],
  );

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

  return (
    <main className="shell shell-wide">
      <h1>auraforge</h1>
      <p className="tag">my version of luminar neo but free</p>
      <p className="muted">{status}</p>
      {lookCount !== null && (
        <p className="muted">{lookCount} looks registered</p>
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
            onClick={() => {
              setSelectedGrade(null);
              scheduleEnhance(strength, mode, showMasks, null);
            }}
          >
            none
          </button>
          {filteredGrades.map((g) => (
            <button
              key={g.id}
              type="button"
              className={selectedGrade === g.id ? "grade-chip active" : "grade-chip"}
              onClick={() => {
                setSelectedGrade(g.id);
                scheduleEnhance(strength, mode, showMasks, g.id);
              }}
            >
              {g.name}
            </button>
          ))}
        </div>
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
              onChange={(e) => {
                const v = Number(e.target.value);
                setStrength(v);
                scheduleEnhance(v, mode, showMasks, selectedGrade);
              }}
            />
            <span className="slider-value">{strength}</span>
          </label>
          <div className="mode-row">
            {MODES.map((m) => (
              <button
                key={m}
                type="button"
                className={m === mode ? "mode active" : "mode"}
                onClick={() => {
                  setMode(m);
                  scheduleEnhance(strength, m, showMasks, selectedGrade);
                }}
              >
                {m}
              </button>
            ))}
          </div>
          <label className="mask-toggle">
            <input
              type="checkbox"
              checked={showMasks}
              onChange={(e) => {
                const on = e.target.checked;
                setShowMasks(on);
                const file = fileRef.current;
                if (file) scheduleEnhance(strength, mode, on, selectedGrade);
              }}
            />
            show mask debug overlay
          </label>
        </section>
      )}

      <div className={`canvas-row ${hasImage ? "show" : ""}`}>
        <div className="canvas-wrap">
          <p className="label">before</p>
          <canvas ref={beforeRef} className="preview-canvas" />
        </div>
        <div className="canvas-wrap">
          <p className="label">after</p>
          <canvas ref={afterRef} className="preview-canvas" />
        </div>
      </div>

      <DebugPanel data={analysis} />
    </main>
  );
}
