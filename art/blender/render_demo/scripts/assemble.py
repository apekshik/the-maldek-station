"""Assemble real Cycles frames and source-stage captures into a silent short."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import imageio_ffmpeg, subprocess, json, shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables';OUT.mkdir(exist_ok=True)
FONT=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
SMALL=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
def encode(path,frames):
 cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
      '-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-preset','slow','-crf','18',
      '-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
 process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 count=0
 try:
  for frame in frames:process.stdin.write(frame.convert('RGB').tobytes());count+=1
 finally:process.stdin.close()
 assert process.wait()==0
 return count
def label(im,title,subtitle):
 im=im.convert('RGBA');overlay=Image.new('RGBA',im.size)
 d=ImageDraw.Draw(overlay)
 for y in range(550,720):d.line((0,y,1280,y),fill=(0,0,0,int(190*(y-550)/170)))
 d.rectangle((40,629,43,687),fill=(189,170,126,255))
 d.text((59,628),title,font=FONT,fill=(239,237,229,255))
 d.text((59,665),subtitle,font=SMALL,fill=(205,204,195,255))
 return Image.alpha_composite(im,overlay).convert('RGB')

source=ROOT/'references'/'material_preview.png'
source.parent.mkdir(exist_ok=True)
if not source.exists():
 shutil.copy2('C:/Users/APEK-A~1/AppData/Local/Temp/codex-clipboard-d6bb6e7c-e762-4298-876d-ea2093cf336c.png',source)
stages=[('html_map.png','01 / THE MAP','The Maldek Station · 2D spatial plan'),
        ('html_3d.png','02 / INTO THREE DIMENSIONS','Interactive HTML blockout'),
        (source,'03 / MATERIAL & FORM','Blender material preview')]
shots=json.loads((ROOT/'shots.json').read_text())
def movie():
 for name,title,subtitle in stages:
  image=Image.open(name if isinstance(name,Path) else ROOT/'proofs'/name).convert('RGB')
  if isinstance(name,Path):image=image.crop((50,40,image.width,image.height-20))
  elif name=='html_map.png':image=image.crop((95,275,865,710))
  elif name=='html_3d.png':image=image.crop((15,312,902,710))
  for i in range(48):
   # Slow optical-style push-in on the documentary intro captures only.
   scale=1+.025*i/47
   frame=ImageOps.fit(image,(int(1280*scale),int(720*scale)),method=Image.Resampling.LANCZOS)
   x=(frame.width-1280)//2;y=(frame.height-720)//2
   yield label(frame.crop((x,y,x+1280,y+720)),title,subtitle)
 for s in shots:
  for i in range(1,61):
   im=Image.open(ROOT/'frames'/s['name']/f'{i:04}.png').convert('RGB')
   if s['name']=='01_exterior':im=label(im,'04 / LIGHT & ATMOSPHERE','Cycles · Camera animation')
   elif s['name']=='04_forest':im=label(im,'THE MALDEK STATION','Environment concept · Work in progress')
   yield im

if __name__=='__main__':
 for s in shots:
  paths=[ROOT/'frames'/s['name']/f'{i:04}.png' for i in range(1,61)]
  assert all(p.exists() for p in paths), f"Incomplete shot: {s['name']}"
  encode(OUT/f"{s['name']}.mp4",(Image.open(p) for p in paths))
 count=encode(OUT/'maldek_map_to_mood.mp4',movie())
 (OUT/'video_info.json').write_text(json.dumps({'frames':count,'fps':24,'duration_seconds':count/24,
   'resolution':[1280,720],'codec':'H.264','audio':'silent','cycles_frames':240},indent=2))
 print('ASSEMBLED',count,'frames',count/24,'seconds')
