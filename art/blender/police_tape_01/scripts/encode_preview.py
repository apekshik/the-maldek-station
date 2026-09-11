"""Convert the rendered frame sequence to an inline motion preview."""
from pathlib import Path
from PIL import Image
out=Path(__file__).resolve().parents[1]/'previews'
files=sorted((out/'motion_frames').glob('frame_*.png'))
assert len(files)==72, len(files)
frames=[]
for path in files:
    with Image.open(path) as im:
        frames.append(im.convert('RGB').resize((800,450)))
frames[0].save(out/'tape_crossing.webp',save_all=True,append_images=frames[1:],duration=83,loop=0,quality=85,method=4)
palette=frames[0].quantize(colors=192)
gif=[im.quantize(palette=palette,dither=Image.Dither.FLOYDSTEINBERG) for im in frames]
gif[0].save(out/'tape_crossing.gif',save_all=True,append_images=gif[1:],duration=[80,80,90]*24,loop=0,optimize=False)
with Image.open(out/'tape_crossing.gif') as check: assert check.n_frames==72
print(out/'tape_crossing.gif')
