import * as THREE from 'three';
import { OrbitControls } from './vendor/three/OrbitControls.js';

/** A measured spatial blockout, not finished game art. Y is elevation; north is -Z. */
export function initializeCompound(root, layout) {
  const host = root.querySelector('#model-canvas');
  const labelHost = root.querySelector('#model-labels');
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x0a0a0b, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  host.appendChild(renderer.domElement);
  renderer.domElement.setAttribute('aria-label', 'Orbitable station model. Use the Space menu to select rooms with the keyboard.');
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(39, 1, 0.1, 250);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.minDistance = 16;
  controls.maxDistance = 250;
  controls.maxPolarAngle = Math.PI * 0.48;
  controls.enableDamping = false;
  const upper = new THREE.Group();
  const lower = new THREE.Group();
  const exterior = new THREE.Group();
  scene.add(upper, lower, exterior);
  scene.add(new THREE.HemisphereLight(0xd5e5f0, 0x3d3827, 2.3));
  const key = new THREE.DirectionalLight(0xffe5bc, 3.1);
  key.position.set(-15, 35, 20);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0x8bbcc9, 1.7);
  fill.position.set(25, 15, -25);
  scene.add(fill);
  const grid = new THREE.GridHelper(84, 42, 0x343c34, 0x1b211e);
  grid.position.set(5, -1.7, 3);
  scene.add(grid);

  const palette = { public: 0x69734f, warm: 0x9d8155, service: 0x517f83, outside: 0x697153, prop: 0x303c39, wall: 0x9d9c83, rail: 0x94a495 };
  const roomGroups = new Map();
  const labels = [];
  const stairSets = [];
  const matt = color => new THREE.MeshStandardMaterial({ color, roughness: 0.87, metalness: 0.08 });
  function box(parent, x, y, z, w, h, d, color, outline = true) {
    const geometry = new THREE.BoxGeometry(w, h, d);
    const mesh = new THREE.Mesh(geometry, matt(color));
    mesh.position.set(x, y, z);
    parent.add(mesh);
    if (outline) {
      const lines = new THREE.LineSegments(new THREE.EdgesGeometry(geometry), new THREE.LineBasicMaterial({ color: 0xc4c7ab, transparent: true, opacity: 0.23 }));
      mesh.add(lines);
    }
    return mesh;
  }
  function line(parent, points, color = 0xa2ab8a, dashed = false) {
    const geometry = new THREE.BufferGeometry().setFromPoints(points.map(p => new THREE.Vector3(...p)));
    const material = dashed ? new THREE.LineDashedMaterial({ color, dashSize: 0.45, gapSize: 0.35 }) : new THREE.LineBasicMaterial({ color });
    const result = new THREE.Line(geometry, material);
    result.computeLineDistances();
    parent.add(result);
    return result;
  }
  function label(parent, text, x, y, z, zone) {
    const anchor = new THREE.Object3D();
    anchor.position.set(x, y, z);
    parent.add(anchor);
    const el = document.createElement(zone ? 'button' : 'span');
    el.className = 'model-label' + (zone ? '' : ' model-label-note');
    el.textContent = text;
    if (zone) el.addEventListener('click', () => select(zone));
    labelHost.appendChild(el);
    labels.push({ anchor, el, zone });
  }
  function room(id, title, parent, x, y, z, w, d, color, walls = true, doors = {}) {
    const group = new THREE.Group();
    group.userData.zone = id;
    parent.add(group);
    box(group, x, y - 0.18, z, w, 0.36, d, color);
    if (walls) {
      // Roofless cutaway walls; only the specified circulation openings are cut.
      const gap = 1.5, height = 1.2;
      function wall(axis, side, length, opening) {
        const ranges = opening === undefined ? [[-length/2,length/2]] : [[-length/2,opening-gap/2],[opening+gap/2,length/2]];
        for (const [start,end] of ranges) {
          if (end<=start) continue;
          const mid=(start+end)/2;
          if (axis==='x') box(group,x+mid,y+height/2,z+side*d/2,end-start,height,.18,color);
          else box(group,x+side*w/2,y+height/2,z+mid,.18,height,end-start,color);
        }
      }
      wall('x',-1,w,doors.north); wall('x',1,w,doors.south);
      wall('z',-1,d,doors.west); wall('z',1,d,doors.east);
    }
    group.traverse(o => { if (o.isMesh) { o.userData.zone = id; o.userData.baseColor = o.material.color.clone(); } });
    roomGroups.set(id, group);
    label(parent, title, x, y + 1.7, z, id);
    return group;
  }
  const platform = room('v2-platform', 'PLATFORM / GONDOLA', upper, -1, 4, 0, 18, 7, palette.public, false);
  const control = room('v2-control', 'CONTROL', upper, -6, 4, 7.5, 8, 8, palette.warm, true, {north:0,west:0});
  const hall = room('v2-waiting', 'WAITING HALL', upper, -14, 4, 7.5, 8, 8, palette.warm, true, {north:0,east:0,south:0});
  const overlook = room('v2-overlook', 'OVERLOOK', upper, 13.5, 4, -1, 7, 5, palette.public, false);
  const drive = room('v2-drive', 'DRIVE GALLERY', lower, 3, 0, 0, 10, 6, palette.service, true, {east:2,south:0});
  const generator = room('v2-generator', 'GENERATOR', lower, 3, 0, 6, 10, 6, palette.service, true, {north:0,east:0});
  const fuel = room('v2-fuel', 'FUEL YARD', exterior, 14, 0, 6, 8, 6, palette.outside, false);
  const relay = room('v2-relay', 'RELAY HUT', exterior, 32, 2, 0, 7, 5, palette.service, true, {north:0,south:0});
  const parking = room('v2-parking', 'PARKING', exterior, -19, -1, 21, 8, 5, palette.outside, false);

  // Upper covered connection closes the hall-platform-control loop.
  box(upper, -14, 3.82, 1.75, 8, .36, 3.5, palette.public);
  box(upper, 9, 3.82, -3, 2, .36, 1, palette.public);
  box(upper, 18, 3.82, -2.5, 2, .36, 2, palette.public);
  // Columns communicate which mass carries the upper dock.
  for (const x of [-9.7, -2, 7.7]) for (const z of [-3.2, 3.2]) box(lower, x, 1.8, z, .28, 4, .28, 0x69706a);
  // North-facing glazing and control furniture.
  box(control, -8.4, 5.45, 3.5, 2.4, 1.5, .08, 0x6e9da3);
  box(control, -6, 4.55, 4.6, 5, 1.1, .85, palette.prop);
  for (const x of [-7.4, -6.4, -5.4]) box(control, x, 5.14, 4.6, .5, .08, .4, 0xc5b278);
  box(control, -8, 4.5, 9.2, 2.4, 1, 1.1, palette.prop);
  box(hall, -16, 4.55, 5.7, 2.8, 1.1, 1.4, palette.prop);
  for (const z of [7.5, 9.5]) box(hall, -12.8, 4.4, z, 3, .8, .6, 0x766344);
  box(drive, 2, .6, -.2, 5, 1.2, 1.7, palette.prop);
  box(drive, 6.7, .7, -1.8, .65, 1.4, 1, 0x9ea58a);
  box(generator, 1.3, .65, 6, 3, 1.3, 1.7, palette.prop);
  box(generator, 6.5, .8, 7.5, 1.1, 1.6, .65, 0x718f8e);
  box(relay, 32, 2.8, -.9, 3.7, 1.6, .65, palette.prop);
  box(parking, -19, -.45, 21, 3.8, 1.1, 1.7, 0x666e66);
  const tank = new THREE.Mesh(new THREE.CylinderGeometry(.7, .7, 3.4, 20), matt(0x9b9874));
  tank.rotation.z = Math.PI / 2;
  tank.position.set(14, 1.1, 6.7);
  fuel.add(tank);
  box(fuel, 12.8, .3, 6.7, .4, .6, 1.5, palette.prop);
  box(fuel, 15.2, .3, 6.7, .4, .6, 1.5, palette.prop);

  // The car and its cable are deliberately recognizable blockout geometry.
  box(platform, 0, 5.15, -2.4, 2.5, 2.3, 2, 0x935447);
  box(platform, 0, 5.65, -3.42, 2.1, .85, .06, 0x8caeb0);
  line(upper, [[0,6.3,-2.4],[0,7.8,-2.4],[0,12,-23]], 0xb8b79a);
  line(upper, [[.5,7.8,-2.4],[.5,12,-23]], 0x7b8678);
  label(upper, '↑ TO MALDEK', 0, 12.8, -23);
  // Edge rails and viewing instrument; keep circulation openings clear.
  for (const [x1, z1, x2, z2] of [[-10,-3.5,-2,-3.5],[2,-3.5,8,-3.5],[10,-3.5,17,-3.5],[17,-3.5,17,-1.8]]) {
    line(upper, [[x1,5,z1],[x2,5,z2]], palette.rail);
    const count = Math.ceil(Math.hypot(x2-x1,z2-z1)/2);
    for (let i=0;i<=count;i++) line(upper, [[x1+(x2-x1)*i/count,4,z1+(z2-z1)*i/count],[x1+(x2-x1)*i/count,5,z1+(z2-z1)*i/count]], palette.rail);
  }
  box(overlook, 13.5, 4.65, -2, .15, 1.3, .15, palette.prop);
  box(overlook, 13.5, 5.3, -2, .6, .2, .5, 0xc0ba8b);

  function path(points, color, width = .9) {
    for (let i=1;i<points.length;i++) {
      const a = new THREE.Vector3(...points[i-1]), b = new THREE.Vector3(...points[i]);
      const segment = box(exterior, 0,0,0,width,.12,a.distanceTo(b),color);
      segment.position.copy(a.clone().add(b).multiplyScalar(.5));
      segment.lookAt(b);
    }
  }
  path([[8,0,6],[10,0,6]], 0x697c73, 1.5);
  path([[18,0,5],[19,0,5]], 0x697c73, 1.5);
  path([[18,0,8],[25,.6,10],[32,2,5],[32,2,2.5]], 0x606b4e);
  path([[32,2,-2.5],[32,3,-12],[24,4,-10],[17,4,-1]], 0x606b4e);
  path([[-14,4,11.5],[-14,1,16],[-19,-1,18.5]], 0x606b4e, 1.3);
  // Real stair flights: the internal stair occupies the east opening in the dock slab.
  function stairs(x, zStart, zEnd, yStart, yEnd, width) {
    const group = new THREE.Group(); scene.add(group);
    const count = 20;
    for (let i=0;i<count;i++) {
      const t=(i+.5)/count;
      box(group,x,yStart+(yEnd-yStart)*t-.1,zStart+(zEnd-zStart)*t,width,.2,Math.abs(zEnd-zStart)/count+.03,0x8b9381);
    }
    line(group,[[x-width/2,yStart+1,zStart],[x-width/2,yEnd+1,zEnd]],0xc0c3a2);
    line(group,[[x+width/2,yStart+1,zStart],[x+width/2,yEnd+1,zEnd]],0xc0c3a2);
    stairSets.push(group);
  }
  stairs(9,-3,3,4,0,1.8);
  stairs(19,-2.5,5,4,0,1.7);
  box(lower,8.5,-.12,2.7,1,.24,1,0x697c73);

  const guides = new THREE.Group(); scene.add(guides); guides.visible = false;
  for (const [x,z] of [[-10,-3.5],[8,-3.5],[-10,3.5],[8,3.5]]) line(guides,[[x,4,z],[x,11,z]],0x758584,true);
  let mode = 'stacked';
  let selectedZone = layout.querySelector('.room.selected')?.dataset.zone;
  function select(id) { layout.dispatchEvent(new CustomEvent('maldek:select-zone', { detail: id })); }
  const picker = root.querySelector('#model-room');
  for (const [id] of roomGroups) {
    const option = document.createElement('option'); option.value=id;
    option.textContent=layout.querySelector(`[data-zone="${id}"] .room-label`).textContent;
    picker.appendChild(option);
  }
  picker.addEventListener('change', () => { if (picker.value) select(picker.value); });
  function highlight(id) {
    selectedZone=id;
    picker.value=id || '';
    for (const [key, group] of roomGroups) group.traverse(o => {
      if (o.isMesh && o.userData.baseColor) { o.material.color.copy(o.userData.baseColor); if (key===id) o.material.color.lerp(new THREE.Color(0xebc974),.5); }
    });
    labels.forEach(l => l.el.classList.toggle('selected', Boolean(l.zone && l.zone===id)));
    render();
  }
  layout.addEventListener('maldek:zone-selected', e => highlight(e.detail));
  const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
  let down;
  renderer.domElement.addEventListener('pointerdown', e => { down={x:e.clientX,y:e.clientY}; });
  renderer.domElement.addEventListener('pointerup', e => {
    if (!down || Math.hypot(e.clientX-down.x,e.clientY-down.y)>5 || e.button!==0) return;
    const r=renderer.domElement.getBoundingClientRect();
    pointer.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);
    raycaster.setFromCamera(pointer,camera);
    const hits=raycaster.intersectObjects([...roomGroups.values()],true).filter(hit => hit.object.isMesh && visible(hit.object));
    let object=hits[0]?.object;
    while(object && !object.userData.zone) object=object.parent;
    if(object) select(object.userData.zone);
  });
  function visible(object) { for(let p=object;p;p=p.parent) if(!p.visible) return false; return true; }
  function reset() {
    controls.target.set(5,2,0);
    const distance = 112 / Math.min(camera.aspect, 1.2);
    camera.position.copy(new THREE.Vector3(50,47,64).normalize().multiplyScalar(distance).add(controls.target));
    controls.update(); render();
  }
  root.querySelector('#model-reset').addEventListener('click',reset);
  root.querySelector('#model-mode').addEventListener('change',e => {
    mode=e.target.value;
    upper.visible=mode!=='lower'; upper.position.y=mode==='exploded'?7:0;
    guides.visible=mode==='exploded'; stairSets.forEach(g=>{g.visible=mode==='stacked';});
    root.querySelector('.model-caption').textContent=mode==='exploded'?'Exploded study / upper floor lifted 7 m for visibility':mode==='lower'?'Lower service level / upper floor hidden':'Cutaway study / provisional proportions · 4 m between main floors';
    render();
  });
  const point = new THREE.Vector3();
  function render() {
    if (root.hidden || layout.hidden || !host.clientWidth || !host.clientHeight) return;
    renderer.render(scene,camera);
    const width=host.clientWidth, height=host.clientHeight;
    const placed=[];
    // Selected labels take priority when projection causes overlap.
    const ordered=[...labels].sort((a,b)=>Number(Boolean(b.zone && b.zone===selectedZone))-Number(Boolean(a.zone && a.zone===selectedZone)));
    for (const entry of ordered) {
      entry.anchor.getWorldPosition(point); point.project(camera);
      const x=(point.x*.5+.5)*width, y=(-point.y*.5+.5)*height;
      const w=entry.el.offsetWidth || 110, h=24;
      const rect={x:x-w/2,y:y-h/2,w,h};
      const collision=placed.some(p=>rect.x<p.x+p.w+3 && rect.x+rect.w+3>p.x && rect.y<p.y+p.h+3 && rect.y+rect.h+3>p.y);
      const show=visible(entry.anchor) && point.z<1 && point.z>-1 && x>0 && x<width && y>80 && y<height-65 && !collision;
      entry.el.style.visibility=show?'visible':'hidden';
      entry.el.style.left=x+'px'; entry.el.style.top=y+'px';
      if(show) placed.push(rect);
    }
  }
  let sized = false;
  function resize() {
    if(!host.clientWidth || !host.clientHeight) return;
    renderer.setSize(host.clientWidth,host.clientHeight,false);
    camera.aspect=host.clientWidth/host.clientHeight; camera.updateProjectionMatrix();
    if (!sized) { sized=true; reset(); }
    render();
  }
  new ResizeObserver(resize).observe(host);
  controls.addEventListener('change',render);
  root.addEventListener('model-visible',resize);
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();root.querySelector('.model-status').hidden=false;root.querySelector('.model-status').textContent='The 3D display was interrupted. Reload to restore it, or continue with the 2D plan.';});
  root.querySelector('.model-status').hidden=true;
  reset(); resize(); highlight(selectedZone);
}
