"""Verify remote checkout identity and hydrated R12 files against Git LFS SHA-256."""
import json,hashlib,subprocess,sys
from pathlib import Path
repo=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve()
def git(*args):return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
head=git('rev-parse','HEAD');remote=git('ls-remote','origin','refs/heads/main').split()[0]
assert head==remote,(head,remote)
assert not git('status','--porcelain'), 'Verification checkout must be clean'
files=json.loads(git('lfs','ls-files','--json'))['files'];assert all(f['checkout'] and f['downloaded'] for f in files)
checked=0;total=0
for f in files:
 if not (f['name'].startswith('art/unreal_handoff/revision12/') or f['name'].startswith('game/Content/MaldekRefinement/R12/')):continue
 h=hashlib.sha256()
 with (repo/f['name']).open('rb') as stream:
  for data in iter(lambda:stream.read(8*1024*1024),b''):h.update(data)
 assert h.hexdigest()==f['oid'],f['name']
 checked+=1;total+=f['size']
ini=(repo/'game/Config/DefaultEngine.ini').read_text()
for key in ['EditorStartupMap','GameDefaultMap']:assert key+'=/Game/MaldekRefinement/R12/Station_R12.Station_R12' in ini
result={'success':True,'verified_release_commit':head,'remote_main':remote,'checkout':str(repo),'clean':True,'all_lfs_files_hydrated':len(files),'r12_lfs_working_files_hash_verified':checked,'r12_bytes_hash_verified':total,
 'retrieval':'Independent Git clone from origin with dissociated Git objects. The already remotely verified baseline LFS cache is reused; missing migration and final LFS objects were downloaded from origin. This is not a second cold download of the baseline.',
 'checks':'Remote HEAD equality, clean checkout, hydrated LFS pointers, actual R12 working-file hashes against committed LFS OIDs, both default-map settings. Separate git lfs fsck and handoff source/FBX/texture checks also run.'}
out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
