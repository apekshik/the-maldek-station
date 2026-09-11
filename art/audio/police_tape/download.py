import urllib.request,re,json,hashlib
from pathlib import Path
p=Path('art/audio/police_tape');url='https://freesound.org/people/alienistcog/sounds/125304/';page=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})).read().decode();assert 'creativecommons.org/publicdomain/zero/1.0' in page
u=next(u for u in re.findall(r'https?[^\s"<>]+?\.mp3',page) if 'hq' in u);target=p/'originals/tearing_duct_tape.mp3';urllib.request.urlretrieve(u,target);(p/'sources.json').write_text(json.dumps({'author':'alienistcog','title':'tearing-duct-tape.aif','source':url,'download':u,'license':'CC0-1.0','license_url':'https://creativecommons.org/publicdomain/zero/1.0/','sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2));print(u)
