# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A static design bible / documentation site for **The Maldek Station**, a cable car horror game. No build tools, no framework — pure HTML/CSS/JS served as static files.

## Development

Serve locally (required for the design doc page which uses `fetch()`):
```
python3 -m http.server 8000
```
Open `http://localhost:8000`. No install step, no build step.

## Architecture

**Pages:** `index.html` (landing), `floorplan.html` (interactive SVG), `gallery.html` (filtered reference images), `timeline.html` (chronological milestones), `design-doc.html` (renders GDD markdown).

**Shared data layer:** `images-data.js` is the single source of truth for all image metadata. It declares globals (`PHASES`, `IMAGES`, `SECTIONS`, `MILESTONES`, helper functions) consumed by both `gallery.js` and `timeline.js`. When adding images, only edit `images-data.js`.

**Shared lightbox:** `lightbox.js` exposes `openLightbox(src, caption)` and `closeLightbox()` as globals. Both gallery and timeline pages include the same lightbox HTML markup and this script.

**Floor plan:** `zones.js` holds zone data (contents, horror potential) and renders sidebar panels. `floorplan.js` handles SVG zoom/pan/selection. The SVG is inline in `floorplan.html`, not a separate file.

**Design doc:** `design-doc.js` fetches `the-maldek-station-gdd.md` and renders it with `marked.js` (loaded from CDN). The GDD markdown file is the source of truth — edit it directly and the site reflects changes on reload.

**Script load order matters.** Pages that use the shared layer must load scripts in this order:
```html
<script src="images-data.js"></script>
<script src="lightbox.js"></script>
<script src="gallery.js"></script>  <!-- or timeline.js -->
```

## Conventions

- All JS uses global scope (no modules/bundler). Functions and data are shared via global variables.
- Every page includes the grain overlay div (`<div class="grain"></div>`) and the same `<nav class="site-nav">` structure. When adding a new page, add its nav link to all existing pages.
- CSS is in a single `styles.css` with sections marked by comment headers. New page styles go before the `/* Responsive */` block. Responsive overrides go inside the `@media (max-width: 900px)` block at the end.
- Typography: `Instrument Serif` for headings, `DM Mono` for body/UI. Both from Google Fonts (imported in CSS).
- Color palette: `#0a0a0b` background, `#c8c5b8` primary text, `#e8e5d8` headings, `#1a1a1c` borders, `#4a4840` accents.
- Images live in `assets/reference/`. Each image entry in `images-data.js` has: `id`, `src`, `caption`, `tags`, `phase`, `date`, `sectionId`.
- Don't say "claude" or "anthropic" in commit messages.
