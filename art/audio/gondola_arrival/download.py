import urllib.request,re,json,hashlib
from pathlib import Path
p=Path('art/audio/gondola_arrival');rows=[]
for name,author,num in [('ElevatorChime','gregconquest',188011),('DoorChime','wjauch',610096),('AirBrakes','rabbydaw',504865)]:
 url=f'https://freesound.org/people/{author}/sounds/{num}/'
 page=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})).read().decode()
 assert 'creativecommons.org/publicdomain/zero/1.0' in page
 previews=list(dict.fromkeys(re.findall(r'https?[^\s"<>]+?\.mp3',page)))
 u=next(u for u in previews if 'hq' in u)
 target=p/'originals'/(name+'.mp3');urllib.request.urlretrieve(u,target)
 rows.append({'name':name,'author':author,'source':url,'download':u,'license':'CC0-1.0','license_url':'https://creativecommons.org/publicdomain/zero/1.0/','sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(p/'sources.json').write_text(json.dumps(rows,indent=2));print(rows)
