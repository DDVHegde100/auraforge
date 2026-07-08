export type TuneState = {
  clarity: number;
  detail: number;
  light: number;
  shadows: number;
  highlights: number;
  warmth: number;
  lookAmount: number;
};

export const DEFAULT_TUNE: TuneState = {
  clarity: 50,
  detail: 55,
  light: 52,
  shadows: 50,
  highlights: 50,
  warmth: 50,
  lookAmount: 100,
};

export function appendTuneToForm(body: FormData, tune: TuneState) {
  body.append("clarity", String(tune.clarity));
  body.append("detail", String(tune.detail));
  body.append("light", String(tune.light));
  body.append("shadows", String(tune.shadows));
  body.append("highlights", String(tune.highlights));
  body.append("warmth", String(tune.warmth));
  body.append("look_amount", String(tune.lookAmount));
}
