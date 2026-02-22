/**
 * Gallery rendering with dual phase + tag filtering.
 * Depends on images-data.js (SECTIONS, IMAGES, helpers) and lightbox.js.
 */

let activePhase = null;
let activeTag = null;

function renderFilters() {
  const container = document.getElementById('gallery-filters');
  const phases = getActivePhases();
  const tags = getAllTags();

  let html = '';

  // Phase row
  html += '<div class="filter-row">';
  html += '<span class="filter-row-label">Phase</span>';
  html += '<button class="filter-tag active" data-phase="">All</button>';
  phases.forEach(p => {
    html += `<button class="filter-tag" data-phase="${p.id}">${p.label}</button>`;
  });
  html += '</div>';

  // Tags row
  html += '<div class="filter-row">';
  html += '<span class="filter-row-label">Tags</span>';
  html += '<button class="filter-tag active" data-tag="">All</button>';
  tags.forEach(tag => {
    html += `<button class="filter-tag" data-tag="${tag}">${tag}</button>`;
  });
  html += '</div>';

  container.innerHTML = html;

  // Phase row click
  const phaseRow = container.querySelector('.filter-row:first-child');
  phaseRow.addEventListener('click', (e) => {
    const btn = e.target.closest('.filter-tag');
    if (!btn) return;
    phaseRow.querySelectorAll('.filter-tag').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activePhase = btn.dataset.phase || null;
    renderSections();
  });

  // Tag row click
  const tagRow = container.querySelector('.filter-row:nth-child(2)');
  tagRow.addEventListener('click', (e) => {
    const btn = e.target.closest('.filter-tag');
    if (!btn) return;
    tagRow.querySelectorAll('.filter-tag').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeTag = btn.dataset.tag || null;
    renderSections();
  });
}

function filterImage(img) {
  return (!activePhase || img.phase === activePhase) &&
         (!activeTag || img.tags.includes(activeTag));
}

function renderSections() {
  const container = document.getElementById('gallery-sections');
  let html = '';

  SECTIONS.forEach(section => {
    const sectionImages = getImagesForSection(section.id);
    const filtered = sectionImages.filter(filterImage);

    if (filtered.length === 0) return;

    html += `
      <section class="gallery-section" id="section-${section.id}">
        <div class="section-header">
          <h2>${section.title}</h2>
          <p>${section.desc}</p>
        </div>
        <div class="gallery-grid">
    `;

    filtered.forEach(img => {
      const tagHTML = img.tags.map(t => `<span class="img-tag">${t}</span>`).join('');
      html += `
        <div class="gallery-item" data-src="${img.src}" data-caption="${img.caption}">
          <img src="${img.src}" alt="${img.caption}" loading="lazy">
          <div class="gallery-item-overlay">
            <div class="gallery-item-tags">${tagHTML}</div>
          </div>
        </div>
      `;
    });

    html += '</div></section>';
  });

  container.innerHTML = html;

  container.querySelectorAll('.gallery-item').forEach(item => {
    item.addEventListener('click', () => {
      openLightbox(item.dataset.src, item.dataset.caption);
    });
  });
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  renderFilters();
  renderSections();
});
