"""Portrait polish — eyes, skin texture, warmth balance."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance
from auraforge_engine.develop.chroma import relight_preserving_chroma


def apply_portrait_polish(
    enhanced: np.ndarray,
    original: np.ndarray,
    skin_mask: np.ndarray,
    subject_mask: np.ndarray,
    *,
    strength: float = 1.0,
) -> np.ndarray:
    t = max(0.0, min(1.0, strength))
    if t <= 0.0 or float(skin_mask.max()) < 0.05:
        return enhanced

    out = enhanced.astype(np.float32, copy=True)
    lum = luminance(out)

    # Soft skin micro-texture: blend high-freq back from original on skin
    blur = cv2.GaussianBlur(out, (0, 0), sigmaX=1.1)
    hf = out - blur
    orig_hf = original - cv2.GaussianBlur(original, (0, 0), sigmaX=1.1)
    skin = np.clip(skin_mask * t, 0.0, 1.0)[..., None]
    out = out - hf * skin * 0.42 + orig_hf * skin * 0.18

    # Eye catchlight lift in upper subject band
    subj = subject_mask
    if float(subj.max()) > 0.1:
        h, w = subj.shape
        yy, xx = np.where(subj > 0.35)
        if len(yy) > 8:
            y0, y1 = int(yy.min()), int(yy.min() + (yy.max() - yy.min()) * 0.45)
            x0, x1 = int(max(0, xx.min() - 2)), int(min(w, xx.max() + 2))
            eye_region = np.zeros_like(subj)
            eye_region[y0:y1, x0:x1] = subj[y0:y1, x0:x1]
            eye_region = cv2.GaussianBlur(eye_region, (0, 0), sigmaX=4.0)
            bright = np.clip((lum - 0.35) / 0.35, 0.0, 1.0) * eye_region
            new_lum = lum + bright * 0.06 * t
            out = relight_preserving_chroma(out, np.clip(new_lum, 0.0, None))

    return np.clip(out, 0.0, None)
