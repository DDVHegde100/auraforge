import type { TuneState } from "../lib/tune";

type SliderDef = {
  key: keyof TuneState | "strength";
  label: string;
};

const SLIDERS: SliderDef[] = [
  { key: "strength", label: "AI Enhance" },
  { key: "lookAmount", label: "Filter Strength" },
  { key: "clarity", label: "Clarity" },
  { key: "detail", label: "Detail" },
  { key: "light", label: "Light" },
  { key: "shadows", label: "Shadows" },
  { key: "highlights", label: "Highlights" },
  { key: "warmth", label: "Warmth" },
];

type Props = {
  tune: TuneState;
  strength: number;
  live: boolean;
  onStrength: (v: number) => void;
  onTune: (key: keyof TuneState, v: number) => void;
};

function sliderValue(key: SliderDef["key"], tune: TuneState, strength: number) {
  return key === "strength" ? strength : tune[key];
}

export function TonePanel({ tune, strength, live, onStrength, onTune }: Props) {
  return (
    <div className="tone-panel-studio">
      {live && (
        <div className="tone-live-bar">
          <span className="live-pill">updating preview…</span>
        </div>
      )}
      {SLIDERS.map((s) => {
        const val = sliderValue(s.key, tune, strength);
        const onChange = (v: number) => {
          if (s.key === "strength") onStrength(v);
          else onTune(s.key, v);
        };
        return (
          <label key={s.key} className="studio-slider">
            <div className="studio-slider-head">
              <span>{s.label}</span>
              <span className="studio-slider-val">{val}</span>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              value={val}
              onChange={(e) => onChange(Number(e.target.value))}
              onInput={(e) => onChange(Number((e.target as HTMLInputElement).value))}
            />
          </label>
        );
      })}
    </div>
  );
}
