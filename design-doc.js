/**
 * GDD markdown viewer — fetches and renders the design document.
 */

document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('doc-content');

  try {
    const res = await fetch('the-maldek-station-gdd.md');
    if (!res.ok) throw new Error(res.statusText);
    const md = await res.text();
    container.innerHTML = marked.parse(md);
  } catch (err) {
    container.innerHTML = '<p class="doc-loading">Failed to load document.</p>';
  }
});
