import urllib.request,re,json
from pathlib import Path
p=Path('art/audio/gondola_drive');rows=[]
for name,author,num in [('ElectricMotor','onursamli',846904),('WheelMechanism','Dan_AudioFile',631820),('MotorHum','felix.blume',414060)]:
 url=f'https://freesound.org/people/{author}/sounds/{num}/'
 page=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})).read().decode()
 previews=list(dict.fromkeys(re.findall(r'https?[^\s"<>]+?\.mp3',page)))
 high=[u for u in previews if 'hq' in u];u=(high or previews)[0]
 urllib.request.urlretrieve(u,p/'originals'/(name+'.mp3'))
 rows.append({'name':name,'author':author,'source':url,'preview_url':u,'license':'CC-BY-4.0' if num==631820 else 'CC0-1.0'})
(p/'downloads.json').write_text(json.dumps(rows,indent=2));print(rows)
