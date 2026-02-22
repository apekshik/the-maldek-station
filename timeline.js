/**
 * Timeline rendering — chronological milestone view.
 * Depends on images-data.js and lightbox.js.
 */

function formatDate(iso) {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

function renderTimeline() {
  const container = document.getElementById('timeline-container');
  const sorted = [...MILESTONES].sort((a, b) => a.date.localeCompare(b.date));

  let html = '<div class="timeline-track">';

  sorted.forEach(milestone => {
    const images = IMAGES
      .filter(img => img.phase === milestone.id)
      .sort((a, b) => a.date.localeCompare(b.date));

    html += `
      <div class="timeline-milestone">
        <div class="milestone-dot"></div>
        <div class="milestone-title">${milestone.title}</div>
        <div class="milestone-date">${formatDate(milestone.date)}</div>
        <div class="milestone-desc">${milestone.description}</div>
        <div class="timeline-cards">
    `;

    images.forEach(img => {
      const tagHTML = img.tags.map(t => `<span class="img-tag">${t}</span>`).join('');
      html += `
        <div class="timeline-card" data-src="${img.src}" data-caption="${img.caption}">
          <img src="${img.src}" alt="${img.caption}" loading="lazy">
          <div class="timeline-card-info">
            <div class="timeline-card-caption">${img.caption}</div>
            <div class="timeline-card-tags">${tagHTML}</div>
          </div>
        </div>
      `;
    });

    html += '</div></div>';
  });

  html += '</div>';
  container.innerHTML = html;

  container.querySelectorAll('.timeline-card').forEach(card => {
    card.addEventListener('click', () => {
      openLightbox(card.dataset.src, card.dataset.caption);
    });
  });
}

document.addEventListener('DOMContentLoaded', renderTimeline);
