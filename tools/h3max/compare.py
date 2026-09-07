# SPDX-License-Identifier: GPL-3.0-or-later
"""Make a silent, side-by-side Eevee/H3 review without stretching either image."""
import argparse,json,subprocess
from pathlib import Path
import imageio_ffmpeg

p=argparse.ArgumentParser();p.add_argument('--guide',type=Path,required=True);p.add_argument('--job',type=Path,required=True)
args=p.parse_args();ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
generated=args.job/'video.mp4'
count,seconds=imageio_ffmpeg.count_frames_and_secs(str(generated))
assert count>=120,'Incomplete generated video'
subprocess.run([ffmpeg,'-y','-v','error','-i',str(generated),'-t','5','-an','-c:v','copy','-movflags','+faststart',str(args.job/'h3_review.mp4')],check=True)
panel='scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,setpts=PTS-STARTPTS'
subprocess.run([ffmpeg,'-y','-v','error','-i',str(args.guide),'-i',str(generated),'-filter_complex',
                f'[0:v]{panel}[a];[1:v]{panel}[b];[a][b]hstack=inputs=2[v]',
                '-map','[v]','-t','5','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(args.job/'eevee_vs_h3.mp4')],check=True)
subprocess.run([ffmpeg,'-y','-v','error','-i',str(generated),'-vf','fps=1,scale=480:-1,tile=3x2','-frames:v','1',str(args.job/'contact.jpg')],check=True)
report={'generated_frames':count,'video_seconds':seconds,'comparison':'Left: Eevee motion guide. Right: H3 Max. Silent, five seconds; aspect ratios preserved.'}
(args.job/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
