import bpy,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
blend_hash=hashlib.sha256((OUT/'Maldek_Passenger_Lodge_Seating.blend').read_bytes()).hexdigest();results=[]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Maldek_Passenger_Lodge_Seating.blend'))
s=bpy.context.scene;ref=bpy.data.collections['REFERENCE_ONLY_Source_Context_DO_NOT_EXPORT'];kit=bpy.data.collections['PLS_Seating_Kit'];views=json.loads((OUT/'views.json').read_text())
for name,pos,target,ortho,mode in views:
 ref.hide_render=mode in ['isolated','human']
 for o in kit.objects:
  if o.type=='MESH':o.hide_render=mode in ['isolated','human'] and o.parent.name!='PLS_Group_03'
 for o in s.objects:
  if o.name.startswith('REVIEW_Human'):o.hide_render=mode!='human'
 s.camera=bpy.data.objects['REVIEW_'+name];s.render.filepath=str(OUT/'previews'/f'{name}.png')
 bpy.ops.render.render(write_still=True)
 results.append(dict(image=name+'.png',sha256=hashlib.sha256((OUT/'previews'/f'{name}.png').read_bytes()).hexdigest(),camera_position=pos,target=target,mode=mode,temporary_neutral_review_lights=True,roof_hidden=True))
assert hashlib.sha256((OUT/'Maldek_Passenger_Lodge_Seating.blend').read_bytes()).hexdigest()==blend_hash
(OUT/'render_report.json').write_text(json.dumps(dict(blend_sha256=blend_hash,engine=s.render.engine,samples=s.cycles.samples,resolution=[s.render.resolution_x,s.render.resolution_y],renders=results),indent=2))
print('SIX REVIEW RENDERS COMPLETE')
