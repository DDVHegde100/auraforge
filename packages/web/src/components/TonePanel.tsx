import type { TuneState } from "../lib/tune";

type SliderDef = {
  key: keyof TuneState;
  label: string;
  hint: string;
};

const SLIDERS: SliderDef[] = [
  { key: "clarity", label: "clarity", hint: "local contrast & punch" },
  { key: "detail", label: "detail / upscale", hint: "edge-aware sharpen + micro-upscale" },
  { key: "light", label: "light sculpt", hint: "relight zones + glow" },
  { key: "shadows", label: "shadows", hint: "lift left · crush right" },
  { key: "highlights", label: "highlights", hint: "recover left · bloom right" },
  { key: "warmth", label: "warmth", hint: "cool left · warm right" },
  { key: "lookAmount", label: "filter strength", hint: "grade + camera + signature" },
];

type Props = {
  tune: TuneState;
  strength: number;
  live: boolean;
  onStrength: (v: number) => void;
  onTune: (key: keyof TuneState, v: number) => void;
};

export function TonePanel({ tune, strength, live, onStrength, onTune }: Props) {
  return (
    <section className="enhance-controls tone-panel">
      <div className="tone-header">
        <p className="section-label">live tone</p>
        {live && <span className="live-pill">updating…</span>}
      </div>

      <label className="slider-label">
        ai enhance
        <input
          type="range"
          min={0}
          max={100}
          value={strength}
          onChange={(e) => onStrength(Number(e.target.value))}
        />
        <span className="slider-value">{strength}</span>
      </label>

      <div className="tone-grid">
        {SLIDERS.map((s) => (
          <label key={s.key} className="slider-label tone-slider">
            <span className="tone-slider-top">
              <span>{s.label}</span>
              <span className="slider-value">{tune[s.key]}</span>
            </span>
            <input
              type="range"
              min={0}
              max={100}
              value={tune[s.key]}
              onChange={(e) => onTune(s.key, Number(e.target.value))}
            />
            <span className="tone-hint">{s.hint}</span>
          </label>
        ))}
      </div>
    </section>
  );
}
