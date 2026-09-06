/** V2 spatial proposal. Kept separate from the original zone definitions. */
const ZONES_V2 = {
  'v2-control': {
    title: 'Control Room', role: '01 / Platform level · retained core',
    desc: 'The intimate, warm operating booth remains the center of Millford. Its north window faces the dock and the cable ascent. Expansion happens around it, not inside it.',
    sections: [{ label: 'Contents', items: [['Analog console', 'drive lever, gauges and status lamps'], ['Desk', 'logbook, radio and dispatch phone']] }, { label: 'Connections', items: [['North door', 'directly onto the platform'], ['West door', 'into the waiting hall'], ['Window', 'dock and cable sightline']] }],
    horror: ['The service floor and exterior path are out of sight.']
  },
  'v2-platform': {
    title: 'Platform & Gondola', role: '01 / Platform level · arrival point',
    desc: 'A covered working dock with an exposed mountain edge. The returning car sits beside the control-room window. The drive gallery occupies the level beneath this area.',
    sections: [{ label: 'Contents', items: [['Dock', 'gondola, lamps and safety markings'], ['Cable mechanism', 'above the lower drive gallery']] }, { label: 'Connections', items: [['South', 'control room'], ['West', 'covered link to waiting hall'], ['East', 'overlook and exterior stair'], ['Service stair', 'descends to the drive gallery']] }],
    horror: ['Receiving a car means leaving the booth and crossing the exposed dock.']
  },
  'v2-waiting': {
    title: 'Waiting Hall', role: '01 / Platform level · new public space',
    desc: 'The closed daytime face of the station: ticket counter, benches and old service records. A sheltered circulation loop links the hall, platform and control room.',
    sections: [{ label: 'Contents', items: [['Ticket office', 'route maps and service records'], ['Lost property', 'shelves and retained belongings']] }, { label: 'Connections', items: [['East door', 'control room'], ['North exit', 'covered link to the platform'], ['South entrance', 'forest approach from parking']] }],
    horror: ['The booth wall blocks a direct view of the dock.']
  },
  'v2-drive': {
    title: 'Drive Gallery', role: '02 / Lower service level · beneath dock',
    desc: 'A lower machinery room beneath the platform, shown offset in the 2D drawing for clarity. Local instruments provide a second place to read the equipment.',
    sections: [{ label: 'Contents', items: [['Guarded machinery', 'drive equipment and brake'], ['Local indicators', 'inspection position beside equipment']] }, { label: 'Connections', items: [['East landing', 'internal stair up to the platform'], ['South door', 'generator room']] }],
    horror: ['Concrete and machinery separate the operator from the dock above.']
  },
  'v2-generator': {
    title: 'Generator Room', role: '02 / Lower service level · power hub',
    desc: 'The original maintenance functions become a dedicated room adjoining the drive gallery. It opens onto the rear fuel yard at the lower elevation.',
    sections: [{ label: 'Contents', items: [['Generator and breakers', 'power distribution'], ['Workbench and locker', 'tools, spares and operator belongings']] }, { label: 'Connections', items: [['North door', 'drive gallery'], ['East door', 'fuel yard']] }],
    horror: ['Generator noise masks the sounds of the platform.']
  },
  'v2-fuel': {
    title: 'Fuel Yard', role: '02 / Exterior lower level · exposed work',
    desc: 'A small concrete pad with the bulk diesel tank. The service loop returns up the exterior stair, while the longer forest path reaches the relay hut.',
    sections: [{ label: 'Contents', items: [['Bulk tank', 'fuel reserve and hand pump']] }, { label: 'Connections', items: [['West', 'generator room'], ['North', 'exterior stair to platform'], ['East', 'forest route to relay hut']] }],
    horror: ['Behind and below the station, the yard has no view into the dock.']
  },
  'v2-relay': {
    title: 'Relay Hut', role: 'Exterior path · remote outbuilding',
    desc: 'A small communications hut on the sloping service path. The route continues uphill to reconnect at the overlook, rather than ending at the hut.',
    sections: [{ label: 'Contents', items: [['Analog junction equipment', 'physical line inspection']] }, { label: 'Connections', items: [['Lower path', 'fuel yard'], ['Upper path', 'overlook']] }],
    horror: ['The forest and hut enclosure remove the station from view.']
  },
  'v2-overlook': {
    title: 'Overlook', role: '01 / Mountain edge · observation',
    desc: 'An exposed railed observation deck retaining the fixed binoculars. It also becomes the upper end of the exterior route through the forest.',
    sections: [{ label: 'Contents', items: [['Mounted binoculars', 'aimed toward distant Maldek']] }, { label: 'Connections', items: [['West', 'platform'], ['East', 'descending forest path to relay hut']] }],
    horror: ['Looking toward Maldek trades awareness of the space behind you.']
  },
  'v2-parking': {
    title: 'Parking & Arrival', role: 'Forest approach · beginning and end',
    desc: 'The parked car and forest approach anchor the compound to the outside world. The path climbs to the waiting-hall entrance.',
    sections: [{ label: 'Connections', items: [['Uphill path', 'waiting hall entrance']] }],
    horror: ['The station emerges from the forest on arrival.']
  }
};

document.addEventListener('DOMContentLoaded', () => {
  renderZonePanels(document.getElementById('zone-panels-v2'), ZONES_V2, 'v2-');
  const intro = document.getElementById('info-v2-default');
  intro.innerHTML = `<div class="zone-title">An expanded Millford</div>
    <div class="zone-role">V2 / Spatial proposal</div>
    <p class="zone-desc">A familiar control booth inside a larger working compound. Select a space to inspect its contents and connections.</p>
    <div class="items-label">Two levels, three routes</div>
    <div class="item"><span>Sheltered loop</span><br>Control → hall → platform → control</div>
    <div class="item"><span>Service loop</span><br>Platform → drive → generator → yard → exterior stair → platform</div>
    <div class="item"><span>Forest loop</span><br>Yard → relay hut → overlook → platform</div>
    <p class="zone-desc" style="margin-top:24px">The 2D plan separates the levels for legibility. The 3D study stacks the drive beneath the dock. Dimensions and mechanics remain provisional.</p>`;
});
