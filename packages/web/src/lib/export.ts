import { apiFetch, apiUrl } from "./api";
import { appendTuneToForm, type TuneState } from "./tune";

export type ExportProgress = {
  phase: "starting" | "processing" | "encoding" | "downloading" | "done" | "error";
  progress: number;
  message: string;
};

type ExportParams = {
  sessionId: string | null;
  strength: number;
  mode: string;
  gradeId: string | null;
  cameraId: string | null;
  signatureId: string | null;
  format: "jpeg" | "tiff";
  tune: TuneState;
  proSafe: boolean;
  useA6000: boolean;
  pixelCount?: number;
};

function buildExportForm(p: ExportParams): FormData {
  const body = new FormData();
  if (p.sessionId) body.append("session_id", p.sessionId);
  body.append("strength", String(p.strength));
  body.append("mode", p.mode);
  if (p.gradeId) body.append("grade_id", p.gradeId);
  if (p.cameraId) body.append("camera_id", p.cameraId);
  if (p.signatureId) body.append("signature_id", p.signatureId);
  body.append("fmt", p.format);
  body.append("pro_safe", p.proSafe ? "true" : "false");
  body.append("use_a6000_profile", p.useA6000 ? "true" : "false");
  appendTuneToForm(body, p.tune);
  return body;
}

async function pollJob(
  jobId: string,
  onProgress: (p: ExportProgress) => void,
): Promise<{ blob: Blob; filename: string }> {
  for (let i = 0; i < 120; i++) {
    const res = await apiFetch(`/jobs/${jobId}`);
    if (!res.ok) throw new Error("export job lost");
    const data = await res.json();
    onProgress({
      phase: data.status === "done" ? "downloading" : "processing",
      progress: Math.max(0.05, data.progress ?? 0),
      message: data.message ?? data.status,
    });
    if (data.status === "done") {
      const dl = await apiFetch(`/jobs/${jobId}/download`);
      if (!dl.ok) throw new Error("download failed");
      const blob = await dl.blob();
      return { blob, filename: data.filename ?? "auraforge.jpg" };
    }
    if (data.status === "error") throw new Error(data.error ?? "export failed");
    await new Promise((r) => setTimeout(r, 400));
  }
  throw new Error("export timed out");
}

export async function exportImage(
  params: ExportParams,
  onProgress: (p: ExportProgress) => void,
): Promise<{ blob: Blob; filename: string }> {
  onProgress({ phase: "starting", progress: 0, message: "starting export" });
  const body = buildExportForm(params);
  const useAsync = (params.pixelCount ?? 0) > 2_000_000;

  if (useAsync) {
    const res = await apiFetch("/process/export/async", { method: "POST", body });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err || "async export failed");
    }
    const data = await res.json();
    return pollJob(data.job_id, onProgress);
  }

  onProgress({ phase: "processing", progress: 0.3, message: "rendering full resolution" });
  const res = await apiFetch("/process/export", { method: "POST", body });
  if (!res.ok) throw new Error(await res.text());
  onProgress({ phase: "downloading", progress: 0.9, message: "preparing download" });
  const blob = await res.blob();
  const cd = res.headers.get("Content-Disposition") ?? "";
  const match = cd.match(/filename="([^"]+)"/);
  const filename = match?.[1] ?? (params.format === "tiff" ? "auraforge.tif" : "auraforge.jpg");
  onProgress({ phase: "done", progress: 1, message: "ready" });
  return { blob, filename };
}

export function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export { apiUrl };
