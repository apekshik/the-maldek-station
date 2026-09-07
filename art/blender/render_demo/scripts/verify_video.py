from pathlib import Path
import hashlib,json,subprocess
import imageio_ffmpeg
from PIL import Image,ImageChops,ImageStat,ImageDraw

root=Path(__file__).resolve().parents[1]
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
report={}
for video in sorted((root/'deliverables').glob('*.mp4')):
 frames,seconds=imageio_ffmpeg.count_frames_and_secs(str(video))
 result=subprocess.run([ffmpeg,'-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
 assert result.returncode==0 and not result.stderr,result.stderr
 report[video.name]={'frames':frames,'seconds':seconds,'bytes':video.stat().st_size,'decode_ok':True}
assert report['maldek_map_to_mood.mp4']['frames']==384
sheet=Image.new('RGB',(960,1080))
for row,shot in enumerate(json.loads((root/'shots.json').read_text())):
 folder=root/'frames'/shot['name']
 a=Image.open(folder/'0001.png').convert('RGB');b=Image.open(folder/'0060.png').convert('RGB')
 assert a.size==b.size==(1280,720)
 diff=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
 assert diff>0.1,'Static or repeated endpoints'
 report[shot['name']]={'endpoint_mean_pixel_difference':diff}
 for col,im in enumerate((a,b)):sheet.paste(im.resize((480,270)),(col*480,row*270))
sheet.save(root/'deliverables'/'shot_contact_sheet.jpg',quality=93)
source=root.parent/'revision_03'/'millford_v2_night_03.blend'
report['source_unchanged']=hashlib.sha256(source.read_bytes()).hexdigest()=='6bca23a3c24feca1f52027ca7afebfc20eb8aed721b668d0a0a0f205a636f057'
assert report['source_unchanged']
(root/'deliverables'/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
