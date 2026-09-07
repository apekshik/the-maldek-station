# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**The Maldek Station** — a cable car horror game built in Unreal Engine 5, with a companion design bible site.

### Repository Structure

```
the-maldek-station/
  docs/       ← static design bible / documentation site
  game/       ← Unreal Engine 5 project (future)
  art/blender/ ← editable blockout, scripts, previews and FBX handoff
```

## Design Bible Site (`docs/`)

A static design bible / documentation site. No build tools, no framework — pure HTML/CSS/JS served as static files.

### Development

Serve locally (required for the design doc page which uses `fetch()`):
```
python3 -m http.server 8000 -d docs
```
Open `http://localhost:8000`. No install step, no build step.

### Architecture

**Pages:** `docs/index.html` (landing), `docs/floorplan.html` (interactive SVG), `docs/gallery.html` (filtered reference images), `docs/timeline.html` (chronological milestones), `docs/design-doc.html` (renders GDD markdown).

**Shared data layer:** `docs/images-data.js` is the single source of truth for all image metadata. It declares globals (`PHASES`, `IMAGES`, `SECTIONS`, `MILESTONES`, helper functions) consumed by both `gallery.js` and `timeline.js`. When adding images, only edit `images-data.js`.

**Shared lightbox:** `docs/lightbox.js` exposes `openLightbox(src, caption)` and `closeLightbox()` as globals. Both gallery and timeline pages include the same lightbox HTML markup and this script.

**Floor plan:** `docs/floorplan.html` contains V1/V2 tabs and their inline SVGs. Preserve V1 when editing V2. `docs/zones.js` holds original zone data and the shared sidebar renderer; `docs/zones-v2.js` holds the expanded compound data. `docs/floorplan.js` scopes zoom/pan/selection to each version panel. V2 has 2D/3D switches in `docs/floorplan-views.js`, which lazily imports `docs/floorplan-3d.js`. The Three.js blockout supports stacked, exploded, and lower-only views. Its dimensions are provisional; the 2D map offsets the lower level for readability. Room selection is synchronized through scoped `maldek:select-zone` / `maldek:zone-selected` events. Three.js 0.180.0 and OrbitControls are vendored with their MIT license under `docs/vendor/three/`; no build step or runtime CDN is needed for the model.

**Design doc:** `docs/design-doc.js` fetches `the-maldek-station-gdd.md` and renders it with `marked.js` (loaded from CDN). The GDD markdown file is the source of truth — edit it directly and the site reflects changes on reload.

**Script load order matters.** Pages that use the shared layer must load scripts in this order:
```html
<script src="images-data.js"></script>
<script src="lightbox.js"></script>
<script src="gallery.js"></script>  <!-- or timeline.js -->
```

### Conventions

- All JS uses global scope (no modules/bundler). Functions and data are shared via global variables.
- Every page includes the grain overlay div (`<div class="grain"></div>`) and the same `<nav class="site-nav">` structure. When adding a new page, add its nav link to all existing pages.
- CSS is in a single `docs/styles.css` with sections marked by comment headers. New page styles go before the `/* Responsive */` block. Responsive overrides go inside the `@media (max-width: 900px)` block at the end.
- Typography: `Instrument Serif` for headings, `DM Mono` for body/UI. Both from Google Fonts (imported in CSS).
- Color palette: `#0a0a0b` background, `#c8c5b8` primary text, `#e8e5d8` headings, `#1a1a1c` borders, `#4a4840` accents.
- Images live in `docs/assets/reference/`. Each image entry in `images-data.js` has: `id`, `src`, `caption`, `tags`, `phase`, `date`, `sectionId`.

## Game (`game/`)

Unreal Engine 5.7 project at `game/game.uproject`, including an existing BlockOut map and gondola/weather content. Inspect the current project before adding replacement systems. The `.gitignore` at the repo root includes standard UE5 ignore rules.

## Blender blockout (`art/blender/`)

Before creating or importing architectural meshes, read [Mesh authoring lessons](art/MESH_AUTHORING.md). It records the R12 z-fighting causes, concealed-core repair, separate Nanite fallback issue, and proactive source/export/rapid-frame checks. Apply these lessons to future openings and layered surfaces.

`millford_v2_blockout_01.blend` is the first metre-scale architectural pass. Read `art/blender/BLOCKOUT_README.md` before editing or exporting. `scripts/build_millford.py` generates revision 01 from scratch in a separate background Blender process; do not rerun it over hand-edited work. `scripts/validate_and_export.py` runs geometry samples, exports named chunks with UCX hulls and checks FBX re-import bounds. UE5 movement/import validation remains pending. The HTML map is still the earlier schematic; it is not the dimensional source of truth for this Blender revision.

Latest environment study: `art/blender/revision_03/millford_v2_night_03.blend`. Read its `README.md` for the continuous relay paths, relocated hut, CC0 pine source, distant cable route and rainy night cameras. Revision 03 has sampled geometry validation but no refreshed FBX export. Keep all earlier revisions and save hand edits under a new filename.

Windows continuation plan: `art/blender/WINDOWS_HANDOFF_AND_REFINEMENT_PLAN.md`. It records LFS checkout, RTX/OptiX baseline, before/after screenshot audit and the ranked model-detail pass.

## General

- Don't say "claude" or "anthropic" in commit messages.
