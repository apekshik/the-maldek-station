/**
 * Floor plan interaction: zoom/pan, zone selection, sightline toggle.
 */

document.addEventListener('DOMContentLoaded', () => {
  const svg = document.querySelector('svg.floorplan');
  const container = document.querySelector('.plan-container');
  const toggleBtn = document.getElementById('toggleSight');
  const sightlines = document.querySelectorAll('.sightline');
  const blindAnnotations = [document.getElementById('blind-1'), document.getElementById('blind-2')];
  const zoomIndicator = document.getElementById('zoom-indicator');

  let sightlinesVisible = false;
  let selectedZone = null;

  // ── Zone selection ──────────────────────────────────────────────

  const zones = document.querySelectorAll('.room');
  const labels = document.querySelectorAll('.room-label');

  function selectZone(zoneId) {
    zones.forEach(z => z.classList.remove('selected'));
    labels.forEach(l => l.classList.remove('selected'));

    const zone = document.getElementById('zone-' + zoneId);
    if (zone) zone.classList.add('selected');

    const label = document.getElementById('label-' + zoneId);
    if (label) label.classList.add('selected');

    document.querySelectorAll('.zone-info').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById('info-' + zoneId);
    if (panel) panel.classList.add('active');

    selectedZone = zoneId;
  }

  zones.forEach(zone => {
    zone.addEventListener('click', (e) => {
      // Don't select if we just dragged
      if (dragMoved) return;
      selectZone(zone.dataset.zone);
    });
  });

  // ── Sightline toggle ───────────────────────────────────────────

  toggleBtn.addEventListener('click', () => {
    sightlinesVisible = !sightlinesVisible;
    toggleBtn.classList.toggle('active', sightlinesVisible);
    toggleBtn.textContent = sightlinesVisible ? 'Hide Sightlines' : 'Show Sightlines';

    sightlines.forEach(s => s.classList.toggle('visible', sightlinesVisible));
    blindAnnotations.forEach(a => {
      if (a) a.style.opacity = sightlinesVisible ? '1' : '0';
    });
  });

  // ── Zoom & Pan ─────────────────────────────────────────────────

  const DEFAULT_VB = { x: 0, y: 0, w: 700, h: 520 };
  const MIN_ZOOM = 0.5;  // viewBox can be 2x the default (zoomed out)
  const MAX_ZOOM = 4;    // viewBox can be 0.25x the default (zoomed in)
  const ZOOM_SENSITIVITY = 0.001;

  let vb = { ...DEFAULT_VB };
  let isPanning = false;
  let panStart = { x: 0, y: 0 };
  let dragMoved = false;

  function currentZoom() {
    return DEFAULT_VB.w / vb.w;
  }

  function applyViewBox() {
    svg.setAttribute('viewBox', `${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
    const zoom = currentZoom();
    if (zoomIndicator) {
      zoomIndicator.textContent = zoom.toFixed(1) + 'x';
      zoomIndicator.style.opacity = Math.abs(zoom - 1) < 0.05 ? '0' : '1';
    }
  }

  function screenToSVG(clientX, clientY) {
    const rect = svg.getBoundingClientRect();
    const sx = (clientX - rect.left) / rect.width;
    const sy = (clientY - rect.top) / rect.height;
    return {
      x: vb.x + sx * vb.w,
      y: vb.y + sy * vb.h
    };
  }

  // Wheel → zoom
  container.addEventListener('wheel', (e) => {
    e.preventDefault();

    const zoom = currentZoom();
    const delta = -e.deltaY * ZOOM_SENSITIVITY;
    let newZoom = zoom * (1 + delta);
    newZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, newZoom));

    const factor = zoom / newZoom;

    // Zoom toward cursor position
    const cursor = screenToSVG(e.clientX, e.clientY);
    vb.x = cursor.x - (cursor.x - vb.x) * factor;
    vb.y = cursor.y - (cursor.y - vb.y) * factor;
    vb.w = DEFAULT_VB.w / newZoom;
    vb.h = DEFAULT_VB.h / newZoom;

    applyViewBox();
  }, { passive: false });

  // Mouse drag → pan
  svg.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    isPanning = true;
    dragMoved = false;
    panStart = { x: e.clientX, y: e.clientY };
    container.classList.add('panning');
  });

  window.addEventListener('mousemove', (e) => {
    if (!isPanning) return;

    const dx = e.clientX - panStart.x;
    const dy = e.clientY - panStart.y;

    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
      dragMoved = true;
    }

    const rect = svg.getBoundingClientRect();
    const svgDX = (dx / rect.width) * vb.w;
    const svgDY = (dy / rect.height) * vb.h;

    vb.x -= svgDX;
    vb.y -= svgDY;

    panStart = { x: e.clientX, y: e.clientY };
    applyViewBox();
  });

  window.addEventListener('mouseup', () => {
    if (isPanning) {
      isPanning = false;
      container.classList.remove('panning');
      // Reset dragMoved after a tick so the click handler can check it
      setTimeout(() => { dragMoved = false; }, 0);
    }
  });

  // Double-click → reset view
  svg.addEventListener('dblclick', (e) => {
    e.preventDefault();
    vb = { ...DEFAULT_VB };
    applyViewBox();
  });

  // Touch support
  let lastTouchDist = null;
  let lastTouchCenter = null;

  svg.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      isPanning = true;
      dragMoved = false;
      panStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      container.classList.add('panning');
    } else if (e.touches.length === 2) {
      isPanning = false;
      const dx = e.touches[1].clientX - e.touches[0].clientX;
      const dy = e.touches[1].clientY - e.touches[0].clientY;
      lastTouchDist = Math.hypot(dx, dy);
      lastTouchCenter = {
        x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
        y: (e.touches[0].clientY + e.touches[1].clientY) / 2
      };
    }
  }, { passive: true });

  svg.addEventListener('touchmove', (e) => {
    e.preventDefault();

    if (e.touches.length === 1 && isPanning) {
      const dx = e.touches[0].clientX - panStart.x;
      const dy = e.touches[0].clientY - panStart.y;

      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) dragMoved = true;

      const rect = svg.getBoundingClientRect();
      vb.x -= (dx / rect.width) * vb.w;
      vb.y -= (dy / rect.height) * vb.h;
      panStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      applyViewBox();

    } else if (e.touches.length === 2 && lastTouchDist !== null) {
      const dx = e.touches[1].clientX - e.touches[0].clientX;
      const dy = e.touches[1].clientY - e.touches[0].clientY;
      const dist = Math.hypot(dx, dy);
      const scale = dist / lastTouchDist;

      const center = {
        x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
        y: (e.touches[0].clientY + e.touches[1].clientY) / 2
      };

      const zoom = currentZoom();
      let newZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom * scale));
      const factor = zoom / newZoom;

      const cursor = screenToSVG(center.x, center.y);
      vb.x = cursor.x - (cursor.x - vb.x) * factor;
      vb.y = cursor.y - (cursor.y - vb.y) * factor;
      vb.w = DEFAULT_VB.w / newZoom;
      vb.h = DEFAULT_VB.h / newZoom;

      lastTouchDist = dist;
      lastTouchCenter = center;
      applyViewBox();
    }
  }, { passive: false });

  svg.addEventListener('touchend', () => {
    isPanning = false;
    lastTouchDist = null;
    lastTouchCenter = null;
    container.classList.remove('panning');
    setTimeout(() => { dragMoved = false; }, 0);
  });

  // ── Sidebar resize ──────────────────────────────────────────────

  const resizeHandle = document.getElementById('resize-handle');
  const sidebar = document.getElementById('zone-panels');

  if (resizeHandle && sidebar) {
    let isResizing = false;

    resizeHandle.addEventListener('mousedown', (e) => {
      e.preventDefault();
      isResizing = true;
      resizeHandle.classList.add('active');
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    });

    window.addEventListener('mousemove', (e) => {
      if (!isResizing) return;
      const newWidth = window.innerWidth - e.clientX;
      const clamped = Math.max(200, Math.min(600, newWidth));
      sidebar.style.width = clamped + 'px';
    });

    window.addEventListener('mouseup', () => {
      if (isResizing) {
        isResizing = false;
        resizeHandle.classList.remove('active');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    });
  }

  // Initialize
  applyViewBox();
});
