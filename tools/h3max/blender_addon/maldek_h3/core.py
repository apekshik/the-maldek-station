# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure-Python art direction shared by the panel and isolated worker."""
import json
from pathlib import Path

FIELDS=('fog','darkness','warmth','wetness','realism','direction','mode','distance','guide','resolution','seed','frame_start','frame_end')

def prompt(s):
    fog=('Clear air, no fog.','Light atmospheric haze.','Visible drifting valley mist.','Dense fog obscures the cliff and distant forest.','Very thick layered fog conceals most lower structures and distant details.')[min(4,int(s['fog']*4.99))]
    dark=('Daylight with readable surfaces.','Overcast dusk.','Dark blue hour.','Low-exposure night; most surfaces remain shadowed.','Very dark night; reveal only fragments in small pools of practical light.')[min(4,int(s['darkness']*4.99))]
    wet=('Dry weathered surfaces.','Slightly damp surfaces.','Patchy wet surfaces with broken reflections.','Rain-wet decking, damp concrete and occasional puddles.','Heavy rain, water-darkened surfaces and restrained puddle reflections.')[min(4,int(s['wetness']*4.99))]
    warmth='Predominantly cool practical lighting.' if s['warmth']<.35 else ('Warm tungsten pools against cool ambient shadows.' if s['warmth']<.75 else 'Warm amber practical lighting, cool unlit surroundings.')
    realism=('Preserve small construction details as closely as possible while improving physical material response.' if s['realism']=='FAITHFUL' else 'Reinterpret simple surfaces as photographed reality: natural fractured rock, moss, weathered concrete, painted steel, layered glass and irregular foliage. Small construction details may be refined, but preserve the major design and openings.')
    motion={'STILL':'Hold this exact viewpoint; only rain and mist move subtly.','PAN':'Follow the guide camera slide exactly, without adding another movement.','DOLLY':'Follow the guide camera approach exactly, without an extra zoom.','ANIMATION':'Follow the reference camera trajectory, timing and parallax.'}[s['mode']]
    reference='Image 1' if s['mode']=='STILL' else 'Video 1'
    return (f'{reference} is a spatial and camera guide ONLY, never the desired rendering style. '
        'Create a live-action cinematic shot of this industrial mountain cable-car station. Preserve its main layout, '
        'two levels, red gondola, roof footprints, openings, supports and stairs. '
        'Replace CG shading, faceting, plastic surfaces and repeated foliage with believable physical materials. '
        'No linework, sketch marks, viewport shading, text, morphing, construction animation or before-after reveal. '
        'The finished photographic look is present from frame one. Keep buildings rigid and stationary. '
        +realism+' '+fog+' '+dark+' '+wet+' '+warmth+' '+motion+' '+s['direction'])

def save(path,data):
    path=Path(path);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2),encoding='utf-8');tmp.replace(path)

def values(properties):
    return {key:getattr(properties,key) for key in FIELDS}
