# Plan: Omalovánky — Personal kids' activity generator

## Context

The user (Petr, Prague, three kids) wants a single-file, Czech-language web app that generates printable activity pages tailored to **each individual child**. There are no hardcoded subjects: every topic, theme, and decoration is defined by the parent at runtime. Each kid has their own profile with their own age, name, favourite topics, themes, and decorations.

The project lives at `/home/user/painting-generator` (sibling of `~/Mobile`, no link to the snake game). It will be developed locally with no rush to publish — the constraint is that the final artifact remains a single `index.html` deployable to GitHub Pages later.

Confirmed answers from earlier in the session:
- **Definability**: prompt **OR** upload (both supported)
- **Connectivity**: online OK (free image API + Google Fonts)
- **Profiles**: per-kid profiles
- **Stack**: single `index.html`, vanilla JS, no build step
- **Language**: Czech UI only
- **Output**: printable PDFs, including a multi-page "playful paperback" book

---

## Why I'm planning before coding

The user has stacked requirements over several messages: profiles, prompt+upload definability, age levels, four activity types (coloring + connect-the-dots + maze + tracing), gallery with filters, Czech text overlay, paperback output. Some interact non-obviously:

- Connect-the-dots needs vector contour data → prompt-generated images need post-processing.
- Mazes are procedural and barely use the topic → they're a special case.
- Profiles must scope every list (topics, themes, decorations, gallery, generated PDFs).

Locking the model now prevents costly rewrites later.

---

## Socratic walkthrough

### F0 — Per-kid profiles (foundation)

- **Q: What is a profile?** A named record per child: `{ id, name, age, color, createdAt, topics: [], themes: [], details: [] }`. Each child also gets a colour for visual differentiation in the UI.
- **Q: How does the user switch?** Profile chips at the very top of the page. Tap a chip → that profile becomes active → the generator and gallery filter to it. A `+ Přidat dítě` button opens a small modal (name, age, color).
- **Q: Where do profiles live?** `localStorage` under `omalovanky-profiles`. Active profile id under `omalovanky-active`.
- **Q: First run?** No profiles exist → onboarding modal asks for first child's name and age. Cannot use the app until at least one profile exists.
- **Q: Are topics/themes/details shared between profiles?** No. Each profile has its own. (V2 could add a "copy from sibling" button.)
- **Q: Is the gallery shared?** Each gallery item is tagged with a `profileId`; the gallery view filters to the active profile by default but a "Všechny děti" filter shows everything.

### F1 — Topic / Theme / Details: prompt OR upload

- **Q: What is a "topic" in this design?** A reusable building block in the active profile's library. Can be either:
  - **Prompt fragment** — Czech free text the user typed (e.g. "T-Rex", "Bagr Liebherr", "Princezna na koni"). Stored as a string.
  - **Uploaded image** — PNG/JPG/SVG file the parent supplied. Stored as a base64 data URL.
- **Q: Same shape for themes and details?** Yes. Themes are environment fragments ("ve vesmíru", "pod vodou"). Details are accessory fragments ("s korunou", "se slunečními brýlemi"). All three lists hold either prompt strings or uploaded images.
- **Q: How does the user add one?** Each section has a `+ Přidat` button that opens a small modal:
  - Tab 1: **Text** — type the Czech phrase, press Save
  - Tab 2: **Soubor** — drag-drop or browse for an image file
  - Each entry gets a label (auto from text, or filename for uploads).
- **Q: Can the user delete/rename?** Yes. Each chip in the list has a × delete button and double-click to rename.
- **Q: Why this design?** It models how parents actually think about their kids' preferences ("Honzík loves dinosaurs and excavators; Tomáš loves princesses and unicorns") without forcing the parent to draw anything.

### F2 — Image generation pipeline

