"""Build a portable review index; all pictures are direct Blender renders."""
from pathlib import Path
import html,json
OUT=Path(__file__).resolve().parents[1]
def figure(name,caption):
    return f'<figure><a href="previews/{name}.png"><img loading="lazy" src="previews/{name}.png" alt="{html.escape(caption)}"></a><figcaption>{html.escape(caption)}</figcaption></figure>'
parts=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PLW 01 — Passenger lodge windows</title><style>
body{margin:0;background:#ebeee9;color:#172d2c;font:16px/1.5 system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:38px}h1{font-size:38px;line-height:1.1;margin:12px 0}h2{margin-top:40px}.eyebrow{font-weight:700;letter-spacing:.16em;color:#506c67}.intro{max-width:850px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.corners{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}figure{margin:0;background:white;border:1px solid #c5cfca}img{display:block;width:100%;height:auto}figcaption{padding:12px;font-size:14px}a{color:#1b625f}table{border-collapse:collapse;width:100%;background:#fff}td,th{padding:10px 14px;border-bottom:1px solid #d2dad5;text-align:left}.note{background:#dae3dc;padding:16px 22px}.links a{margin-right:20px}@media(max-width:800px){main{padding:18px}.grid,.corners{grid-template-columns:1fr}h1{font-size:28px}}</style><main>
<div class="eyebrow">MALDEK STATION / PLW 01</div><h1>Passenger lodge windows</h1><p class="intro">Two three-bay fixed windows, fitted to the approved north facade. Hollow metal profiles, frosted insulated glazing, gasketed beads, sloping pans and separate reveals. All images below are direct renders of the saved Blender review copy.</p>
<p class="links"><a href="README.md">Assembly handoff</a><a href="replacement_manifest.json">Replacement manifest</a><a href="verification.json">Geometry checks</a><a href="references/README.md">Construction references</a></p>
<div class="note">Rough openings: 3800 × 1700 mm. Core depth: 180 mm. Sill: 900 mm above finished floor. Public exit: 1200 mm retained. No master wall patch required.</div>
<h2>Facade beside control</h2><p>Identical camera and source lighting. Original control-room window assets remain unchanged.</p><div class="grid">''']
parts.extend([figure('PLW_Facade_Before','Before — original solid frosted proxies'),figure('PLW_Facade_Beside_Control','After — PLW assemblies fitted beside the existing control building'),'</div><h2>Player-height fitted views</h2><p>Camera elevation 1.65 m above the lodge floor. Roof retained; temporary neutral review softboxes.</p><div class="grid">'])
for i in [1,2]:
    for side in ['Exterior','Interior']:parts.append(figure(f'PLW_{i:02}_{side}',f'Window {i:02} / {side.lower()}'))
parts.append('</div><h2>Construction details</h2><div class="grid">')
parts.extend([figure('PLW_Sill_Detail','Sill — machined drainage slots discharge over the sloping galvanized pan'),figure('PLW_Head_Detail','Head — painted profile, gasket, enamel reveal and galvanized drip hood'),'</div><h2>Corner ownership review</h2><p>All four corners of both assemblies, viewed from both sides. Click any image for full resolution.</p><div class="corners">'])
for i in [1,2]:
    for side in ['West','East']:
        for level in ['Sill','Head']:
            for face in ['Exterior','Interior']:parts.append(figure(f'PLW_{i:02}_{side}_{level}_{face}',f'{i:02} / {side} {level.lower()} / {face.lower()}'))
parts.append('</div><h2>Assembly dimensions</h2><table><tr><th>Component</th><th>Authored dimensions</th></tr>')
for k,v in [('Opening','3800 × 1700 mm'),('Frame','3760 × 1630 × 110 mm; 3 mm section wall'),('Faces','70 mm perimeter / 60 mm mullions'),('Each pane','1158.67 × 1482 × 6 mm; 12 mm sealed cavity'),('Reveal','2 mm metal; 4 mm concealed core clearance'),('Sill','30 mm outward fall over 316 mm; 5.42°'),('Overall envelope','3882 × 1769 × 321 mm')]:parts.append(f'<tr><td>{k}</td><td>{v}</td></tr>')
parts.append('</table><p>Verification covers saved Blender geometry, not engine collision or rated structural/weather performance. Manufacturer reference applications and remaining integration work are documented in the handoff.</p></main></html>')
(OUT/'review.html').write_text('\n'.join(parts),encoding='utf-8')
expected=['PLW_Facade_Before','PLW_Facade_Beside_Control','PLW_01_Exterior','PLW_01_Interior','PLW_02_Exterior','PLW_02_Interior','PLW_Sill_Detail','PLW_Head_Detail']+[f'PLW_{i:02}_{side}_{level}_{face}' for i in [1,2] for side in ['West','East'] for level in ['Sill','Head'] for face in ['Exterior','Interior']]
missing=[n for n in expected if not (OUT/'previews'/f'{n}.png').exists()]
print('Gallery written; expected images:',len(expected),'missing:',missing)
