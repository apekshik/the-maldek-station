import urllib.request,re,json,hashlib,concurrent.futures
from pathlib import Path
b=Path('art/audio/lodge_refine_01')
rows=[('wind','Kinoton',815100),('drawer','maaaks',521214),('wooddrawer','FOSSarts',740297),('cupboard','wlabarron',509108),('locker','kyles',450785),('fridge','sethlind',265024),('tile','IENBA',834027),('concrete','florianreichelt',459964),('room','launemax',250024),('fridge_alt','SpliceSound',218334)]
def get(r):
 name,author,i=r;url=f'https://freesound.org/people/{author}/sounds/{i}/';page=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read().decode();licenses=sorted(set(re.findall(r'https?://creativecommons.org/(?:licenses|publicdomain)/[^"<> ]+',page)));assert licenses
 u=next(u for u in re.findall(r'https?[^\s"<>]+?\.mp3',page) if 'hq' in u);p=b/'originals'/(name+'.mp3');
 if not p.exists():urllib.request.urlretrieve(u,p)
 return {'name':name,'author':author,'id':i,'page':url,'download':u,'licenses':licenses,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 results=[]
 for f in pool.map(get,rows):results.append(f);print(f)
(b/'sources.json').write_text(json.dumps(results,indent=2))