- **Q: How does the app turn a topic + theme + details + age into an image?** Two paths depending on the topic source:

  **Path A — Prompt-based (topic is text):**
  1. Combine fragments into a single prompt: `[topic]` + `[theme]` + `[details]` + `, černobílá omalovánka pro děti, silné obrysy, jednoduché tvary, bez stínování, bílé pozadí`
  2. Map age → suffix: `pro [age] leté dítě`
  3. URL-encode and call Pollinations.ai:
     `https://image.pollinations.ai/prompt/{encodedPrompt}?width=1024&height=1024&nologo=true&seed={randomSeed}&model=flux`
  4. The response is a PNG image. Load it into an `Image` element directly (CORS-friendly, no key, no auth).
  5. Optional client-side post-processing: increase contrast and threshold to true black-and-white via canvas pixel manipulation, so the result looks more like coloring-page line art even if the API returns a softer image.

  **Path B — Upload-based (topic is image):**
  1. Use the uploaded image directly as the base.
  2. Optional toggle: "Převést na omalovánku" — runs a small in-browser Canny edge detector (custom JS, ~80 LOC, no OpenCV.js dependency) to convert the photo to line art.
  3. Skip the API entirely. Themes and details from prompts are ignored for upload topics (we can't re-mix a raster image).

- **Q: What about errors?** Pollinations sometimes returns a degraded image. Show a "Zkusit znovu" button on each gallery card that re-rolls the seed.
- **Q: Why Pollinations specifically?** It is the only well-known free image API that:
  - Requires no API key
  - Returns the image directly from a URL (works from static HTML)
  - Is CORS-friendly
  - Has a "flux" model that handles English-and-Czech prompts well
  - Has been stable since 2023
  Backup: Hugging Face Inference API (also free, also no key for some models, slightly more setup).

### F3 — Czech text overlay with playful font

- **Q: Which font?** Google Fonts **Fredoka** weights 400/600/700 — rounded, kid-friendly, full Czech diacritics support. Loaded via `<link>` from `fonts.googleapis.com`.
- **Q: How does the text appear?** Outlined hollow letters in a colour drawn from the kid's profile colour. Positioned at the bottom of the page so the kid can colour the title too.
- **Q: How does it survive PDF rasterization?** Render base image to a high-res canvas first, then `ctx.fillText` + `ctx.strokeText` the Czech string on top. `await document.fonts.load('bold 64px Fredoka')` before drawing so the canvas has the font.
- **Q: Per-image text?** Yes. The generator form has a `Tvůj text` field that ends up overlaid on every image in the batch.

### F4 — Age level selection

- **Q: Granularity?** Three brackets:
  - **2–3 let** (toddler) — chunky shapes, no small details, no text overlay or just first letter
  - **4–5 let** (preschool) — default; standard activities
  - **6–8 let** (school) — finer details, harder puzzles
- **Q: How does age affect output?** Affects three things:
  1. The **prompt suffix** sent to Pollinations (`pro 4 leté dítě, jednoduché tvary` vs `pro 7 leté dítě, více detailů`)
  2. The **post-processing** threshold (younger = thicker, simpler edges)
  3. The available **activity types** (no maze for 2–3 yrs, no connect-the-dots for 2–3 yrs)
- **Q: Where does age live?** On the profile, but overrideable per-generation.

### F5 — Activity types (puzzle pages)

- **Q: Which types ship in v1?**
  - **Omalovánka** (coloring) — base; every age
  - **Obtahovačka** (tracing) — every age; same image with `stroke-dasharray`-style dashed conversion via canvas
  - **Spoj tečky** (connect-the-dots) — 4+; needs contour extraction
  - **Bludiště** (maze) — 4+; procedurally generated, ignores topic except as start/end icon
- **Q: Connect-the-dots — how exactly?**
  1. Take the generated/uploaded image
  2. Run Canny edge detection (same impl as upload mode)
  3. Trace the longest connected contour
  4. Sample N evenly-spaced points along it (N varies by age: 8/15/30)
  5. Render numbered dots on a blank canvas
  6. Discard the line art
- **Q: Maze — how?** Recursive backtracker on a grid. Grid size varies by age (6×6 / 10×10 / 14×14). Render a tiny version of the topic icon at the entrance and exit.
- **Q: Unified or per-type form?** Unified. Form has a `Typ aktivity` dropdown; the rest of the form is shared. The picker hides types that are inappropriate for the current age.
- **Q: Deferred to v2?** Color-by-number, Spot-the-difference, Find-and-count.

### F6 — Count: how many pictures per click

- **Q: What does count mean?** Number of variant images to generate in one batch from the same form settings. 1–12.
- **Q: Variation source?**
  - For prompt topics: each variant uses a different random seed in the Pollinations URL, so the API returns different images
  - For upload topics: each variant just re-applies post-processing with slightly different parameters (line thickness, threshold). Useful if the user wants a few options to print
- **Q: Progress UI?** A small progress bar during batch generation. The grid populates as each image arrives. Errors don't block siblings.

### F7 — Gallery with labels and filters

- **Q: Storage shape?** Each entry: `{ id, profileId, type, topicLabel, themeLabel, detailLabels, age, text, seed, createdAt, imageDataUrl }`. Stored under `omalovanky-gallery`. Each image is base64 PNG (~30–80 KB), so localStorage can hold a few hundred items per origin (5 MB cap).
- **Q: Card layout?** Image thumbnail + chip row (Type / Topic / Theme / Age) + Czech text + date + per-card actions: PDF, Smazat, Re-roll (regenerate same settings with new seed).
- **Q: Filter controls?** Profile (default = active), Type, Topic, Theme, Age, free-text search (matches Czech text). All combinable.
- **Q: Bulk actions?** "Smazat vše" (with confirmation), "Vytvořit knížku z výběru".

### F8 — Playful paperback output

- **Q: What is the paperback?** A multi-page A4 PDF formatted like a printed activity book:
  - **Cover page** — big title from a modal input (default: "OMALOVÁNKY pro [Jméno]"), child's name and age, decorative border in the kid's profile colour
  - **One activity per page** — title on top in Fredoka, big centred image, type-specific footer hint ("Vybarvi mě!" / "Spoj tečky" / "Najdi cestu" / "Obtáhni linky"), page number bottom-right
  - **Back cover** — simple thank-you page, optional
- **Q: Trigger?** Two entry points:
  1. From the gallery: "Vytvořit knížku z galerie" — bundles all currently-filtered items
  2. From a multi-select mode: tick checkboxes on cards, "Vytvořit knížku z výběru"
- **Q: Cover customization?** Modal asks for: book title (default: "OMALOVÁNKY pro [Jméno]"), child's name (default: from profile), age (default: from profile), date (default: today). All editable.
- **Q: Empty?** Button is disabled when no items match.

---

## Recommended architecture

```
index.html  (single file, ~1200–1600 LOC)
├── <head>
│   ├── meta + Google Fonts (Fredoka 400/600/700)
│   └── <style> bright/playful CSS, mobile-first grid
├── <body>
│   ├── #profile-bar — chips for each kid + "+ Přidat dítě"
│   ├── #generator section
│   │   ├── topic select (from active profile's topics)
│   │   ├── theme select (from active profile's themes)
│   │   ├── details checkboxes (from active profile's details)
│   │   ├── type select (omalovánka / obtahovačka / spoj tečky / bludiště)
│   │   ├── age select (override profile age)
│   │   ├── text input
│   │   ├── count input (1–12)
│   │   └── "VYTVOŘ!" button → progress bar → results
│   ├── #library section (collapsible)
│   │   ├── topics list with + Přidat / × delete / rename
│   │   ├── themes list ditto
│   │   └── details list ditto
│   └── #gallery section
│       ├── filter bar (profile, type, topic, theme, age, search, clear-all)
│       ├── gallery grid
│       └── "VYTVOŘIT KNÍŽKU" button → cover modal → paperback PDF
├── #modals
│   ├── add-profile modal
│   ├── add-topic / add-theme / add-detail modal (text/upload tabs)
│   ├── paperback cover modal
│   └── generic confirm modal
└── <script>
    ├── jsPDF (CDN)
    ├── STORAGE keys + helpers (loadProfiles, saveProfiles, loadGallery, saveGallery)
    ├── PROFILE state (active id, list)
    ├── pollinations(prompt, seed, w, h) → PNG dataURL
    ├── canny(imageDataUrl) → edge dataURL  (~80 LOC custom Sobel+threshold)
    ├── postprocessLineArt(dataUrl, ageProfile) → cleaner dataURL
    ├── generators per type:
    │   ├── genColoring(settings)
    │   ├── genTracing(settings)
    │   ├── genConnectDots(settings)
    │   └── genMaze(settings)
    ├── overlayCzechText(canvas, text, color)
    ├── ageProfile(age) → { strokeBoost, dotCount, mazeGrid, promptSuffix, allowedTypes }
    ├── UI render: profile bar, library, generator form, gallery
    ├── filter logic
    ├── PDF helpers:
    │   ├── singlePagePdf(item)
    │   └── paperbackPdf(items, coverMeta)
    └── init + event wiring
```

## Critical files

- `/home/user/painting-generator/index.html` — single source file. Currently a draft of the wrong (hardcoded library) approach from earlier in the session. Will be fully rewritten.

## Key external dependencies (all loaded from CDN)

| Dependency | Use | URL |
|---|---|---|
| jsPDF 2.5.1 | A4 PDF generation | jsdelivr |
| Google Fonts Fredoka | Czech-friendly playful font | fonts.googleapis.com |
| Pollinations.ai (flux model) | Free image generation, no key | image.pollinations.ai |

## Verification plan

1. Open `index.html` in a desktop browser → onboarding modal asks for first child.
2. Add child "Honzík", age 5, color orange → profile chip appears, generator unlocks.
3. Library: add a topic prompt "T-Rex", a theme "ve vesmíru", a detail "s korunou".
4. Generator: pick those, type "Omalovánka" + age 5, count 3, text "Honzík" → 3 images appear in the gallery from Pollinations.
5. Click PDF on one card → A4 PDF downloads with Fredoka Czech text "Honzík" overlaid at the bottom.
6. Add a second child "Anička", age 3, color pink. Switch profile → generator and gallery filter to her empty library.
7. Switch back to Honzík → his stuff is still there.
8. Filter by Type "Bludiště" → only mazes visible.
9. Generate a maze → grid appears with a tiny T-Rex icon at start/end.
10. Generate a connect-the-dots → numbered dots appear, no line art.
11. Click "Vytvořit knížku z galerie" → cover modal → multi-page PDF with cover + activity pages downloads.
12. Reload browser → profiles, libraries, gallery all survive via localStorage.
13. Mobile viewport (375 px) → form collapses to one column, profile chips wrap, buttons stay tappable.
14. Disconnect internet → upload-mode topics still work; prompt-mode topics fail gracefully with a "Žádné připojení" toast.

## V1 scope decisions (locked)

- **Profiles**: required, multi-child, stored in localStorage
- **Topics/Themes/Details**: nothing hardcoded; everything user-defined; prompt OR upload
- **Image source**: Pollinations.ai (flux) for prompts, file upload + custom Canny for uploads
- **Activity types**: Omalovánka, Obtahovačka, Spoj tečky, Bludiště (4)
- **Age brackets**: 2–3 / 4–5 / 6–8 let (3) — affects prompt + post-processing + allowed types
- **Font**: Fredoka via Google Fonts CDN
- **Gallery storage**: localStorage, base64 PNG per item, profile-tagged
- **PDF**: jsPDF 2.5.1 raster (single page + paperback)
- **Paperback**: cover with title/name/age/date from modal + activity pages + page numbers
- **Czech text overlay**: rendered on canvas after raster, in profile colour
- **Local-only**: no remote, no commits, no GitHub Pages until the user says so
- **Deferred to v2**: color-by-number, spot-the-difference, find-and-count, vector PDF, multi-language UI, copy-library-from-sibling
