# look catalog — 20 signature + 40 grades

naming: `sig_*` = aggressive creative filters · `grade_*` = curated color grades.

all recipes live as JSON under `data/looks/` once implementation starts.
strengths below are **target design intent** (engine maps to params in PLAN_100).

---

## A. 20 signature looks (aggressive / unique)

| id | name | vibe | core technique |
|----|------|------|----------------|
| `sig_floating_light` | floating light | soft volumetric key; light “sits” on subject | luminance bloom on highlights + soft gradient light from estimated subject |
| `sig_halo_dawn` | halo dawn | rim glow at golden hour | edge-light from sobel bright rim + warm bloom |
| `sig_velvet_depth` | velvet depth | dark edges, subject lifts | strong vignette + mid lift + cool shadows |
| `sig_prism_flare` | prism flare | light leaks / prism | anisotropic streaks on highlights + pastel overlay |
| `sig_thermal_spectrum` | thermal | faux FLIR aesthetic | false-color map luminance → ironbow palette |
| `sig_infrared_dream` | IR dream | faux 720nm IR | invert foliage bias, pale skies, high glow |
| `sig_neon_noir` | neon noir | cyber street | crushing mids + magenta/cyan glow edges |
| `sig_liquid_sun` | liquid sun | molten highlight bloom | heavy threshold bloom + warm split |
| `sig_soft_godray` | soft god rays | shafts of light | radial rays from bright source + haze |
| `sig_porcelain_skin` | porcelain | high-end beauty | frequency soft + slight cool mids + eye clarity |
| `sig_cinema_fog` | cinema fog | atmospheric depth | soft haze lift + cool air + vignette |
| `sig_ember_glow` | ember glow | fireplace warmth | deep orange glow map from dark hotspots |
| `sig_arctic_glass` | arctic glass | cold crystalline | teal ice mids + sharp local contrast |
| `sig_biolume` | biolume | underwater night fantasy | deep teal + cyan emissive on lights |
| `sig_paper_print` | paper print | matte gallery print | soft contrast + cream paper tone + gentle grain |
| `sig_hyper_clarity` | hyper clarity | obsessive detail | multi-scale clarity + microcontrast (aggressive) |
| `sig_moon_milk` | moon milk | night soft silver | lift blacks silver + desat + soft bloom |
| `sig_spectrum_split` | spectrum split | RGB fringe creative | channel offset bloom |
| `sig_golden_dust` | golden dust | floating warm particles | warm noise layer in midtones + glow |
| `sig_editorial_chrome` | editorial chrome | magazine hard light | clipped stylish contrast + cool metallics |

### signature design rules

- each must look **obviously different** at 60% strength in gallery
- portrait-safe variants: auto-skin-protect unless look is explicitly “fashion crush”
- thermal / IR / neon: tagged `experimental`; off by default in “pro” enhance

---

## B. 40 color grades (moods × subjects)

### portraits (10)

| id | name | mood |
|----|------|------|
| `grade_portrait_natural` | natural skin | clean, faithful |
| `grade_portrait_soft_peach` | soft peach | beauty / bridal |
| `grade_portrait_cool_editorial` | cool editorial | magazine |
| `grade_portrait_warm_honey` | warm honey | lifestyle |
| `grade_portrait_matte_film` | matte film | faded blacks |
| `grade_portrait_bw_silver` | bw silver | classic mono |
| `grade_portrait_bw_ink` | bw ink | high contrast mono |
| `grade_portrait_teal_safe` | teal-safe | teal env, protected skin |
| `grade_portrait_golden_hour` | golden hour | warm key |
| `grade_portrait_moody_rembrandt` | rembrandt mood | dark, single key |

### food (6)

| id | name | mood |
|----|------|------|
| `grade_food_appetite` | appetite | warm, vibrant plates |
| `grade_food_rustic` | rustic | earthy browns |
| `grade_food_fresh_greens` | fresh greens | grocery / healthy |
| `grade_food_moody_chef` | moody chef | dark restaurant |
| `grade_food_pastel_bakery` | pastel bakery | soft sweets |
| `grade_food_street_night` | street night | neon food stalls |

### landscape / travel (8)

| id | name | mood |
|----|------|------|
| `grade_land_vivid_sky` | vivid sky | travel postcard |
| `grade_land_misty` | misty | soft fog |
| `grade_land_autumn` | autumn | warm foliage |
| `grade_land_arctic` | arctic | cold blues |
| `grade_land_desert` | desert | sand / amber |
| `grade_land_jungle` | jungle | deep greens |
| `grade_land_bw_dramatic` | bw dramatic | Ansel-ish punch |
| `grade_land_pastel_travel` | pastel travel | soft IG |

### street / urban (5)

| id | name | mood |
|----|------|------|
| `grade_street_chrome` | chrome | city grit |
| `grade_street_night_neon` | night neon | nightlife |
| `grade_street_rain` | rain | cool wet asphalt |
| `grade_street_film80s` | film 80s | nostalgia |
| `grade_street_bleach` | bleach bypass | harsh desat |

### wedding / event (4)

| id | name | mood |
|----|------|------|
| `grade_event_romantic` | romantic | soft pink-warm |
| `grade_event_champagne` | champagne | luminous gold |
| `grade_event_documentary` | documentary | honest / flat contrast |
| `grade_event_sparkle` | sparkle | highlights glitter |

### general / cinema (7)

| id | name | mood |
|----|------|------|
| `grade_cine_teal_orange` | teal orange | blockbuster (skin-safe) |
| `grade_cine_bleach` | bleach | action desat |
| `grade_cine_pastel` | pastel cine | soft contrast color |
| `grade_cine_noir` | noir | crushed, smoky |
| `grade_still_product` | product clean | ecommerce white |
| `grade_still_vintage` | vintage | sepia-lean fade |
| `grade_still_hdr_subtle` | hdr subtle | local tone map mild |

---

## C. enhance defaults (meta looks)

| id | maps to |
|----|---------|
| `enhance_natural` | recipe only, no signature |
| `enhance_glow` | recipe + mild floating light |
| `enhance_portrait` | recipe + porcelain light path |
| `enhance_landscape` | recipe + sky enhancer |
| `enhance_food` | recipe + appetite grade lean |

---

## D. perceptual QA notes (grades)

quick visual checks at **100% grade strength** on reference sets in `samples/`:

| tag | pass criteria |
|-----|----------------|
| portrait | skin hue stable; no orange/teal shift on cheeks at 100% |
| food | whites on plates stay neutral; greens not neon |
| landscape | sky gradient smooth; no halos on tree lines |
| street | neons pop without color bleed into skin |
| wedding | highlights soft; no clipped bridal dress |
| cinema | teal-orange separation readable; skin not mint |
| still | product edges crisp; no muddy shadows |

stacking with **AI enhance @ 50%** then grade @ 100%: grade should read as color mood, not second exposure pass.

problem grades to watch: `grade_portrait_bw_ink` (crush on dark skin), `grade_street_bleach` (over-desat), `grade_food_street_night` (fringe on small plates).

---

## E. showcase gallery requirements

for local web visual showcase (`/showcase`):

- 3 demo images per category (portrait / food / land) — user-supplied or libre-licensed set in `samples/`
- before | enhance | signature | grade tiles
- slider compare component

do **not** ship copyrighted luminar sample packs.
