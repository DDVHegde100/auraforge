import type { FileMeta, UploadStep } from "../lib/upload";

type Props = {
  step: UploadStep;
  meta: FileMeta | null;
  convertNote: string | null;
  localPreview: string | null;
  serverWidth: number | null;
  serverHeight: number | null;
  previewMs: number | null;
  enhanceMs: number | null;
  error: string | null;
  hint: string | null;
};

const STEP_LABEL: Record<UploadStep, string> = {
  idle: "waiting for photo",
  reading: "reading file from disk",
  local_preview: "showing instant local preview",
  uploading_preview: "uploading to engine for analysis",
  uploading_enhance: "running enhance + looks pipeline",
  done: "ready — adjust sliders below",
  error: "upload failed",
};

export function UploadPanel({
  step,
  meta,
  convertNote,
  localPreview,
  serverWidth,
  serverHeight,
  previewMs,
  enhanceMs,
  error,
  hint,
}: Props) {
  const busy = step !== "idle" && step !== "done" && step !== "error";

  return (
    <section className={`upload-panel ${busy ? "busy" : ""} ${error ? "has-error" : ""}`}>
      <p className="section-label">photo upload</p>
      <div className="upload-steps">
        <StepRow label="1 · pick file" active={step === "reading"} done={step !== "idle"} />
        <StepRow
          label="2 · local preview"
          active={step === "local_preview"}
          done={!!localPreview && step !== "reading" && step !== "local_preview"}
        />
        <StepRow
          label="3 · engine preview"
          active={step === "uploading_preview"}
          done={serverWidth != null && step !== "uploading_preview"}
        />
        <StepRow
          label="4 · enhance"
          active={step === "uploading_enhance"}
          done={step === "done"}
        />
      </div>

      {meta && (
        <dl className="upload-meta">
          <div className="upload-meta-row">
            <dt>file</dt>
            <dd>{meta.name}</dd>
          </div>
          <div className="upload-meta-row">
            <dt>size</dt>
            <dd>
              {meta.sizeLabel} ({meta.sizeBytes.toLocaleString()} bytes)
            </dd>
          </div>
          <div className="upload-meta-row">
            <dt>type</dt>
            <dd>
              .{meta.ext} · {meta.mime}
            </dd>
          </div>
          {convertNote && (
            <div className="upload-meta-row">
              <dt>convert</dt>
              <dd>{convertNote}</dd>
            </div>
          )}
          {serverWidth != null && serverHeight != null && (
            <div className="upload-meta-row">
              <dt>preview size</dt>
              <dd>
                {serverWidth} × {serverHeight}px
              </dd>
            </div>
          )}
          {(previewMs != null || enhanceMs != null) && (
            <div className="upload-meta-row">
              <dt>timing</dt>
              <dd>
                {previewMs != null && `preview ${previewMs}ms`}
                {previewMs != null && enhanceMs != null && " · "}
                {enhanceMs != null && `enhance ${enhanceMs}ms`}
              </dd>
            </div>
          )}
        </dl>
      )}

      <p className={`upload-status ${error ? "error-text" : ""}`}>{error || STEP_LABEL[step]}</p>
      {hint && <p className="upload-hint">{hint}</p>}

      {localPreview && (
        <div className="upload-preview-wrap">
          <p className="label">your photo</p>
          <img src={localPreview} alt="upload preview" className="upload-preview-img" />
        </div>
      )}
    </section>
  );
}

function StepRow({ label, active, done }: { label: string; active: boolean; done: boolean }) {
  return (
    <div className={`upload-step ${active ? "active" : ""} ${done ? "done" : ""}`}>
      <span className="upload-step-dot" />
      <span>{label}</span>
    </div>
  );
}
