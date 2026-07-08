import { useCallback, useEffect, useRef, useState } from "react";
import { StudioCanvas } from "../components/StudioCanvas";
import { LooksPanel } from "../components/LooksPanel";
import {
  IconCamera,
  IconEnhance,
  IconExport,
  IconFolder,
  IconFx,
  IconPalette,
  IconSliders,
  IconUndo,
  IconUpload,
} from "../components/icons";
import { TonePanel } from "../components/TonePanel";
import { ErrorBanner } from "../components/ErrorBanner";
import { appendTuneToForm, DEFAULT_TUNE, type TuneState } from "../lib/tune";
import { apiFetch } from "../lib/api";
import { exportImage as runExport, triggerDownload, type ExportProgress } from "../lib/export";
import type { CameraItem } from "../lib/cameras";
import { CameraPanel } from "../components/CameraPanel";
import {
  fileMeta,
  normalizeForUpload,
  parseApiError,
  readLocalPreview,
  validateFile,
  type FileMeta,
  type UploadStep,
} from "../lib/upload";

type AnalysisSummary = Record<string, string | number | boolean>;
type EnhanceMode = "natural" | "portrait" | "land" | "food" | "glow";
type ExportFormat = "jpeg" | "tiff";

type LookItem = {
  id: string;
  name: string;
  kind: string;
  tags: string[];
  experimental?: boolean;
  meta?: CameraItem["meta"];
  notes?: string;
};

type HistorySnap = {
  strength: number;
  mode: EnhanceMode;
  gradeId: string | null;
  cameraId: string | null;
  signatureId: string | null;
  showMasks: boolean;
  proSafe: boolean;
  useA6000: boolean;
  tune: TuneState;
};

const MODES: EnhanceMode[] = ["natural", "portrait", "land", "food", "glow"];
const GRADE_TAGS = ["all", "portrait", "food", "landscape", "street", "wedding", "cinema", "still"];
const CAMERA_TAGS = ["all", "pro", "film", "digital", "vintage", "cinema", "flash", "fuji", "lomo"];
const PREVIEW_LIVE = 1280;
const PREVIEW_HD = 1800;
const LIVE_DEBOUNCE_MS = 28;

type SidebarTab = "enhance" | "tone" | "looks" | "cameras" | "fx" | "settings";

