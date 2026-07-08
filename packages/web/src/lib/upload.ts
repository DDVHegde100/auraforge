/** Upload helpers — validation, HEIC fallback, detailed API errors. */

const RAW_EXT = new Set(["arw", "dng", "nef", "cr2", "cr3"]);
const HEIC_EXT = new Set(["heic", "heif"]);
const OK_EXT = new Set([
  "jpg",
  "jpeg",
  "png",
  "webp",
  "tif",
  "tiff",
  ...RAW_EXT,
  ...HEIC_EXT,
]);

export type FileMeta = {
  name: string;
  sizeBytes: number;
  sizeLabel: string;
  mime: string;
  ext: string;
};

export type UploadStep =
  | "idle"
  | "reading"
  | "local_preview"
  | "uploading_preview"
  | "uploading_enhance"
  | "done"
  | "error";

export function fileMeta(file: File): FileMeta {
  const ext = (file.name.split(".").pop() || "").toLowerCase();
  const mb = file.size / (1024 * 1024);
  const sizeLabel = mb >= 1 ? `${mb.toFixed(2)} MB` : `${(file.size / 1024).toFixed(1)} KB`;
  return { name: file.name, sizeBytes: file.size, sizeLabel, mime: file.type || "unknown", ext };
}

export function validateFile(file: File): string | null {
  const { ext, sizeBytes } = fileMeta(file);
  if (sizeBytes === 0) return "file is empty (0 bytes)";
  if (sizeBytes > 80 * 1024 * 1024) return "file too large — max ~80 MB for local preview";
  if (!ext) return "file has no extension — use .jpg, .png, .heic, .tif, or .arw";
  if (!OK_EXT.has(ext) && !file.type.startsWith("image/")) {
    return `unsupported type “.${ext}” — try JPEG, PNG, HEIC, TIFF, or Sony ARW`;
  }
  if (RAW_EXT.has(ext)) {
    return null; // allowed; server may need rawpy
  }
  return null;
}

function loadImageElement(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error("browser could not decode this image"));
    img.src = src;
  });
}

/** Convert HEIC/HEIF to JPEG in-browser when the engine cannot read them. */
export async function normalizeForUpload(file: File): Promise<{ file: File; note?: string }> {
  const { ext } = fileMeta(file);
  if (!HEIC_EXT.has(ext)) return { file };

  const url = URL.createObjectURL(file);
  try {
    const img = await loadImageElement(url);
    const canvas = document.createElement("canvas");
    canvas.width = img.naturalWidth || img.width;
    canvas.height = img.naturalHeight || img.height;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("canvas unavailable");
    ctx.drawImage(img, 0, 0);
    const blob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob((b) => (b ? resolve(b) : reject(new Error("HEIC convert failed"))), "image/jpeg", 0.92);
    });
    const out = new File([blob], file.name.replace(/\.(heic|heif)$/i, ".jpg"), { type: "image/jpeg" });
    return { file: out, note: "converted HEIC → JPEG in browser" };
  } catch {
    throw new Error(
      "HEIC not supported in this browser — export as JPEG from Photos, or run: pip install pillow-heif",
    );
  } finally {
    URL.revokeObjectURL(url);
  }
}

export async function readLocalPreview(file: File): Promise<string> {
  return URL.createObjectURL(file);
}

export type ApiErrorDetail = {
  message: string;
  status?: number;
  detail?: string;
  hint?: string;
};

export async function parseApiError(res: Response, fallback: string): Promise<ApiErrorDetail> {
  let detail = "";
  try {
    const data = await res.json();
    if (typeof data.detail === "string") detail = data.detail;
    else if (Array.isArray(data.detail)) detail = data.detail.map((d: { msg?: string }) => d.msg).join("; ");
    else if (data.detail) detail = String(data.detail);
  } catch {
    detail = await res.text().catch(() => "");
  }
  const message = detail || fallback;
  let hint: string | undefined;
  if (/unsupported type|could not read/i.test(message)) {
    hint = "try JPEG or PNG; for iPhone HEIC enable browser convert or pip install pillow-heif";
  } else if (/rawpy/i.test(message)) {
    hint = "install RAW support: pip install auraforge-engine[raw]";
  } else if (res.status === 413) {
    hint = "file too large for upload";
  } else if (res.status >= 500) {
    hint = "engine error — check terminal running ./dev.sh";
  } else if (res.status === 0 || message.includes("fetch")) {
    hint = "api offline — run ./dev.sh in auraforge folder";
  }
  return { message, status: res.status, detail, hint };
}

export async function postForm(path: string, body: FormData): Promise<Response> {
  return fetch(path, { method: "POST", body });
}
