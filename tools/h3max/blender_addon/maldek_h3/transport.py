# SPDX-License-Identifier: GPL-3.0-or-later
"""Station-specific H3 Max job preparation and one-shot submission.

Uses the reference-image workflow documented by gokayfem/H3-Max-Blender.
Only `generate` sends data. Interrupted/uncertain jobs are never resubmitted.
"""
import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
ENDPOINT='https://fal.run/minimax/h3-max/reference-to-video'
RULES=('Image 1 is the authoritative geometry and camera reference. Preserve the station footprint, '
       'two-level arrangement, gondola proportions and position, door and window openings, railings, '
       'stairs, structural supports, cliff and paths. Image 2 provides ONLY the established mood, '
       'palette, lighting and material character; do not copy a different viewpoint or layout from it. '
       'Render one coherent full-frame view, not a collage. Finish the scene from the first frame: '
       'no gray-to-color transition, construction animation, dissolve or morph. Keep architecture rigid '
       'and stationary. Fine rain and gently drifting mist may move naturally. ')

def read_config(path):
    path=Path(path).resolve(); data=json.loads(path.read_text(encoding='utf-8'))
    if data['resolution'] not in ('480P','768P') or data['duration']!=5:
        raise ValueError('This pilot supports five-second 480P or 768P clips')
    ids=[s['id'] for s in data['shots']]
    if len(ids)!=len(set(ids)) or any(not i.replace('_','').isalnum() for i in ids):
        raise ValueError('Shot IDs must be unique alphanumeric names')
    return path,data

def uri(path):
    data=Path(path).read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'): mime='image/png'
    elif data.startswith(b'\xff\xd8'): mime='image/jpeg'
    elif len(data)>12 and data[4:8]==b'ftyp': mime='video/mp4'
    else: raise ValueError('Reference must be a PNG, JPEG or MP4')
    return 'data:'+mime+';base64,'+base64.b64encode(data).decode('ascii')

def prepare(config_path,capture_path,shot_id):
    path,config=read_config(config_path)
    shot=next((s for s in config['shots'] if s['id']==shot_id),None)
    if shot is None: raise ValueError('Unknown shot')
    captures=Path(capture_path).resolve()
    manifest=json.loads((captures/'capture.json').read_text())
    source=(path.parent/config['source_blend']).resolve()
    if source!=Path(manifest['source']).resolve() or hashlib.sha256(source.read_bytes()).hexdigest()!=manifest['source_sha256']:
        raise ValueError('Capture belongs to a different or changed Blender source; capture the configured scene again')
    item=next(i for i in manifest['shots'] if i['id']==shot_id)
    geometry=captures/item['image'];style=(path.parent/shot['style_image']).resolve()
    if hashlib.sha256(geometry.read_bytes()).hexdigest()!=item['sha256']:
        raise ValueError('Capture changed after manifest creation')
    prompt=RULES+config['mood']+' CAMERA MOTION: '+shot['motion']
    payload=dict(prompt=prompt,duration=config['duration'],resolution=config['resolution'],
                 aspect_ratio='16:9',seed=config['seed'],prompt_expansion_mode='balanced',
                 enable_safety_checker=True,sync_mode=False,reference_image_urls=[uri(geometry),uri(style)])
    video=captures/item['video']
    if hashlib.sha256(video.read_bytes()).hexdigest()!=item['video_sha256']:
        raise ValueError('Motion capture changed after manifest creation')
    payload['reference_video_urls']=[uri(video)]
    payload['prompt']+=' Video 1 is the authoritative five-second camera-motion and geometry guide. Follow its framing, camera trajectory, timing, parallax and stationary architectural layout throughout. Replace its flat daylight look with the Image 2 night treatment from the very first frame. Do not show a transition from the guide into the finished look. Do not invent a different camera move.'
    if config.get('conditioning')=='motion_only':
        payload.pop('reference_image_urls')
        payload['prompt']=(
            'Create a live-action cinematic location shot of a real industrial cable-car station. '
            'Video 1 is an unfinished computer-generated previs used ONLY for camera choreography and spatial layout. '
            'Match its camera position, slow travel direction, perspective, timing and parallax. Preserve the two-level '
            'station arrangement, cliffside position, red cable-car cabin, roof footprints, openings, supports and stairs. '
            'Completely replace the visual rendering of the previs with convincing photographed reality. '
            'Do not reproduce its viewport shading, flat surfaces, simple polygonal terrain, plastic glazing, '
            'uniform colors, faceted mannequins, repeated tree shapes or synthetic illumination. '
            'Interpret blockout geometry as full-scale real construction: rough fractured stratified rock with moss '
            'and crevices, physically detailed concrete with water-darkened pores and runoff, painted steel with '
            'subtle oxidation at joints, rounded manufactured cabin sheet metal, layered window glass with reflections '
            'and visible interior depth. Replace scale mannequins with stationary distant people in ordinary workwear. '
            'Natural irregular pines, fine branches, atmospheric depth and believable ground contact. '
            'All of these photographic details are present from frame one; no building-up, morph, before-after '
            'transition, style reveal or camera reframe. Architecture stays rigid and stationary. '
            +config['mood']+' CAMERA: '+shot['motion']+
            ' The final result should be indistinguishable from a carefully photographed real location, '
            'with subtle lens response and natural material variation, never a video-game screenshot or architectural viewport.')
        payload['prompt_expansion_mode']='quality'
        if manifest.get('preprocessing'):
            payload['prompt']='Video 1 is an abstract moving architectural line drawing, not a visual style reference. Use only its perspective, scene arrangement and camera motion. Produce a full-color LIVE-ACTION photographic shot, with no outlines, sketch marks, monochrome effect or drawing-to-real transition. '+payload['prompt']
    summary=dict(endpoint=ENDPOINT,shot=shot_id,requests=1,prompt=payload['prompt'],resolution=config['resolution'],
                 duration=config['duration'],seed=config['seed'],source_sha256=manifest['source_sha256'],
                 references=[dict(role=role,path=str(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest())
                             for role,file in [('geometry',geometry),('mood',style)]])
    summary['references'].append(dict(role='camera_motion',path=str(video),sha256=item['video_sha256']))
    if config.get('conditioning')=='motion_only':
        summary['references']=summary['references'][-1:]
    summary['conditioning']=config.get('conditioning','images_and_video')
    return payload,summary

def load_key(path):
    key=os.environ.get('FAL_KEY','').strip()
    if not key and Path(path).is_file():
        for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
            name,sep,value=line.partition('=')
            if sep and name.strip()=='FAL_KEY':key=value.strip().strip('\"\'')
    if not key:raise ValueError('Fill FAL_KEY in tools/h3max/.env.local; do not paste it into chat')
    return key

def save(path,data):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data,indent=2),encoding='utf-8');temporary.replace(path)