function formatApiError(err: unknown, hint?: string | null): string {
  const base = err instanceof Error ? err.message : String(err);
  return hint ? `${base} — ${hint}` : base;
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
  const [strength, setStrength] = useState(80);
  const [tune, setTune] = useState<TuneState>(DEFAULT_TUNE);
  const [isLiveRender, setIsLiveRender] = useState(false);
  const [mode, setMode] = useState<EnhanceMode>("natural");
  const [showMasks, setShowMasks] = useState(false);
  const [proSafe, setProSafe] = useState(true);
  const [useA6000, setUseA6000] = useState(false);
  const [hdPreview, setHdPreview] = useState(false);
  const [sidebarTab, setSidebarTab] = useState<SidebarTab>("enhance");
  const [grades, setGrades] = useState<LookItem[]>([]);
  const [cameras, setCameras] = useState<CameraItem[]>([]);
  const [signatures, setSignatures] = useState<LookItem[]>([]);
  const [gradeTag, setGradeTag] = useState("all");
  const [cameraTag, setCameraTag] = useState("all");
  const [selectedGrade, setSelectedGrade] = useState<string | null>(null);
  const [selectedCamera, setSelectedCamera] = useState<string | null>(null);
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
  const [uploadStep, setUploadStep] = useState<UploadStep>("idle");
  const [uploadMeta, setUploadMeta] = useState<FileMeta | null>(null);
  const [convertNote, setConvertNote] = useState<string | null>(null);
  const [localPreview, setLocalPreview] = useState<string | null>(null);
  const [serverWidth, setServerWidth] = useState<number | null>(null);
  const [serverHeight, setServerHeight] = useState<number | null>(null);
  const [previewMs, setPreviewMs] = useState<number | null>(null);
  const [enhanceMs, setEnhanceMs] = useState<number | null>(null);
  const [exportProgress, setExportProgress] = useState<ExportProgress | null>(null);
  const [errorHint, setErrorHint] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const fileRef = useRef<File | null>(null);
  const sessionIdRef = useRef<string | null>(null);
  const enhanceAbortRef = useRef<AbortController | null>(null);
  const enhanceSeqRef = useRef(0);
  const localPreviewRef = useRef<string | null>(null);
  const debounceRef = useRef<number | null>(null);
  const previewMaxRef = useRef(PREVIEW_LIVE);
  previewMaxRef.current = hdPreview ? PREVIEW_HD : PREVIEW_LIVE;

  const revokeLocalPreview = useCallback(() => {
    if (localPreviewRef.current) {
      URL.revokeObjectURL(localPreviewRef.current);
      localPreviewRef.current = null;
    }
  }, []);

  const loadGrades = useCallback(async (tag: string) => {
    const q = tag === "all" ? "" : `?tag=${encodeURIComponent(tag)}`;
    const res = await apiFetch(`/grades${q}`);
    if (!res.ok) throw new Error("grades unavailable");
    const data = await res.json();
    setGrades(data.grades ?? []);
  }, []);

  const loadCameras = useCallback(async (tag: string) => {
    const q = tag === "all" ? "" : `?tag=${encodeURIComponent(tag)}`;
    const res = await apiFetch(`/cameras${q}`);
    if (!res.ok) throw new Error("cameras unavailable");
    const data = await res.json();
    setCameras(data.cameras ?? []);
  }, []);

  const loadSignatures = useCallback(async () => {
    const res = await apiFetch("/signatures");
    if (!res.ok) throw new Error("signatures unavailable");
    const data = await res.json();
    setSignatures(data.signatures ?? []);
  }, []);

  const refreshHealth = useCallback(async () => {
    try {
      const [health, looks, cache] = await Promise.all([
        apiFetch("/health").then((r) => r.json()),
        apiFetch("/looks").then((r) => r.json()),
        apiFetch("/cache/stats").then((r) => r.json()),
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
    void loadCameras("all");
    void loadSignatures();
  }, [loadGrades, loadCameras, loadSignatures, refreshHealth]);

  const pushHistory = useCallback((snap: HistorySnap) => {
    setHistory((prev) => [...prev.slice(-19), snap]);
  }, []);

  const runEnhance = useCallback(
    async (
      file: File | null,
      snap: HistorySnap,
      opts?: { skipHistory?: boolean; trackUpload?: boolean; live?: boolean },
    ) => {
      const seq = ++enhanceSeqRef.current;
      if (enhanceAbortRef.current) enhanceAbortRef.current.abort();
      const abort = new AbortController();
      enhanceAbortRef.current = abort;

      if (opts?.live) setIsLiveRender(true);
      else if (opts?.trackUpload) setUploadStep("uploading_enhance");
      else setBusy(true);
      setErrorMsg(null);
      setErrorHint(null);
      const t0 = performance.now();
      try {
        if (snap.showMasks) {
          if (!file) return;
          const body = new FormData();
          body.append("file", file);
          const res = await apiFetch("/process/masks", { method: "POST", body, signal: abort.signal });
          if (!res.ok) {
            const err = await parseApiError(res, "mask preview failed");
            throw new Error(formatApiError(err.message, err.hint));
          }
          const data = await res.json();
          if (seq !== enhanceSeqRef.current) return;
          setAfterUrl(data.preview);
          setStatus("mask debug · cyan sky · magenta skin · yellow subject");
          setOffline(false);
          if (opts?.trackUpload) {
            setEnhanceMs(Math.round(performance.now() - t0));
            setUploadStep("done");
          }
          return;
        }

        const body = new FormData();
        const live = Boolean(opts?.live);
        const sessionId = sessionIdRef.current;
        if (sessionId && (live || !file)) {
          body.append("session_id", sessionId);
        } else if (file) {
          body.append("file", file);
        } else {
          throw new Error("no image session — re-upload");
        }
        body.append("max_size", live ? String(previewMaxRef.current) : "2048");
        body.append("strength", String(snap.strength));
        body.append("mode", snap.mode);
        body.append("pro_safe", snap.proSafe ? "true" : "false");
        body.append("use_a6000_profile", snap.useA6000 ? "true" : "false");
        if (snap.gradeId) body.append("grade_id", snap.gradeId);
        if (snap.cameraId) body.append("camera_id", snap.cameraId);
        if (snap.signatureId) body.append("signature_id", snap.signatureId);
        appendTuneToForm(body, snap.tune);

        const res = await apiFetch("/process/enhance", {
          method: "POST",
          body,
          signal: abort.signal,
        });
        if (!res.ok) {
          const err = await parseApiError(res, "enhance failed");
          throw new Error(formatApiError(err.message, err.hint));
        }
        const data = await res.json();
        if (seq !== enhanceSeqRef.current) return;

        setAfterUrl(data.preview);
        setAnalysis(data.analysis ?? null);
        setOffline(false);
        const sig = data.signature_id ? String(data.signature_id).replace("sig_", "") : "—";
        const cam = data.camera_id ? String(data.camera_id).replace("cam_", "") : "—";
        const clamped = data.signature_clamped ? " · clamped" : "";
        const cached = data.cached ? " · cached" : "";
        const a6000 = data.a6000_profile ? " · a6000" : "";
        const ms = Math.round(performance.now() - t0);
        setEnhanceMs(ms);
        setStatus(
          `enhance ${snap.strength}% · ${snap.mode} · cam ${cam} · sig ${sig}${clamped}${cached}${a6000} · ${ms}ms`,
        );
        if (!opts?.skipHistory) pushHistory(snap);
        if (opts?.trackUpload) setUploadStep("done");
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        const msg = err instanceof Error ? err.message : "enhance failed";
        if (seq !== enhanceSeqRef.current) return;
        setErrorMsg(msg);
        setStatus(msg);
        if (opts?.trackUpload) setUploadStep("error");
        if (msg.includes("fetch") || msg.includes("network") || msg.includes("offline")) setOffline(true);
      } finally {
        if (seq === enhanceSeqRef.current) {
          if (opts?.live) setIsLiveRender(false);
          else setBusy(false);
        }
      }
    },
    [pushHistory],
  );

  const currentSnap = useCallback(
    (): HistorySnap => ({
      strength,
      mode,
      gradeId: selectedGrade,
      cameraId: selectedCamera,
      signatureId: selectedSignature,
      showMasks,
      proSafe,
      useA6000,
      tune,
    }),
    [mode, proSafe, selectedCamera, selectedGrade, selectedSignature, showMasks, strength, tune, useA6000],
  );

  const scheduleEnhance = useCallback(
    (snap: HistorySnap) => {
      if (!sessionIdRef.current && !fileRef.current) return;
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
      debounceRef.current = window.setTimeout(() => {
        void runEnhance(fileRef.current, snap, { live: true });
      }, LIVE_DEBOUNCE_MS);
    },
    [runEnhance],
  );

  const openFile = useCallback(
    async (file: File) => {
      setBusy(true);
      setErrorMsg(null);
      setErrorHint(null);
      setUploadStep("reading");
      setPreviewMs(null);
      setEnhanceMs(null);
      setServerWidth(null);
      setServerHeight(null);
      setBeforeUrl(null);
      setAfterUrl(null);
      setHasImage(false);
      sessionIdRef.current = null;

      const validation = validateFile(file);
      if (validation) {
        setUploadMeta(fileMeta(file));
        setUploadStep("error");
        setErrorMsg(validation);
        setErrorHint("use JPEG, PNG, HEIC, TIFF, or Sony RAW (.arw)");
        setBusy(false);
        return;
      }

      try {
        setUploadMeta(fileMeta(file));
        setFileName(file.name);

        const { file: uploadFile, note } = await normalizeForUpload(file);
        setConvertNote(note ?? null);
        fileRef.current = uploadFile;

        revokeLocalPreview();
        setUploadStep("local_preview");
        const localUrl = await readLocalPreview(uploadFile);
        localPreviewRef.current = localUrl;
        setLocalPreview(localUrl);
        setHasImage(true);

        setUploadStep("uploading_preview");
        const tPreview = performance.now();
        const body = new FormData();
        body.append("file", uploadFile);
        body.append("max_size", String(previewMaxRef.current));
        body.append("use_a6000_profile", useA6000 ? "true" : "false");
        const res = await apiFetch("/process/open", { method: "POST", body });
        if (!res.ok) {
          const err = await parseApiError(res, "open failed");
          setErrorHint(err.hint ?? null);
          throw new Error(err.message);
        }
        const data = await res.json();
        sessionIdRef.current = data.session_id ?? null;
        setPreviewMs(Math.round(performance.now() - tPreview));
        setBeforeUrl(data.preview);
        setServerWidth(data.width ?? null);
        setServerHeight(data.height ?? null);
        setAnalysis(data.analysis ?? null);
        setOffline(false);
        setHistory([]);

        const snap = currentSnap();
        await runEnhance(null, snap, { trackUpload: true });
      } catch (err) {
        const msg = err instanceof Error ? err.message : "upload failed";
        setErrorMsg(msg);
        setStatus(msg);
        setUploadStep("error");
        if (msg.includes("fetch") || msg.includes("offline")) {
          setOffline(true);
          setErrorHint("run ./dev.sh in the auraforge folder, then reload");
        }
      } finally {
        setBusy(false);
      }
    },
    [currentSnap, revokeLocalPreview, runEnhance, useA6000],
  );

  const pickFile = useCallback(
    (file: File | undefined) => {
      if (!file) return;
      void openFile(file);
    },
    [openFile],
  );

  useEffect(() => () => revokeLocalPreview(), [revokeLocalPreview]);

  const undo = useCallback(() => {
    if (history.length < 2) return;
    const prev = history[history.length - 2];
    setHistory((h) => h.slice(0, -1));
    setStrength(prev.strength);
    setMode(prev.mode);
    setSelectedGrade(prev.gradeId);
    setSelectedCamera(prev.cameraId);
    setSelectedSignature(prev.signatureId);
    setShowMasks(prev.showMasks);
    setProSafe(prev.proSafe);
    setUseA6000(prev.useA6000);
    setTune(prev.tune);
    const file = fileRef.current;
    if (sessionIdRef.current || file) void runEnhance(file, prev, { skipHistory: true });
  }, [history, runEnhance]);

  const exportImage = useCallback(async () => {
    const file = fileRef.current;
    const sessionId = sessionIdRef.current;
    if (!sessionId && !file) return;
    setBusy(true);
    setExportProgress({ phase: "starting", progress: 0, message: "starting" });
    try {
      const snap = currentSnap();
      const pixels = (serverWidth ?? 0) * (serverHeight ?? 0);
      const { blob, filename } = await runExport(
        {
          sessionId,
          strength: snap.strength,
          mode: snap.mode,
          gradeId: snap.gradeId,
          cameraId: snap.cameraId,
          signatureId: snap.signatureId,
          format: exportFormat,
          tune: snap.tune,
          proSafe: snap.proSafe,
          useA6000: snap.useA6000,
          pixelCount: pixels,
        },
        setExportProgress,
      );
      triggerDownload(blob, filename);
      setStatus(`exported ${filename}`);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "export failed");
    } finally {
      setBusy(false);
      setExportProgress(null);
    }
  }, [currentSnap, exportFormat, serverHeight, serverWidth]);

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
      if (snap.cameraId) body.append("camera_id", snap.cameraId);
      if (snap.signatureId) body.append("signature_id", snap.signatureId);
      appendTuneToForm(body, snap.tune);
      const res = await apiFetch("/process/batch", { method: "POST", body });
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
      if (!mod && hasImage && (beforeUrl || localPreview)) {
        if (e.key === "ArrowLeft") setScrub((s) => Math.max(0, s - 5));
        if (e.key === "ArrowRight") setScrub((s) => Math.min(100, s + 5));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [afterUrl, beforeUrl, exportImage, hasImage, localPreview, undo]);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) {
      setErrorMsg("no file in drop — drag a single image file");
      setUploadStep("error");
      return;
    }
    pickFile(file);
  };

  const displayBefore = beforeUrl || localPreview;

  const applySnap = (partial: Partial<HistorySnap>) => {
    const snap: HistorySnap = { ...currentSnap(), ...partial };
    if (partial.strength !== undefined) setStrength(partial.strength);
    if (partial.mode !== undefined) setMode(partial.mode);
    if (partial.gradeId !== undefined) setSelectedGrade(partial.gradeId);
    if (partial.cameraId !== undefined) setSelectedCamera(partial.cameraId);
    if (partial.signatureId !== undefined) setSelectedSignature(partial.signatureId);
    if (partial.showMasks !== undefined) setShowMasks(partial.showMasks);
    if (partial.proSafe !== undefined) setProSafe(partial.proSafe);
    if (partial.useA6000 !== undefined) setUseA6000(partial.useA6000);
    if (partial.tune !== undefined) setTune(partial.tune);
    scheduleEnhance(snap);
  };

  return (
    <div className="studio-app">
      <header className="studio-topbar">
        <div className="studio-brand">
          <h1>auraforge</h1>
          <span className="studio-tag">local studio</span>
        </div>
        <nav className="studio-nav">
          <a href="/" className="active">
            editor
          </a>
          <a href="/showcase">showcase</a>
          <a href="/research">research</a>
        </nav>
        <div className="studio-topbar-actions">
          <button type="button" className="studio-icon-btn" title="Open (⌘O)" onClick={() => fileInputRef.current?.click()}>
            <IconUpload size={18} />
          </button>
          <button
            type="button"
            className="studio-icon-btn"
            title="Undo (⌘Z)"
            disabled={history.length < 2}
            onClick={undo}
          >
            <IconUndo size={18} />
          </button>
          <select
            className="studio-select"
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value as ExportFormat)}
          >
            <option value="jpeg">JPEG</option>
            <option value="tiff">TIFF 16-bit</option>
          </select>
          <button
            type="button"
            className="studio-btn primary"
            disabled={!hasImage || busy}
            onClick={() => void exportImage()}
          >
            <IconExport size={16} /> {exportProgress ? exportProgress.message : "Export"}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,.heic,.heif,.arw,.dng,.nef,.cr2,.cr3,.tif,.tiff"
            hidden
            onChange={(e) => {
              pickFile(e.target.files?.[0]);
              e.target.value = "";
            }}
          />
        </div>
      </header>

      {(offline || errorMsg) && (
        <div className="studio-banner-wrap">
          <ErrorBanner
            message={errorMsg || "api offline — run ./dev.sh"}
            offline={offline}
            onRetry={() => void refreshHealth()}
          />
        </div>
      )}

      <div className="studio-body">
        <aside className="studio-sidebar">
          <div className="sidebar-tabs">
            <button
              type="button"
              className={sidebarTab === "enhance" ? "sidebar-tab active" : "sidebar-tab"}
              onClick={() => setSidebarTab("enhance")}
            >
              <IconEnhance size={17} />
              <span>Enhance</span>
            </button>
            <button
              type="button"
              className={sidebarTab === "tone" ? "sidebar-tab active" : "sidebar-tab"}
              onClick={() => setSidebarTab("tone")}
            >
              <IconSliders size={17} />
              <span>Tone</span>
            </button>
            <button
              type="button"
              className={sidebarTab === "looks" ? "sidebar-tab active" : "sidebar-tab"}
              onClick={() => setSidebarTab("looks")}
            >
              <IconPalette size={17} />
              <span>Looks</span>
            </button>
            <button
              type="button"
              className={sidebarTab === "cameras" ? "sidebar-tab active" : "sidebar-tab"}
              onClick={() => setSidebarTab("cameras")}
            >
              <IconCamera size={17} />
              <span>Cameras</span>
            </button>
            <button
              type="button"
              className={sidebarTab === "fx" ? "sidebar-tab active" : "sidebar-tab"}
              onClick={() => setSidebarTab("fx")}
            >
              <IconFx size={17} />
              <span>FX</span>
            </button>
            <button
              type="button"
              className={sidebarTab === "settings" ? "sidebar-tab active" : "sidebar-tab"}
              onClick={() => setSidebarTab("settings")}
            >
              <IconFolder size={17} />
              <span>More</span>
            </button>
          </div>

          <div className="sidebar-panel">
            {sidebarTab === "enhance" && (
              <>
                <p className="panel-title">Enhance mode</p>
                <div className="mode-grid">
                  {MODES.map((m) => (
                    <button
                      key={m}
                      type="button"
                      className={m === mode ? "mode-pill active" : "mode-pill"}
                      onClick={() => applySnap({ mode: m })}
                    >
                      {m}
                    </button>
                  ))}
                </div>
                <p className="panel-hint">All changes update the preview live.</p>
              </>
            )}

            {sidebarTab === "tone" && (
              <TonePanel
                tune={tune}
                strength={strength}
                live={isLiveRender}
                onStrength={(v) => applySnap({ strength: v })}
                onTune={(key, v) => applySnap({ tune: { ...tune, [key]: v } })}
              />
            )}

            {sidebarTab === "looks" && (
              <LooksPanel
                kind="grades"
                items={grades}
                tags={GRADE_TAGS}
                activeTag={gradeTag}
                selectedId={selectedGrade}
                lookAmount={tune.lookAmount}
                live={isLiveRender}
                onTag={(tag) => {
                  setGradeTag(tag);
                  void loadGrades(tag);
                }}
                onSelect={(id) => applySnap({ gradeId: id })}
                onLookAmount={(v) => applySnap({ tune: { ...tune, lookAmount: v } })}
              />
            )}

            {sidebarTab === "cameras" && (
              <CameraPanel
                items={cameras}
                tags={CAMERA_TAGS}
                activeTag={cameraTag}
                selectedId={selectedCamera}
                lookAmount={tune.lookAmount}
                live={isLiveRender}
                onTag={(tag) => {
                  setCameraTag(tag);
                  void loadCameras(tag);
                }}
                onSelect={(id) => applySnap({ cameraId: id })}
                onLookAmount={(v) => applySnap({ tune: { ...tune, lookAmount: v } })}
              />
            )}

            {sidebarTab === "fx" && (
              <LooksPanel
                kind="signatures"
                items={signatures}
                tags={["all"]}
                activeTag="all"
                selectedId={selectedSignature}
                lookAmount={tune.lookAmount}
                live={isLiveRender}
                onTag={() => {}}
                onSelect={(id) => applySnap({ signatureId: id })}
                onLookAmount={(v) => applySnap({ tune: { ...tune, lookAmount: v } })}
              />
            )}

            {sidebarTab === "settings" && (
              <div className="settings-panel">
                <label className="studio-check">
                  <input
                    type="checkbox"
                    checked={hdPreview}
                    onChange={(e) => {
                      setHdPreview(e.target.checked);
                      window.setTimeout(() => scheduleEnhance(currentSnap()), 0);
                    }}
                  />
                  HD preview ({PREVIEW_HD}px)
                </label>
                <label className="studio-check">
                  <input
                    type="checkbox"
                    checked={showMasks}
                    onChange={(e) => applySnap({ showMasks: e.target.checked })}
                  />
                  Mask debug overlay
                </label>
                <label className="studio-check">
                  <input
                    type="checkbox"
                    checked={proSafe}
                    onChange={(e) => applySnap({ proSafe: e.target.checked })}
                  />
                  Pro-safe signature clamp
                </label>
                <label className="studio-check">
                  <input
                    type="checkbox"
                    checked={useA6000}
                    onChange={(e) => applySnap({ useA6000: e.target.checked })}
                  />
                  a6000 base profile
                </label>
                <details className="studio-details">
                  <summary>Batch folder</summary>
                  <input
                    className="studio-input"
                    type="text"
                    placeholder="/path/to/folder"
                    value={batchFolder}
                    onChange={(e) => setBatchFolder(e.target.value)}
                  />
                  <input
                    className="studio-input"
                    type="text"
                    placeholder="output dir (optional)"
                    value={batchOut}
                    onChange={(e) => setBatchOut(e.target.value)}
                  />
                  <button
                    type="button"
                    className="studio-btn"
                    disabled={busy || !batchFolder.trim()}
                    onClick={() => void runBatch()}
                  >
                    Run batch
                  </button>
                  {batchResult && <p className="panel-hint">{batchResult}</p>}
                </details>
                {uploadStep !== "idle" && (
                  <p className="panel-hint">
                    {uploadStep === "done" ? "Ready" : uploadStep.replace(/_/g, " ")}
                    {enhanceMs != null && ` · ${enhanceMs}ms`}
                    {previewMs != null && ` · open ${previewMs}ms`}
                  </p>
                )}
                {(uploadMeta || serverWidth != null) && (
                  <div className="file-info-panel">
                    {uploadMeta && (
                      <p className="panel-hint">
                        {uploadMeta.name} · {uploadMeta.sizeLabel}
                      </p>
                    )}
                    {serverWidth != null && serverHeight != null && (
                      <p className="panel-hint">
                        {serverWidth}×{serverHeight}px
                      </p>
                    )}
                    {convertNote && <p className="panel-hint">{convertNote}</p>}
                    {cacheHits != null && <p className="panel-hint">cache hits {cacheHits}</p>}
                  </div>
                )}
                {errorHint && uploadStep === "error" && <p className="panel-hint">{errorHint}</p>}
                <DebugPanel data={analysis} />
              </div>
            )}
          </div>

          <footer className="sidebar-footer">
            <span className="sidebar-status">{status}</span>
            {lookCount != null && <span>{lookCount} looks</span>}
          </footer>
        </aside>

        <StudioCanvas
          hasImage={hasImage}
          displayBefore={displayBefore}
          afterUrl={afterUrl}
          scrub={scrub}
          onScrub={setScrub}
          isLiveRender={isLiveRender}
          enhanceMs={enhanceMs}
          hdPreview={hdPreview}
          previewMax={previewMaxRef.current}
          busy={busy}
          dragOver={dragOver}
          fileName={fileName}
          onDrop={onDrop}
          onDragOver={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onPickFile={() => fileInputRef.current?.click()}
        />
      </div>
    </div>
  );
}
