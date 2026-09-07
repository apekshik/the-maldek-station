# SPDX-License-Identifier: GPL-3.0-or-later
"""Remove the Eevee surface appearance while retaining animated spatial edges."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
import imageio_ffmpeg

p=argparse.ArgumentParser();p.add_argument('--captures',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();manifest=json.loads((a.captures/'capture.json').read_text());a.output.mkdir(parents=True,exist_ok=False)
for shot in manifest['shots']:
    shutil.copy2(a.captures/shot['image'],a.output/shot['image'])
    video=a.output/shot['video']
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(a.captures/shot['video']),
                    '-vf','format=gray,gblur=sigma=1.2,edgedetect=low=0.08:high=0.2,negate',
                    '-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(video)],check=True)
    shot['video_sha256']=hashlib.sha256(video.read_bytes()).hexdigest()
manifest['preprocessing']='Grayscale, Gaussian blur sigma 1.2, edge guide. Camera timing unchanged.'
(a.output/'capture.json').write_text(json.dumps(manifest,indent=2))