def download(job):
    job=Path(job);result=json.loads((job/'result.json').read_text())
    url=result.get('video',{}).get('url','')
    if not url.startswith('https://'):raise ValueError('Provider returned no HTTPS video')
    destination=job/'video.mp4'
    with urllib.request.urlopen(url,timeout=120) as response, (job/'video.part').open('wb') as out:
        while chunk:=response.read(1024*1024):out.write(chunk)
    (job/'video.part').replace(destination)
    state=json.loads((job/'job.json').read_text());state['status']='downloaded';state['video']=str(destination)
    save(job/'job.json',state)
    return destination

def generate(payload,summary,key,job):
    job=Path(job)
    job.mkdir(parents=True,exist_ok=False) # Prevent accidental repeat POSTs for the same job.
    record=dict(summary,status='submitting',started_at=time.time())
    save(job/'job.json',record)
    request=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),
        headers={'Authorization':'Key '+key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=600) as response:
            result=json.load(response);record['request_id']=response.headers.get('x-fal-request-id')
        save(job/'result.json',result)
        record.update(status='generated',api_seconds=time.time()-record['started_at'])
        save(job/'job.json',record)
    except Exception as error:
        record.update(status='uncertain_check_fal_dashboard',error_type=type(error).__name__)
        save(job/'job.json',record)
        raise RuntimeError('Request failed or completion is uncertain. Check fal dashboard; no automatic retry.') from None
    try:return download(job)
    except Exception:
        raise RuntimeError('Generation response saved; download failed. Use download --job to recover without another generation.') from None

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['capture','plan','generate','download'])
    parser.add_argument('--config',type=Path,default=HERE/'maldek.json')
    parser.add_argument('--captures',type=Path,default=HERE/'../../art/blender/h3max/outputs/refined-exterior-eevee-01')
    parser.add_argument('--shot',default='exterior')
    parser.add_argument('--job',type=Path)
    parser.add_argument('--env',type=Path,default=HERE/'.env.local')
    parser.add_argument('--blender',default='C:/Program Files/Blender Foundation/Blender 5.0/blender.exe')
    args=parser.parse_args()
    if args.command=='download':
        if not args.job:parser.error('download needs --job')
        print(download(args.job));return
    if args.command=='capture':
        import imageio_ffmpeg
        path,config=read_config(args.config)
        args.captures.resolve().mkdir(parents=True,exist_ok=False)
        command=[args.blender,'--background',str((path.parent/config['source_blend']).resolve()),
                 '--python-exit-code','1','--python',str(HERE/'capture.py'),'--','--config',str(path),
                 '--output',str(args.captures.resolve()),'--shot',args.shot,'--ffmpeg',imageio_ffmpeg.get_ffmpeg_exe()]
        subprocess.run(command,check=True);return
    payload,summary=prepare(args.config,args.captures,args.shot)
    if args.command=='plan':
        print(json.dumps(summary,indent=2));return
    if not args.job:parser.error('generate needs a new --job directory')
    print(generate(payload,summary,load_key(args.env),args.job))

if __name__=='__main__':
    try:main()
    except Exception as error:
        # Avoid exposing keys, HTTP request bodies, or arbitrary server responses.
        if isinstance(error,(ValueError,RuntimeError,FileExistsError)):
            print(str(error) if not isinstance(error,FileExistsError) else 'Output already exists; no request sent.',file=sys.stderr)
        else:print(type(error).__name__+': pipeline stopped; inspect local files.',file=sys.stderr)
        sys.exit(1)
