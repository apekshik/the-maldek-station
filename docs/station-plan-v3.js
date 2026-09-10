/** Current planning proposal. Metre-scaled lodge; retained assets require a Blender survey. */
(() => {
  const panel = document.getElementById('plan-v3');
  const zones = {
    lodge: ['Passenger lodge / approved program', '14 × 11.2 m hall + 5 × 5 m coffee annex + 6 × 6 m restroom wing: 217.8 m² gross. Six tables, twelve benches and twelve lockers. Its north exit meets the west apron; the entrance court faces the relocated public stair. The east wall is solid. Exact site position remains proposed.'],
    apron: ['Expanded public platform / proposed', 'Extend the platform west along the lodge frontage. Reserve a 3 m clear covered strip between lodge and boarding area, with a 3 × 3 m landing at the lodge exit. Rebuild its outer support line and guardrails. Keep the dock, cable mechanism and gondola arrival alignment fixed until a survey proves relocation necessary.'],
    control: ['Central control / retain anchor', 'Keep the current booth, keypad entrance and dock sightline. The 6 × 5 m rectangle is a planning envelope, not a measured replacement. No lodge connection. A separate exterior path reaches the existing entrance; its final orientation follows the surveyed door. Retain the quarters above and their independent access.'],
    stairs: ['Public arrival stair / relocate', 'Move the upper landing toward the lodge entrance court. Reserve a 4 × 6 m switchback stair envelope with 1.8 m clear flights and at least 1.8 m landings. For the nominal 4 m rise, study 24 risers of about 167 mm in two flights; verify the actual terrain rise, tread count, headroom and capsule movement in Blender. Join the existing approach at a surveyed lower tie-in.'],
    bypass: ['Exterior bypass / add', 'A 2 m clear public path runs around the lodge’s east side and reaches the apron without going through the lodge. It keeps control reachable when the lodge is closed. Preserve guardrails, runoff and clear corners; do not turn it into a shortcut through staff prep.'],
    service: ['Service stair and lower yard / retain destinations', 'Reserve the eastern stair corridor separately from the public stair. Rework its top landing only where the platform edge changes; keep the drive gallery under the dock and the generator, workshop and fuel yard connected below. Lower-level locations in the inset show connectivity, not scale or relocation.'],
    routes: ['Wider map / retain connections', 'Parking and the forest approach feed the new stair tie-in. The relay destination, overlook, bridge and water terrace stay on the exterior network. Reconnect their nearest path segments where the new apron meets the old station. No remote building relocation is proposed.']
  };
  const room = (id, shape, x, y, title) => `<g class="room" data-zone="v3-${id}" id="zone-v3-${id}">${shape}<text x="${x}" y="${y}" class="room-label" id="label-v3-${id}">${title}</text></g>`;
  panel.innerHTML = `<div class="plan-container">
    <svg class="floorplan floorplan-v2" viewBox="0 0 1080 900" xmlns="http://www.w3.org/2000/svg" aria-label="Current proposed station expansion around the approved six-table lodge">
    <defs><pattern id="grid-v3" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#30332b" stroke-width=".5"/></pattern></defs>
    <rect width="1080" height="900" fill="url(#grid-v3)"/>
    <text x="40" y="30" class="map-kicker">MILLFORD / STATION EXPANSION 03</text>
    <text x="40" y="51" class="map-note">Lodge program approved · station placement proposed · local plan axes, not Unreal axes</text>
    <path d="M570 65V145" stroke="#a7b8b0" stroke-width="3"/><text x="590" y="85" class="map-note">CABLE / MOUNTAIN ↑</text>
    ${room('apron','<path d="M70 130H740V260H70Z" fill="#303929" stroke="#a7ac7b" stroke-width="2"/>',95,180,'EXPANDED WEST APRON')}
    <rect x="540" y="130" width="60" height="64" fill="#172421" stroke="#c8b784" stroke-width="2"/><text x="549" y="153" class="map-note">DOCK</text><text x="610" y="165" class="map-note">RETAIN ANCHOR</text>
    <path d="M100 224H380" stroke="#b3a77f" stroke-dasharray="6 4"/><text x="105" y="246" class="map-note">3 m covered frontage / clear of boarding</text>
    <path d="M70 260H100V604H380V260H460V650H70Z" fill="#262c23" stroke="#6c765c"/>
    ${room('lodge','<path d="M100 260H380V604H260V484H200V584H100Z" fill="#473923" stroke="#d0ad75" stroke-width="2"/>',115,456,'PASSENGER LODGE')}
    <text x="115" y="475" class="map-note">14 × 11.2 m hall · six tables</text>
    <path d="M100 484H200M260 484H380M260 524H380M320 524V604" stroke="#b39a70" fill="none"/>
    <text x="111" y="535" class="map-note">COFFEE</text><text x="111" y="551" class="map-note">5 × 5 m</text><text x="274" y="503" class="map-note">WC HALL</text><text x="275" y="558" class="map-note">W</text><text x="341" y="558" class="map-note">M</text>
    <path d="M228 260H252M228 484H252" stroke="#1a211a" stroke-width="5"/>
    ${[[180,282],[300,282],[180,346],[300,346],[180,410],[300,410]].map(([x,y])=>`<rect x="${x}" y="${y}" width="36" height="16" fill="#8c704a" stroke="#baa077"/><rect x="${x}" y="${y-11}" width="36" height="7" fill="#806a49"/><rect x="${x}" y="${y+20}" width="36" height="7" fill="#806a49"/>`).join('')}
    ${room('control','<rect x="480" y="260" width="120" height="100" fill="#423829" stroke="#a79673" stroke-width="2"/>',490,287,'CONTROL')}
    <text x="490" y="309" class="map-note">Keypad / retained</text><text x="490" y="329" class="map-note">Envelope: 6 × 5 m*</text>
    <rect x="488" y="268" width="104" height="84" fill="none" stroke="#bab7a1" stroke-dasharray="3 5"/><text x="485" y="386" class="map-note">Quarters above +7.65 m*</text>
    <path d="M240 267V207H515V250" class="sightline" stroke="#c4ba82"/><text x="355" y="120" class="map-note">PUBLIC LEVEL +4 m</text>
    ${room('bypass','<rect x="400" y="260" width="40" height="365" fill="#324138" stroke="#83a48d"/>',399,425,'BYPASS')}
    <text x="403" y="443" class="map-note">2 m</text>
    <path d="M240 650H420V235H510" fill="none" stroke="#92b59b" stroke-width="3" stroke-dasharray="7 5"/>
    <path d="M240 665V497M240 470V280" fill="none" stroke="#d7b984" stroke-width="3" stroke-dasharray="7 5"/>
    <rect x="200" y="650" width="80" height="25" fill="#34382a" stroke="#a99a75"/>
    ${room('stairs','<rect x="200" y="675" width="80" height="120" fill="#453d2c" stroke="#d7b984" stroke-width="2"/>',295,720,'NEW PUBLIC STAIR')}
    ${Array.from({length:11},(_,i)=>`<path d="M204 ${702+i*8}H235M245 ${702+i*8}H276" stroke="#bda878"/>`).join('')}
    <text x="295" y="741" class="map-note">4 × 6 m reservation</text><text x="295" y="762" class="map-note">2 flights / nominal 4 m rise</text><text x="295" y="783" class="map-note">Upper landing → arrival court</text>
    <path d="M200 805L150 840H55" stroke="#a99a75" stroke-width="8" fill="none"/><text x="45" y="871" class="map-note">TO EXISTING FOREST APPROACH / PARKING</text>
    <rect x="635" y="260" width="80" height="15" fill="#243638" stroke="#7a9b9d"/>
    ${room('service','<rect x="635" y="275" width="80" height="120" fill="#243638" stroke="#7a9b9d"/>',625,425,'SERVICE STAIR')}
    ${Array.from({length:10},(_,i)=>`<path d="M640 ${295+i*9}H710" stroke="#789496"/>`).join('')}
    <text x="618" y="449" class="map-note">Separate from public arrival</text>
    ${room('routes','<path d="M750 130H1010V400H750Z" fill="#1c241f" stroke="#64795f" stroke-dasharray="5 5"/>',775,166,'EXTERIOR NETWORK')}
    <text x="775" y="197" class="map-note">Overlook → relay path</text><text x="775" y="223" class="map-note">Bridge / water terrace</text><text x="775" y="249" class="map-note">Keep destinations and landings</text><text x="775" y="280" class="map-note">Reconnect at eastern apron</text><text x="775" y="310" class="map-note">Route diagram, not site scale</text>
    <path d="M720 220H765" stroke="#7c9d80" stroke-width="3"/>
    <rect x="520" y="510" width="510" height="220" fill="#172124" stroke="#668589"/>
    <text x="540" y="540" class="map-kicker">LOWER SERVICE LEVEL / 0 m / CONNECTIVITY INSET</text>
    <text x="540" y="577" class="map-note">Drive gallery remains beneath dock</text><text x="540" y="610" class="map-note">Gallery ↔ workshop ↔ generator ↔ fuel yard</text><text x="540" y="643" class="map-note">Eastern service stair ↔ upper platform</text><text x="540" y="680" class="map-note">Lodge extension requires its own supports;</text><text x="540" y="702" class="map-note">do not fill machinery clearance with foundations.</text>
    <text x="545" y="775" class="map-note">*Retained building envelopes need a current mesh survey.</text><text x="545" y="798" class="map-note">New west deck edge and stairs are proposals, not surveyed deltas.</text>
    <path d="M790 840H990M790 834V846M890 834V846M990 834V846" stroke="#b7a57a"/><text x="790" y="866" class="map-note">0</text><text x="878" y="866" class="map-note">5 m</text><text x="968" y="866" class="map-note">10 m</text>
    </svg><div class="legend">Gold: lodge / arrival · Green: exterior bypass · Blue: service</div><button class="toggle-sightlines" aria-pressed="false">Show Sightlines</button><div class="zoom-indicator"></div></div>
    <div class="resize-handle"></div><aside class="sidebar" aria-live="polite"><div class="zone-info active" id="info-v3-default"><div class="zone-title">A larger public station</div><p class="zone-desc">The lodge is approved. This station arrangement is the next proposal: expand west and toward arrival, retain the dock/control anchors, and relocate the public stair.</p><p class="zone-desc">Select a space for its dimensions and connections. Scroll to zoom; drag to pan.</p><p><a href="passenger-cabin.html">Approved lodge interior →</a></p><p><a href="design/station-expansion.md">Placement and build sequence →</a></p></div>${Object.entries(zones).map(([id,[title,body]])=>`<div class="zone-info" id="info-v3-${id}"><div class="zone-title">${title}</div><p class="zone-desc">${body}</p><p><a href="design/station-expansion.md">Full station brief →</a></p></div>`).join('')}</aside>`;
})();
