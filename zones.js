/**
 * Zone data and sidebar rendering for the floor plan.
 */

const ZONES = {
  control: {
    title: 'Control Room',
    role: 'Home base — Information & decisions',
    desc: 'The player\'s safe space. Warm, lit, everything within reach. This is where you monitor the station systems and wait for the car. The large window looks directly at the platform and up toward the mountain — your primary viewport to the outside world.',
    sections: [
      {
        label: 'Control Panel',
        items: [
          ['Cable tension gauge', 'analog dial, most-watched instrument'],
          ['Motor temperature', 'analog dial'],
          ['Brake pressure', 'analog dial'],
          ['Cycle counter', 'mechanical flip display'],
          ['Status lights', 'platform lights, interior, generator, radio, brake, cable drive'],
          ['Drive lever', 'sends/stops the car'],
          ['Brake lever', 'manual brake release'],
          ['Emergency stop', 'under flip cover'],
        ]
      },
      {
        label: 'Desk & Room',
        items: [
          ['Logbook', 'player writes entries each cycle'],
          ['Radio unit', 'dispatch check-ins, incoming transmissions'],
          ['Phone', 'landline to operations office'],
          ['Thermos, pen, desk lamp', null],
          ['Previous operator\'s note', 'first story hook'],
          ['Emergency procedures card', 'laminated'],
          ['Checklist on wall', 'subtle tutorial'],
          ['Cable line map/photo', 'Millford & Maldek stations'],
          ['Coat hook', 'vest + flashlight'],
          ['Space heater', 'warmth source, can fail'],
        ]
      }
    ],
    horror: [
      'Gauges reading impossible values',
      'Log entries appearing that you didn\'t write',
      'Radio activating on its own — wrong voice',
      'Heater failing — cold creeping in',
      'Status lights contradicting reality',
    ]
  },

  platform: {
    title: 'Platform',
    role: 'Transition zone — Exposure & vulnerability',
    desc: 'Open air concrete platform where the gondola docks. Two industrial lamps create a pool of light but the edges fall into black forest. The cable mechanism — a large steel wheel housing — dominates the center. This is where the player is most exposed.',
    sections: [
      {
        label: 'Key Elements',
        items: [
          ['Gondola docking bay', 'recessed channel where the car hangs from the cable'],
          ['Bull wheel mechanism', 'steel housing, cable wraps around'],
          ['Two overhead lamps', 'pools of light, dark edges'],
          ['Safety line markings', 'painted on concrete'],
          ['Cable tensioner', 'manual adjustment point'],
          ['Wet concrete surface', 'mountain condensation'],
        ]
      },
      {
        label: 'Connections',
        items: [
          ['Door to Control Room', '(south-west, same level)'],
          ['Stairs down to Maintenance', '(south-east, ~1m below)'],
          ['Open passage to Overlook', '(east)'],
          ['Exit stairs', '(west, down to parking)'],
        ]
      }
    ],
    horror: [
      'Car arriving while player is elsewhere',
      'Platform lights going out — total darkness',
      'Cable moving on its own — no command sent',
      'Sounds from the forest edge beyond the light',
      'Something standing just outside the lamp radius',
    ]
  },

  overlook: {
    title: 'Overlook',
    role: 'Observation point — Dread & player-driven fear',
    desc: 'A railed balcony at the platform\'s edge with mounted binoculars pointed up the mountain. The most exposed point in the station. Using the binoculars locks your vision — you can\'t see anything around you. Coming here is always the player\'s choice.',
    sections: [
      {
        label: 'Key Elements',
        items: [
          ['Fixed binoculars', 'aimed at Maldek Station'],
          ['Metal railing', 'edge of the world'],
          ['No lamp', 'lit only by spill from platform'],
          ['Unobstructed mountain view', null],
        ]
      }
    ],
    horror: [
      'Maldek station light behaving wrong',
      'Second light appearing on the mountain',
      'Seeing something through binoculars you can\'t unsee',
      'Hearing something behind you while vision is locked',
      'Maldek station no longer being there at all',
    ]
  },

  maintenance: {
    title: 'Maintenance Room',
    role: 'The body — Physical, loud, blind',
    desc: 'Power and electrical hub. Industrial, cold, loud from the generator. Sits ~1m below platform level — reaching it means crossing the exposed platform and descending a stairway. When you\'re down here, you can\'t hear subtle sounds and can\'t see the control panel or platform above. A rear door opens to the exterior where the bulk fuel tank sits on a concrete pad behind the station. The game pulls you here when it wants you vulnerable — and on bad nights, pulls you outside.',
    sections: [
      {
        label: 'Key Elements',
        items: [
          ['Diesel generator', 'noisy, warm, powers the entire station'],
          ['Fuel drum + hand pump', 'shift supply — enough for a normal night'],
          ['Circuit breaker panel', 'labeled breakers, distributes power to all systems'],
          ['Tool rack', 'wrench, pliers, pry bar, cable grease'],
          ['Workbench + vise', 'spare parts'],
          ['Previous operator\'s locker', 'narrative items'],
          ['Rust-stained sink', null],
        ]
      },
      {
        label: 'Exterior — Behind Station',
        items: [
          ['Bulk diesel tank', 'main fuel reserve, on concrete pad'],
          ['Rear door access', 'only way to reach the tank — outside, in the dark'],
        ]
      },
      {
        label: 'Connections',
        items: [
          ['Stairway up to Platform', '(north) — ~1m climb'],
          ['Rear door to exterior', '(south) — bulk fuel tank, gravel, dark forest'],
        ]
      }
    ],
    horror: [
      'Shift fuel drum draining impossibly fast — forced outside to bulk tank',
      'Breakers tripping on their own — or being flipped by something else',
      'Finding new items in the locker between visits',
      'Generator noise masking sounds you should hear',
      'Being in here when the car arrives unmonitored',
      'Standing outside behind the station at the fuel tank — no sightline to anything',
    ]
  }
};

