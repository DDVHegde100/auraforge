# research: aesthetics, perception, neo-style enhance

notes that drive auraforge algorithms. not marketing fluff — constraints for the engine.

---

## 1. what luminar neo “does” (capability map, not a clone)

neo sells **minimum clicks → maximum perceived quality**. product surface we reverse-engineer *as capabilities*:

| neo-ish tool | underlying tech family | perception lever |
|--------------|------------------------|------------------|
| enhance / accent ai | image stats → multi-param develop recipe | global tone & color harmony |
| sky enhancer | semantic sky mask + selective tone | atmospheric vividness |
| sky ai (replace) | sky segmentation + depth/relight | narrative drama (phase later) |
| light depth / relight | monocular depth → zone exposure | subject pop / volume |
| structure / detail | multi-scale unsharp / bilateral | edge energy without noise |
| generative erase | inpainting (heavy; optional later) | cleanup |

**enhance is not one neural net magicking beauty.**
skylum describes accent as balancing ~12 classic controls (shadows, highlights, contrast, exposure, saturation, detail…). modern versions add learned *priors* (what “good” photos look like) and **selective** paths (sky).

**auraforge stance:** make the recipe **explicit** (inspectable params) + optional tiny predictors. beat opaque “magic” with transparency + scientific grades.

---

## 2. what human viewers reward (computational aesthetics)

### sources to treat as grounding

- **AVA** (Murray et al., CVPR 2012) — ~250k photos with community aesthetic scores; content tags: portrait, landscape, food/drink, floral, etc.
- surveys of image aesthetic assessment — composition, color, sharpness, depth of field as predictive features
- photographic style labels on AVA (rule of thirds, HDR, soft focus, complementary colors, etc.)

### features that reliably correlate with “looks good”

| feature | why it scores | auraforge use |
|---------|---------------|---------------|
| midtone contrast | punch without crushing blacks | accent contrast curve pivot ~18% grey |
| highlight roll-off | “expensive” digital feel | soft highlight compression |
| shadow lift (gentle) | readability / editorial | shadow lift with luminance mask |
| color contrast (complementary) | pop subject (esp. teal–orange) | split tone + skin-line protect |
| saturation in mids, not skins | food / landscape vivid | selective vibrance |
| sharp edges + soft backgrounds | depth of field proxy | clarity + optional subject mask |
| warm key / cool fill | cinematic light story | floating light + haze |
| low noise in shadows | “pro gear” cue | bilateral / ISO-aware denoise |

### skin-tone line (portrait science)

across ethnicities, skin reflectance sits in a narrow **orange–amber** range on vectorscope (melanin + hemoglobin).
**professionals protect that line.** grading that tints skin teal/green fails A/B instantly.

rule for auraforge portrait grades:

1. detect approximate skin (HSV + optional face box)
2. apply cool shifts to **non-skin** first
3. warmth / glow on highlights can touch skin carefully
4. never global-force teal onto full RGB for portraits

### teal–orange popularity (why neo / hollywood grades “feel expensive”)

complementary hues → maximum hue contrast.
skin already orange-ish → teal shadows separate subject **by color**, not only by depth of field.
implement as: shadow hue shift cyan-teal + keep midtone skin; not a flat LUT wash.

### food photography preferences

- slightly lifted shadows (texture on plating)
- warm highlights (appetite / hospitality literature)
- greens and reds selectively punched; muddy yellows pulled
- avoid crushing blacks (looks phone-flash cheap)

---

## 3. designing “ai enhance” as a scientific pipeline

```
input
  → scene analysis (features + masks)
  → recipe solver (params in known safe ranges)
  → render stack (develop → selective → creative)
  → strength mixer (0–100% neo-style slider)
```

### 3.1 scene analysis (feature vector)

compute (CPU-first, lightweight):

- luminance histogram (shadows/mids/highlights mass)
- mean / median Lab color
- estimated white balance (grey-world / white-patch)
- contrast (std of luminance, local RMS)
- saturation mean & 95th percentile
- **sky score** — high blue-ratio + upper-third + low texture OR ML segmentation later
- **face score** — Haar/MediaPipe optional; fallback skin %, center weight
- **noise estimate** — high-ISO proxy from flat patch variance
- **salience proxy** — center + contrast peaks

### 3.2 multi-slider recipe (maps features → develop)

each control has a target based on scene class:

| control | underexposed landscape | flat portrait | food flat |
|---------|------------------------|---------------|-----------|
| exposure | +0.3–0.8 | +0.1–0.3 | +0.2 |
| shadow lift | medium | higher | medium |
| highlight recover | high (sky) | medium | low |
| contrast | medium–high | low–medium | medium |
| vibrance | high sky-biased | low global | selective |
| clarity | medium | low–medium | medium |
| warmth | sunset detect | mild | warm |
| bloom/glow | optional soft | soft key light | subtle |

**strength slider** scales recipe deltas from identity → full recipe (same UX as accent).

### 3.3 sky mask

phase A (lightweight algorithmic):

- convert HSV / Lab
- upper image bias + hue in blue–cyan + low saturation variance → soft mask
- feather edges; exclude water false-positives via vertical gradient heuristics where possible

phase B (optional ML): lightweight segmentation model onnx — still **local**.

sky enhancer apply: contrast + saturation + detail on masked sky only (neo sky enhancer behavior).

---

## 4. looking at neo / pro color stacks (behavioral analysis)

without cloning neo assets, we replicate **look families** photographers buy neo for:

| look family | neo-ish behavior | algorithmic recipe |
|-------------|------------------|--------------------|
| natural accent | lift, punch, color | develop + mild vibrance |
| golden / warm | warmth + soft bloom | WB + orton + split tone warm hi |
| mood / cool | cool shadows, soft | teal shadows + desat mids |
| dream / ethereal | heavy orton | blur screen + haze |
| crisp / pro | clarity, dehaze | local contrast + dehaze |
| sky pop | sky-only vivid | mask + sat/contrast |
| portrait soft | skin protect, glow | skin mask + soft light |
| film | grain + halation | grain + highlight bloom |

**aggressive unique filters** (our 20) push past neo defaults into distinctive signatures (thermal, floating light orbs, infrared faux, etc.) while keeping a toggle for “pro-safe” intensity.

---

## 5. what to optimize for A/B “looks amazing”

evaluation checklist for every look (manual gallery later automated):

1. subject readable in 1 second?
2. skin on-line for portraits?
3. no hue banding / posterization?
4. shadows hold texture (not plastic)?
5. highlight bloom doesn’t milk whole frame?
6. food still appetizing (not corpse-green)?
7. works on phone JPEG **and** a6000 TIFF?

---

## 6. lightweight constraint (local web)

- prefer **numpy/opencv** recipes over giant diffusion for v1
- optional onnx models under ~50MB for face/sky
- process preview at ≤1600px long edge; full-res on export
- no cloud required for core enhance + looks

---

## 7. references (starting set)

1. Murray, Marchesotti, Perronnin — AVA (CVPR 2012)
2. Datta et al. — Studying Aesthetics in Photographic Images
3. Surveys on image aesthetic assessment (arXiv 2103.11616)
4. Color psychology / complementary contrast (teal–orange industry practice)
5. Classical photography: Orton effect, frequency separation, luminosity masking

update this file as commits land measuring real look scores on a fixed golden set of test photos.
