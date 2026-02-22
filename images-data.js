/**
 * Shared image data layer — consumed by gallery.js and timeline.js
 */

const PHASES = [
  { id: 'early-concept', label: 'Early Concept' }
];

const MILESTONES = [
  {
    id: 'early-concept',
    title: 'Early Concept',
    date: '2026-02-01',
    description: 'Initial visual exploration — establishing tone, atmosphere, and core environment language for the station.'
  }
];

const SECTIONS = [
  {
    id: 'station-exterior',
    title: 'Station Exterior',
    desc: 'The building from outside — isolated, fog-wrapped, a single warm light.'
  },
  {
    id: 'platform',
    title: 'Platform & Dock',
    desc: 'Open air, wet concrete, industrial lamps cutting through fog.'
  },
  {
    id: 'gondola',
    title: 'Gondola',
    desc: 'The car that travels to Maldek and returns. An artifact from the other place.'
  },
  {
    id: 'control-room',
    title: 'Control Room',
    desc: 'The cockpit. Analog gauges, warm light, a window looking out at the mountain.'
  }
];

const IMAGES = [
  // Station Exterior
  {
    id: 'ext-night',
    src: 'assets/reference/station-exterior-night.png',
    caption: 'Lower station exterior at night — "THE LOWER STATION" sign, warm interior glow',
    tags: ['exterior', 'night', 'station', 'mood'],
    phase: 'early-concept',
    date: '2026-02-03',
    sectionId: 'station-exterior'
  },
  {
    id: 'ext-dusk',
    src: 'assets/reference/station-exterior-dusk.png',
    caption: 'Station at dusk — concrete and timber, mountains behind, single lit window',
    tags: ['exterior', 'dusk', 'station', 'mood'],
    phase: 'early-concept',
    date: '2026-02-03',
    sectionId: 'station-exterior'
  },
  {
    id: 'ext-fog',
    src: 'assets/reference/station-mountainside-fog.png',
    caption: 'Mountainside station in fog — gondola approaching, warm light from inside',
    tags: ['exterior', 'fog', 'station', 'gondola'],
    phase: 'early-concept',
    date: '2026-02-04',
    sectionId: 'station-exterior'
  },
  // Platform & Dock
  {
    id: 'plat-fog',
    src: 'assets/reference/platform-fog-pov.jpg',
    caption: 'Platform POV — cable ascending into fog, control room warm light ahead',
    tags: ['platform', 'fog', 'night', 'mood'],
    phase: 'early-concept',
    date: '2026-02-05',
    sectionId: 'platform'
  },
  {
    id: 'plat-dock',
    src: 'assets/reference/platform-gondola-docking.png',
    caption: 'Gondola docking at platform — two overhead lamps, fog rolling in',
    tags: ['platform', 'gondola', 'fog', 'night'],
    phase: 'early-concept',
    date: '2026-02-05',
    sectionId: 'platform'
  },
  {
    id: 'plat-arrival',
    src: 'assets/reference/platform-gondola-arrival.png',
    caption: 'Gondola arriving — red signal light, wet platform surface, forest behind',
    tags: ['platform', 'gondola', 'night', 'mood'],
    phase: 'early-concept',
    date: '2026-02-06',
    sectionId: 'platform'
  },
  // Gondola
  {
    id: 'gond-fog',
    src: 'assets/reference/gondola-foggy-mountain.jpg',
    caption: 'Gondola on cable — foggy mountains, small station visible below',
    tags: ['gondola', 'fog', 'exterior', 'mood'],
    phase: 'early-concept',
    date: '2026-02-07',
    sectionId: 'gondola'
  },
  {
    id: 'gond-red',
    src: 'assets/reference/gondola-red-docked.png',
    caption: 'Red gondola docked — overhead lamps, wet concrete, dark forest',
    tags: ['gondola', 'platform', 'night'],
    phase: 'early-concept',
    date: '2026-02-07',
    sectionId: 'gondola'
  },
  {
    id: 'gond-modern',
    src: 'assets/reference/gondola-modern-arriving.jpg',
    caption: 'Modern gondola approaching station — wet platform, mountain fog',
    tags: ['gondola', 'platform', 'fog', 'exterior'],
    phase: 'early-concept',
    date: '2026-02-08',
    sectionId: 'gondola'
  },
  {
    id: 'gond-interior',
    src: 'assets/reference/gondola-interior-benches.png',
    caption: 'Gondola interior — wooden benches, dome light, steamy windows',
    tags: ['gondola', 'interior', 'mood'],
    phase: 'early-concept',
    date: '2026-02-08',
    sectionId: 'gondola'
  },
  // Control Room
  {
    id: 'ctrl-panel',
    src: 'assets/reference/control-room-panel-detail.png',
    caption: 'Control panel detail — gauges, levers, logbook, desk lamp, gondola visible through window',
    tags: ['interior', 'control-room', 'mood'],
    phase: 'early-concept',
    date: '2026-02-09',
    sectionId: 'control-room'
  },
  {
    id: 'ctrl-room',
    src: 'assets/reference/control-room-interior.png',
    caption: 'Control room interior — panel, chair, window view to platform and cable',
    tags: ['interior', 'control-room'],
    phase: 'early-concept',
    date: '2026-02-10',
    sectionId: 'control-room'
  }
];

// Helpers

function getImagesForSection(sectionId) {
  return IMAGES.filter(img => img.sectionId === sectionId);
}

function getAllTags() {
  const tags = new Set();
  IMAGES.forEach(img => img.tags.forEach(t => tags.add(t)));
  return Array.from(tags).sort();
}

function getActivePhases() {
  const ids = new Set(IMAGES.map(img => img.phase));
  return PHASES.filter(p => ids.has(p.id));
}