/**
 * Render the sidebar zone panels into the given container.
 */
function renderZonePanels(container) {
  // Default panel
  const defaultDiv = document.createElement('div');
  defaultDiv.className = 'zone-info active';
  defaultDiv.id = 'info-default';
  defaultDiv.innerHTML = `
    <div class="zone-title">Select a Zone</div>
    <div class="zone-role">Interactive Floor Plan</div>
    <p class="default-msg">Click on any zone in the floor plan to see details about its contents, gameplay function, and horror potential.</p>
    <br>
    <p class="default-msg">Toggle sightlines to see what the player can and cannot observe from each position.</p>
  `;
  container.appendChild(defaultDiv);

  // Zone panels
  for (const [id, zone] of Object.entries(ZONES)) {
    const div = document.createElement('div');
    div.className = 'zone-info';
    div.id = 'info-' + id;

    let html = `
      <div class="zone-title">${zone.title}</div>
      <div class="zone-role">${zone.role}</div>
      <div class="zone-desc">${zone.desc}</div>
    `;

    zone.sections.forEach((section, i) => {
      const mt = i > 0 ? ' style="margin-top:20px"' : '';
      html += `<div class="items-label"${mt}>${section.label}</div>`;
      section.items.forEach(([name, detail]) => {
        if (detail) {
          html += `<div class="item"><span>${name}</span> — ${detail}</div>`;
        } else {
          html += `<div class="item"><span>${name}</span></div>`;
        }
      });
    });

    html += `<div class="horror-label">Horror Potential</div>`;
    zone.horror.forEach(h => {
      html += `<div class="horror-item">${h}</div>`;
    });

    div.innerHTML = html;
    container.appendChild(div);
  }
}

// Initialize sidebar
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('zone-panels');
  if (sidebar) renderZonePanels(sidebar);
});
